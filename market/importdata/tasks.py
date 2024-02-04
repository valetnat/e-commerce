import os
import json
import time
from typing import List, Dict, Optional, Tuple, Union

from django.core.mail import EmailMessage
from django.conf import settings
from django.core.cache import cache
from django.db import transaction, DatabaseError, IntegrityError
from config.celery import app
from celery.utils.log import get_task_logger
from pydantic import ValidationError
from json.decoder import JSONDecodeError

from products.models import Product, ProductDetail, Detail, Manufacturer, Category, Tag
from shops.models import Offer, Shop
from importdata.services import ProductBaseModel, DetailsBaseModel


logger = get_task_logger(__name__)


# noqa: C901
@app.task(ignore_result=True, name="importdata.tasks.load_files")
def load_files(files: Tuple[Optional[str]], email_to: Optional[str]) -> None:  # noqa: C901
    """
    Задача Сelery. Импорт файлов.
    """
    file_total: int = 0
    failed_file: int = 0
    successed_file: int = 0
    total_product: int = 0
    total_loaded_product: int = 0
    total_failed_product: int = 0
    formats: List[str] = ["json"]
    folder: str = settings.IMPORT_FOLDER
    excp: Optional[Dict] = {}

    cache_key = "import_is_running"
    cache.set(key=cache_key, value=True)

    # set delay to imitate a complicated task
    time.sleep(10)

    try:
        dir_files = get_files(folder)
    except FileNotFoundError as e:
        logger.critical(e)
    else:
        if not files:
            files = dir_files
            logger.warning("Файлы не выбраны, импорт инициирован из всех файлов находящихся в '%s'." % folder)

        for file in files:
            logger.info("Импорт файла %s..." % file)
            file_total += 1

            try:
                if file in dir_files:
                    file_format_validator(file=file, formats=formats)
                    file_path = os.path.join(folder, file)

                    with open(file_path, "r", encoding="utf-8") as f:
                        products = json.load(f)

                        l, f, t, e = load(products)
                else:
                    raise FileNotFoundError("Файла нет папке '%s'" % folder)

            except (DatabaseError, JSONDecodeError, FileNotFoundError, OSError, ValueError) as e:
                failed_file += 1
                excp[file] = [e]
                if not isinstance(e, FileNotFoundError):
                    os.rename(
                        os.path.join(folder, file),
                        os.path.join(folder, "failed_import_files", file),
                    )
                logger.critical("Файл '%s' не импортирован. %s: %s" % (file, type(e), e))

            else:
                total_loaded_product += l
                total_failed_product += f
                total_product += t
                successed_file += 1
                os.rename(file_path, os.path.join(folder, "success_import_files", file))

                if f > 0:
                    excp[file] = e
                    logger.warning(
                        "Файл %s импортирован не полностью. Импортировано %d из %d продуктов." % (file, l, t)
                    )
                else:
                    logger.info("Импорт файла '%s' завершен. Импортировано %d из %d продуктов." % (file, l, t))

        logger.info("Всего импортированно %d файлов из %d" % (successed_file, file_total))
        logger.info(
            "Всего импортированно %d из %d продуктов из %d файлов"
            % (total_loaded_product, total_product, successed_file)
        )

        mail_report(files, file_total, successed_file, excp, email_to)

    finally:
        cache.set(key=cache_key, value=False)


def load(products) -> tuple[int, int, int, List[Optional[Exception]]]:
    """
    Импорт проудктов из файла.
    """
    total_objects: int = 0
    loaded_object_count: int = 0
    failed_object_count: int = 0
    obj_count: int = 0
    excp: List[Union[Exception]] = []

    for product_data in products:
        total_objects += 1
        obj_count += 1
        logger.info("Импорт продукта №%d..." % obj_count)
        try:
            obj: ProductBaseModel = ProductBaseModel(**product_data)

            with transaction.atomic():
                shop = get_and_validate_shop(obj)
                manufacturer = get_or_create_manufacturer(obj)
                tags = get_or_create_tag(obj)

                try:
                    product = (
                        Product.objects.select_related("manufacturer", "category")
                        .prefetch_related("details", "tags")
                        .get(name=obj.name)
                    )

                except Product.DoesNotExist:
                    create_product(obj, manufacturer, shop, tags)
                    logger.info("Продукт №%d(%s) импортирован успешно" % (obj_count, obj.name))
                else:
                    update_product(obj, manufacturer, product, shop, tags)
                    logger.info("Продукт №%d(%s) обновлен успешно" % (obj_count, obj.name))

                loaded_object_count += 1

        except ValidationError as e:
            failed_object_count += 1
            excp.append(e)
            logger.error(
                "Продукт №%d не импортирован. %s: продукт содержит ошибки валидации в кол-ве: %s шт"
                % (obj_count, type(e), e.error_count())
            )

        except (ValueError, FileNotFoundError, IntegrityError) as e:
            failed_object_count += 1
            excp.append(e)
            logger.error("Продукт №%d(%s) не импортирован: %s %s" % (obj_count, product_data["name"], type(e), e))

        except DatabaseError:
            raise

        except Exception as e:
            failed_object_count += 1
            excp.append(e)
            logger.critical(
                "Продукт №%d(%s) не импортирован, необработаная ошибка: %s %s"
                % (obj_count, product_data["name"], type(e), e)
            )

    if total_objects == failed_object_count:
        raise ValueError("Ни один продукт не был добавлен")

    return loaded_object_count, failed_object_count, total_objects, excp


def create_product(obj: ProductBaseModel, manufacturer: Manufacturer, shop: Shop, tags: Optional[List[Tag]]) -> None:
    """
    Создание сущности Продукт.
    """
    # create product
    product = Product.objects.create(
        name=obj.name,
        category=category_create(obj),
        about=obj.about,
        description=obj.description,
        manufacturer=manufacturer,
    )
    # add tags if any
    product.tags.add(*tags)
    product.save()

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    # get or create details and create product_details
    product_details_create_or_update(obj, product)

    # create offer
    offer = Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)
    offer.save()


def update_product(obj: ProductBaseModel, manufacturer: Manufacturer, product: Product, shop: Shop, tags) -> None:
    """
    Обнавление сущности Продукт.
    """
    # update_product
    product.category = category_create(obj)
    product.manufacturer = manufacturer
    product.about = obj.about
    product.description = obj.description
    # clear current tags if any and add new if any
    product.tags.clear()
    product.tags.add(*tags)
    product.save()

    # delete image if any
    product.preview.delete(save=True)

    img_name, img_path = parse_img_name_and_validate(obj.preview)
    # add image
    with open(img_path, "rb") as f:
        product.preview.save(img_name, f, save=True)

    product_details_create_or_update(obj, product, update=True)

    try:
        offer = Offer.objects.select_related("shop", "product").get(product=product, shop=shop)
        # update offer
        offer.price = obj.offer.price
        offer.remains += obj.offer.quantity
        offer.save()
    except Offer.DoesNotExist:
        # create new offer
        Offer(product=product, shop=shop, price=obj.offer.price, remains=obj.offer.quantity)


def get_and_validate_shop(obj: ProductBaseModel) -> Shop:
    """Получение сущности Магазин."""
    try:
        shop = Shop.objects.get(name=obj.shop)
    except Shop.DoesNotExist:
        raise ValueError("Магазина '%s' нет базе данных" % obj.shop)
    else:
        return shop


def get_or_create_manufacturer(obj: ProductBaseModel) -> Manufacturer:
    """
    Получение или создание сущности Производитель.
    """
    try:
        manufacturer = Manufacturer.objects.get(name=obj.manufacturer.name)
    except Manufacturer.DoesNotExist:
        manufacturer = Manufacturer.objects.create(name=obj.manufacturer.name, slug=obj.manufacturer.slug)

    return manufacturer


def get_or_create_tag(obj: ProductBaseModel) -> Optional[List[Tag]]:
    """
    Получение списка сущностей Тag.
    """
    tags = []
    for tag_name in obj.tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)

    return tags


def main_category_create(obj: ProductBaseModel, has_sub_cat=False) -> Category:
    if has_sub_cat:
        category_data = (obj.category.subcategory, obj.category.sub_slug)
    else:
        category_data = (obj.category.category, obj.category.cat_slug)

    try:
        category = Category.objects.get(name=category_data[0])
        if category.parent:
            raise IntegrityError("'%s' уже используется в БД, как подкатегория." % category_data[0])

        category.slug = category_data[1]
        category.save()

        return category

    except Category.DoesNotExist:
        category = Category.objects.create(name=category_data[0], slug=category_data[1])
        return category


def category_create(obj: ProductBaseModel) -> Category:
    """
    Получение или создание сущности Категория.
    Если присутствует родительская категория,
    то попутно создается родительской категория.
    """

    if obj.category.subcategory:
        main_category = main_category_create(obj=obj, has_sub_cat=True)
        try:
            parent, created = Category.objects.get_or_create(name=obj.category.category, parent=main_category)
            if not created:
                parent.slug = obj.category.cat_slug
                parent.save()
            return parent

        except IntegrityError:
            raise

    else:
        return main_category_create(obj=obj, has_sub_cat=False)


def product_details_create_or_update(obj: ProductBaseModel, product: Product, update=False) -> None:
    """
    Создание или обновление свойств продукта и его характеристик.
    """
    detail_must_be_unique_validator(obj.details)

    if update:
        ProductDetail.objects.filter(product=product).delete()

    for item in obj.details:
        detail, created = Detail.objects.get_or_create(name=item.name)
        product_detail = ProductDetail(product=product, detail=detail, value=item.value)
        product_detail.save()


def detail_must_be_unique_validator(v: List[Optional[DetailsBaseModel]]) -> None:
    """
    Валидация параметров продукта по уникальности.
    """
    details = []
    for item in v:
        if item.name not in details:
            details.append(item.name)
        else:
            raise ValueError("Свойство продукта '%s' дублируется" % item.name)


def parse_img_name_and_validate(file_path: str) -> tuple[str, str]:
    """
    Получение названия изображения, валидация формата изображения и его пути.
    """
    allowed_extensions: List[str] = ["jpg", "jpeg", "img", "webp", "png", "gif", "svg", "bmp"]

    # Валидация пути
    if len(file_path) == 0:
        raise ValueError("Не задан путь к изображению.")
    if len(file_path) < 5:
        raise ValueError("Путь '%s' к изображению короче 4 символов." % file_path)

    if os.path.isfile(file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension[1:] in allowed_extensions:
            file_name = os.path.basename(file_path)

            return file_name, file_path

        else:
            raise ValueError("Формат изображения '%s' не поддерживается." % file_extension)
    else:
        raise FileNotFoundError("Файл изображения не существует или путь '%s' недействителен." % file_path)


def file_format_validator(file: str, formats: List[str]) -> None:
    """
    Валидация формата файла.
    """
    parts = file.rsplit(".", 2)

    if len(parts) > 1:
        if not parts[-1] in formats:
            raise OSError("Формат файла '%s' не поддерживается." % parts[-1])
    else:
        raise OSError("Формат файла не задан")


def get_files(folder: str) -> List[Optional[str]]:
    """
    Получение файлов из папки для импорта продуктов.
    """

    if not os.path.exists(folder):
        raise FileNotFoundError("Директория '%s' не существует." % folder)

    files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

    return files


def mail_report(
    files: Tuple[Optional[str]], file_total: int, successed_file: int, excp: Dict, email_to: Optional[str]
) -> None:
    """
    Отправка отчета по завершению команды ипорта продуктов.
    """
    if email_to:
        subject: str = "Отчет по заврешнению команды импорта продутков"
        html_content = html_content_maker(files, file_total, successed_file, excp)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email_to]
        msg = EmailMessage(subject, html_content, email_from, recipient_list)
        msg.content_subtype = "html"
        try:
            msg.send()
        except ValueError as e:
            logger.error("Отчет не отправлен на адреc: %s. Ошибка: %s" % (email_to, e))
        else:
            logger.info("Отчет отправлен на слeдующий адреc: %s" % email_to)

    else:
        logger.info("Отчет не отправлен. Адрес для отправки отчета не указан")


def html_content_maker(files: Tuple[Optional[str]], file_total: int, successed_file: int, excp: Dict) -> str:
    """
    Получения контента собщения в html.
    """
    html_content = "<h1>Отчет:</h1><p>Импортированно %d файлов из %d.</p>" % (successed_file, file_total)

    if excp:
        html_content += "<h2>Ошибки в следующих файлах: </h2>"
        for file in files:
            errors = excp.get(file)
            if errors:
                html_content += "<h3><b>'%s':</b></h3>" % file
                errors_count = 0
                for error in errors:
                    errors_count += 1
                    html_content += "<p>%d) %s</p>" % (errors_count, error)

    else:
        html_content += "<h2>Ошибкок не выявлено.</h2>"

    return html_content

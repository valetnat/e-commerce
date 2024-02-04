import datetime

from django.db import DatabaseError
from config.celery import app
from celery.utils.log import get_task_logger

from discount.models import CartPromo, ProductPromo, SetPromo


logger = get_task_logger(__name__)


@app.task(ignore_result=True, name="discount.tasks.update_discount_status")
def update_discount_status():
    logger.info("Запушена команда изменения статуса скидок")
    today = datetime.date.today()
    promos = list()

    try:
        promos.extend(SetPromo.objects.all())
        promos.extend(ProductPromo.objects.all())
        promos.extend(CartPromo.objects.all())

        for promo in promos:
            if promo.active_from <= today <= promo.active_to and promo.is_active is False:
                promo.is_active = True
                promo.save()
                logger.info(
                    "[model=%s, pk=%s, name=%s] - активирована" % (promo.__class__.__name__, promo.pk, promo.name)
                )

            if not promo.active_from <= today <= promo.active_to and promo.is_active is True:
                promo.is_active = False
                promo.save()
                logger.info(
                    "[model=%s, pk=%s, name=%s] - деактивирована" % (promo.__class__.__name__, promo.pk, promo.name)
                )

    except DatabaseError as e:
        logger.error("Ошибка %s: %s" % (type(e), e))

    except Exception as e:
        logger.error("Необработанная ошибка %s: %s" % (type(e), e))
        raise

    else:
        logger.info("Изменение статуса скидок завершено успешно")

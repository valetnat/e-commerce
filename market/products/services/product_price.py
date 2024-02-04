from products.models import Product


def product_min_price_or_none(product: Product, product_offers=None):
    """
    Возвращает минимальную цену товара(Product) серди всех предложений(offer), если передать список предложений,
    то будет искать среди этого списка, иначе будет искать по БД.
    :param product: Модель товара
    :param product_offers: Список предложений
    :return:
    """
    if product_offers:
        price = min(product_offers, key=lambda x: x.price).price
        return price
    else:
        offers = product.offers.all()
        if offers:
            return product_min_price_or_none(product, offers)
        else:
            return None

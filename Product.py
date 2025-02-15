import random
import shelve


class Product:
    # product_id = 0
    # all_product_ids = []

    def __init__(self, product_name, description, price, category, condition, remarks, image_filename=None):
        db = shelve.open('product.db', 'c')
        last_product_id = db.get('last_product_id', 0)
        new_product_id = last_product_id + 1

        self.__product_id = new_product_id
        self.__image_filename = image_filename
        self.__product_name = product_name
        self.__description = description
        self.__price = price
        self.__category = category
        self.__condition = condition
        self.__remarks = remarks

        db['last_product_id'] = new_product_id

        # Retrieve and update the Products list in shelve
        product_dict = db.get('Products', {})
        product_dict[self.__product_id] = self
        db['Products'] = product_dict

    def get_product_id(self):
        return self.__product_id

    def get_image_filename(self):
        return self.__image_filename

    def get_product_name(self):
        return self.__product_name

    def get_description(self):
        return self.__description

    def get_price(self):
        return self.__price

    def get_category(self):
        return self.__category

    def get_condition(self):
        return self.__condition

    def get_remarks(self):
        return self.__remarks

    def set_product_id(self, product_id):
        self.__product_id = product_id

    def set_image_filename(self, image_filename):
        self.__image_filename = image_filename

    def set_name(self, product_name):
        self.__product_name = product_name

    def set_description(self, description):
        self.__description = description

    def set_price(self, price):
        self.__price = price

    def set_category(self, category):
        self.__category = category

    def set_condition(self, condition):
        self.__condition = condition

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def __str__(self):
        return f'asd{id} name = {self.__product_name}'
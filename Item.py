class Item:
    count_id = 0

    def __init__(self, category, item, description, condition, stock, selling_price):
        Item.count_id += 1
        self.__item_id = Item.count_id
        self.__category = category
        self.__item = item
        self.__description = description
        self.__condition = condition
        self.__stock = stock
        self.__selling_price = selling_price

    def get_item_id(self):
        return self.__item_id

    def get_category(self):
        return self.__category

    def get_item(self):
        return self.__item

    def get_description(self):
        return self.__description

    def get_condition(self):
        return self.__condition

    def get_stock(self):
        return self.__stock

    def get_selling_price(self):
        return self.__selling_price

    def set_item_id(self, item_id):
        self.__item_id = item_id

    def set_category(self, category):
        self.__category = category

    def set_item(self, item):
        self.__item = item

    def set_description(self, description):
        self.__description = description

    def set_condition(self, condition):
        self.__condition = condition

    def set_stock(self, stock):
        self.__stock = stock

    def set_selling_price(self, selling_price):
        self.__selling_price = selling_price
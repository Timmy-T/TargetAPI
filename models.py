from marshmallow import Schema, fields


class PriceDataSchema(Schema):
    # This value is STR because Decimal is not serializable by default.
    # Future enhancements could include custom JSON encoder
    value = fields.Str()
    currency_code = fields.Str()


class ProductSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    current_price = fields.Nested(PriceDataSchema)


class Product:
    def __init__(self, id, name, price_data=None):
        self.id = id
        self.name = name
        self.current_price = price_data


class PriceData:
    def __init__(self, value, currency_code):
        self.value = value
        self.currency_code = currency_code

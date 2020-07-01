from marshmallow import Schema, fields

class PropertyPriceSchema(Schema):
    id = fields.Int(dump_only=True)
    freehold_price = fields.Int(dump_only=True)
    leasehold_price = fields.Int(dump_only=True)
    leasehold_period = fields.Str(dump_only=True)
    daily_price = fields.Int(dump_only=True)
    weekly_price = fields.Int(dump_only=True)
    monthly_price = fields.Int(dump_only=True)
    annually_price = fields.Int(dump_only=True)

from odoo import models, fields

class TransitVehicle(models.Model):
    _name = 'transit.vehicle'
    _description = 'Vehicle'

    registration_no = fields.Char(
        string="Registration Number",
        required=True
    )

    name = fields.Char(
        string="Vehicle Name",
        required=True
    )

    vehicle_type = fields.Selection([
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('car', 'Car')
    ], string="Vehicle Type")

    max_load_capacity = fields.Float(
        string="Maximum Load Capacity (kg)"
    )

    odometer = fields.Float(
        string="Odometer"
    )

    acquisition_cost = fields.Float(
        string="Acquisition Cost"
    )

    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired')
    ], default='available')
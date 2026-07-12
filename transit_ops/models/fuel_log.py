# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransitFuelLog(models.Model):
    _name = 'transit.fuel.log'
    _description = 'Fuel Log Entry'
    _inherit = ['mail.thread']
    _order = 'date desc'

    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
    )
    driver_id = fields.Many2one(
        'transit.driver',
        string='Driver',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
    )
    litres = fields.Float(
        string='Litres',
        required=True,
    )
    cost = fields.Float(
        string='Cost',
        required=True,
    )
    station = fields.Char(string='Fuel Station')
    mileage = fields.Float(string='Mileage (km)')

    # ── Related ──
    vehicle_name = fields.Char(related='vehicle_id.name', string='Vehicle Name')
    vehicle_registration = fields.Char(
        related='vehicle_id.registration_number',
        string='Vehicle Plate',
    )
    driver_name = fields.Char(related='driver_id.name', string='Driver Name')

    # ── Computed ──
    cost_per_litre = fields.Float(
        compute='_compute_cost_per_litre',
        string='Cost/Litre',
        store=True,
    )

    @api.depends('cost', 'litres')
    def _compute_cost_per_litre(self):
        for rec in self:
            rec.cost_per_litre = (rec.cost / rec.litres) if rec.litres > 0 else 0.0

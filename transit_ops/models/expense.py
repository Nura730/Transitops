# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransitExpense(models.Model):
    _name = 'transit.expense'
    _description = 'Operational Expense'
    _inherit = ['mail.thread']
    _order = 'date desc'

    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
    )
    expense_type = fields.Selection(
        selection=[
            ('fuel', 'Fuel'),
            ('maintenance', 'Maintenance'),
            ('insurance', 'Insurance'),
            ('toll', 'Toll'),
            ('other', 'Other'),
        ],
        string='Expense Type',
        default='other',
        required=True,
    )
    amount = fields.Float(
        string='Amount',
        required=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
    )
    description = fields.Text(string='Description')

    # ── Related ──
    vehicle_name = fields.Char(related='vehicle_id.name', string='Vehicle Name')
    vehicle_registration = fields.Char(
        related='vehicle_id.registration_number',
        string='Vehicle Plate',
    )

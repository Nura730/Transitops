# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class TransitDriver(models.Model):
    _name = 'transit.driver'
    _description = 'Fleet Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # ── Core Fields ──
    name = fields.Char(
        string='Driver Name',
        required=True,
        tracking=True,
    )
    license_number = fields.Char(
        string='License Number',
        required=True,
        copy=False,
        tracking=True,
    )
    license_category = fields.Selection(
        selection=[
            ('lmv', 'LMV'),
            ('hmv', 'HMV'),
        ],
        string='License Category',
        default='hmv',
        required=True,
    )
    license_expiry = fields.Date(
        string='License Expiry Date',
        required=True,
        tracking=True,
    )
    phone = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    safety_score = fields.Float(
        string='Safety Score',
        default=85.0,
        tracking=True,
    )
    rating = fields.Float(
        string='Rating',
        default=4.5,
    )
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_total_trips',
        store=True,
    )
    hours_per_week = fields.Float(
        string='Hours / Week',
        default=40.0,
    )
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('off_duty', 'Off Duty'),
            ('suspended', 'Suspended'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    # ── Relational ──
    trip_ids = fields.One2many('transit.trip', 'driver_id', string='Trips')
    fuel_log_ids = fields.One2many('transit.fuel.log', 'driver_id', string='Fuel Logs')

    # ── Computed ──
    is_license_expired = fields.Boolean(
        compute='_compute_license_status',
        string='License Expired',
        store=True,
    )
    license_days_remaining = fields.Integer(
        compute='_compute_license_status',
        string='Days Until Expiry',
        store=True,
    )
    license_status_display = fields.Char(
        compute='_compute_license_status',
        string='License Status',
    )

    # ── Constraints ──
    _sql_constraints = [
        ('license_number_unique', 'UNIQUE(license_number)',
         'The license number must be unique!'),
    ]

    @api.constrains('safety_score')
    def _check_safety_score(self):
        for rec in self:
            if rec.safety_score < 0 or rec.safety_score > 100:
                raise ValidationError("Safety score must be between 0 and 100.")

    # ── Computed Methods ──
    @api.depends('trip_ids', 'trip_ids.status')
    def _compute_total_trips(self):
        for rec in self:
            rec.total_trips = len(rec.trip_ids.filtered(lambda t: t.status == 'completed'))

    @api.depends('license_expiry')
    def _compute_license_status(self):
        today = date.today()
        for rec in self:
            if rec.license_expiry:
                delta = (rec.license_expiry - today).days
                rec.license_days_remaining = delta
                rec.is_license_expired = delta <= 0
                if delta <= 0:
                    rec.license_status_display = '🔴 Expired'
                elif delta <= 14:
                    rec.license_status_display = f'🔴 Expires in {delta}d'
                elif delta <= 30:
                    rec.license_status_display = f'🟠 Expires in {delta}d'
                else:
                    rec.license_status_display = f'🟢 Valid ({delta}d)'
            else:
                rec.license_days_remaining = 0
                rec.is_license_expired = True
                rec.license_status_display = '🔴 No expiry set'

    # ── Actions ──
    def action_set_available(self):
        for rec in self:
            rec.status = 'available'

    def action_set_off_duty(self):
        for rec in self:
            if rec.status == 'on_trip':
                raise ValidationError("Cannot set driver off-duty while on a trip.")
            rec.status = 'off_duty'

    def action_suspend(self):
        for rec in self:
            if rec.status == 'on_trip':
                raise ValidationError("Cannot suspend a driver while on a trip.")
            rec.status = 'suspended'

    def action_view_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Trips for {self.name}',
            'res_model': 'transit.trip',
            'view_mode': 'tree,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_check_on_trip(self):
        for rec in self:
            if rec.status == 'on_trip':
                raise ValidationError("Cannot delete a driver that is currently on a trip.")

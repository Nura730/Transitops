# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransitVehicle(models.Model):
    _name = 'transit.vehicle'
    _description = 'Fleet Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _rec_name = 'display_name'

    # ── Core Fields ──
    name = fields.Char(
        string='Vehicle Name / Model',
        required=True,
        tracking=True,
    )
    registration_number = fields.Char(
        string='Registration Number',
        required=True,
        copy=False,
        tracking=True,
    )
    vehicle_type = fields.Selection(
        selection=[
            ('truck', 'Truck'),
            ('trailer', 'Trailer'),
            ('van', 'Van'),
            ('reefer', 'Reefer'),
        ],
        string='Type',
        required=True,
        default='truck',
        tracking=True,
    )
    max_capacity = fields.Float(
        string='Maximum Load Capacity (kg)',
        required=True,
        tracking=True,
    )
    odometer = fields.Float(
        string='Odometer (km)',
        default=0.0,
        tracking=True,
    )
    acquisition_cost = fields.Float(
        string='Acquisition Cost',
        default=0.0,
        tracking=True,
    )
    fuel_level = fields.Float(
        string='Fuel Level (%)',
        default=100.0,
    )
    year = fields.Integer(
        string='Year',
        default=2024,
    )
    home_depot = fields.Char(
        string='Home Depot',
    )
    location = fields.Char(
        string='Current Location',
    )
    next_service_date = fields.Date(
        string='Next Service Date',
    )
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('in_shop', 'In Shop'),
            ('retired', 'Retired'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    # ── Relational Fields ──
    trip_ids = fields.One2many('transit.trip', 'vehicle_id', string='Trips')
    maintenance_ids = fields.One2many('transit.maintenance', 'vehicle_id', string='Maintenance Records')
    fuel_log_ids = fields.One2many('transit.fuel.log', 'vehicle_id', string='Fuel Logs')
    expense_ids = fields.One2many('transit.expense', 'vehicle_id', string='Expenses')

    # ── Computed Fields ──
    display_name = fields.Char(compute='_compute_display_name', store=True)
    trip_count = fields.Integer(compute='_compute_trip_count', string='Total Trips')
    total_fuel_cost = fields.Float(compute='_compute_costs', string='Total Fuel Cost')
    total_maintenance_cost = fields.Float(compute='_compute_costs', string='Total Maintenance Cost')
    operational_cost = fields.Float(compute='_compute_costs', string='Operational Cost')
    total_revenue = fields.Float(compute='_compute_costs', string='Total Revenue')
    vehicle_roi = fields.Float(compute='_compute_costs', string='Vehicle ROI (%)')
    fuel_efficiency = fields.Float(compute='_compute_costs', string='Fuel Efficiency (km/L)')

    # ── Constraints ──
    _sql_constraints = [
        ('registration_number_unique', 'UNIQUE(registration_number)',
         'The vehicle registration number must be unique!'),
    ]

    @api.constrains('max_capacity')
    def _check_max_capacity(self):
        for rec in self:
            if rec.max_capacity <= 0:
                raise ValidationError("Maximum load capacity must be greater than zero.")

    # ── Computed Methods ──
    @api.depends('name', 'registration_number')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} [{rec.registration_number}]" if rec.registration_number else rec.name

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.trip_ids.filtered(lambda t: t.status == 'completed'))

    @api.depends('trip_ids', 'fuel_log_ids', 'maintenance_ids', 'acquisition_cost')
    def _compute_costs(self):
        for rec in self:
            completed_trips = rec.trip_ids.filtered(lambda t: t.status == 'completed')
            rec.total_revenue = sum(completed_trips.mapped('revenue'))
            rec.total_fuel_cost = sum(rec.fuel_log_ids.mapped('cost'))
            rec.total_maintenance_cost = sum(rec.maintenance_ids.mapped('cost'))
            rec.operational_cost = rec.total_fuel_cost + rec.total_maintenance_cost
            # ROI = (Revenue - (Maintenance + Fuel)) / Acquisition Cost
            if rec.acquisition_cost > 0:
                rec.vehicle_roi = ((rec.total_revenue - rec.operational_cost) / rec.acquisition_cost) * 100
            else:
                rec.vehicle_roi = 0.0
            # Fuel Efficiency = Total Distance / Total Fuel
            total_distance = sum(completed_trips.mapped('distance'))
            total_litres = sum(rec.fuel_log_ids.mapped('litres'))
            rec.fuel_efficiency = (total_distance / total_litres) if total_litres > 0 else 0.0

    # ── Actions ──
    def action_set_available(self):
        for rec in self:
            rec.status = 'available'

    def action_set_retired(self):
        for rec in self:
            if rec.status == 'on_trip':
                raise ValidationError("Cannot retire a vehicle that is currently on a trip.")
            rec.status = 'retired'

    def action_view_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Trips for {self.name}',
            'res_model': 'transit.trip',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Maintenance for {self.name}',
            'res_model': 'transit.maintenance',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_fuel_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Fuel Logs for {self.name}',
            'res_model': 'transit.fuel.log',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_check_on_trip(self):
        for rec in self:
            if rec.status == 'on_trip':
                raise ValidationError("Cannot delete a vehicle that is currently on a trip.")

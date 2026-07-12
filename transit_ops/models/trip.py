# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class TransitTrip(models.Model):
    _name = 'transit.trip'
    _description = 'Transport Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ── Core Fields ──
    trip_code = fields.Char(
        string='Trip Code',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    source = fields.Char(
        string='Source / Origin',
        required=True,
        tracking=True,
    )
    destination = fields.Char(
        string='Destination',
        required=True,
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
    )
    driver_id = fields.Many2one(
        'transit.driver',
        string='Driver',
        required=True,
        tracking=True,
    )
    cargo_weight = fields.Float(
        string='Cargo Weight (kg)',
        required=True,
        tracking=True,
    )
    distance = fields.Float(
        string='Planned Distance (km)',
        default=0.0,
    )
    revenue = fields.Float(
        string='Revenue',
        default=0.0,
        tracking=True,
    )
    priority = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        string='Priority',
        default='standard',
    )
    pickup_date = fields.Datetime(
        string='Pickup Date & Time',
        default=fields.Datetime.now,
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('dispatched', 'Dispatched'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    dispatched_at = fields.Datetime(string='Dispatched At', readonly=True)
    completed_at = fields.Datetime(string='Completed At', readonly=True)
    cancelled_at = fields.Datetime(string='Cancelled At', readonly=True)

    # Trip completion fields
    final_odometer = fields.Float(string='Final Odometer Reading')
    fuel_consumed = fields.Float(string='Fuel Consumed (L)')

    # ── Related / Computed ──
    vehicle_max_capacity = fields.Float(
        related='vehicle_id.max_capacity',
        string='Vehicle Capacity (kg)',
        readonly=True,
    )
    vehicle_registration = fields.Char(
        related='vehicle_id.registration_number',
        string='Vehicle Plate',
    )
    driver_license = fields.Char(
        related='driver_id.license_number',
        string='Driver License',
    )
    vehicle_status = fields.Selection(
        related='vehicle_id.status',
        string='Vehicle Status',
    )
    driver_status = fields.Selection(
        related='driver_id.status',
        string='Driver Status',
    )
    fuel_efficiency_trip = fields.Float(
        compute='_compute_fuel_efficiency',
        string='Fuel Efficiency (km/L)',
    )

    # ── Sequence ──
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('trip_code', 'New') == 'New':
                vals['trip_code'] = self.env['ir.sequence'].next_by_code('transit.trip') or 'New'
        return super().create(vals_list)

    # ── Constraints ──
    @api.constrains('cargo_weight', 'vehicle_id')
    def _check_cargo_weight(self):
        for rec in self:
            if rec.vehicle_id and rec.cargo_weight > rec.vehicle_id.max_capacity:
                raise ValidationError(
                    f"Cargo weight ({rec.cargo_weight} kg) exceeds vehicle maximum "
                    f"capacity ({rec.vehicle_id.max_capacity} kg)."
                )

    @api.constrains('vehicle_id', 'status')
    def _check_vehicle_availability(self):
        """Retired or In Shop vehicles must never appear in dispatch selection."""
        for rec in self:
            if rec.status == 'draft' and rec.vehicle_id.status in ('in_shop', 'retired'):
                raise ValidationError(
                    f"Vehicle '{rec.vehicle_id.name}' is {rec.vehicle_id.status.replace('_', ' ')} "
                    f"and cannot be assigned to a trip."
                )
            if rec.status == 'draft' and rec.vehicle_id.status == 'on_trip':
                raise ValidationError(
                    f"Vehicle '{rec.vehicle_id.name}' is already on another trip."
                )

    @api.constrains('driver_id', 'status')
    def _check_driver_availability(self):
        """Drivers with expired licenses or Suspended status cannot be assigned."""
        for rec in self:
            if rec.status in ('draft', 'dispatched'):
                if rec.driver_id.status == 'suspended':
                    raise ValidationError(
                        f"Driver '{rec.driver_id.name}' is suspended and cannot be assigned to a trip."
                    )
                if rec.driver_id.is_license_expired:
                    raise ValidationError(
                        f"Driver '{rec.driver_id.name}' has an expired license and cannot be assigned to a trip."
                    )
                if rec.driver_id.status == 'on_trip':
                    # Check if this driver is on trip for a DIFFERENT trip
                    other_active = self.search([
                        ('driver_id', '=', rec.driver_id.id),
                        ('status', '=', 'dispatched'),
                        ('id', '!=', rec.id),
                    ])
                    if other_active:
                        raise ValidationError(
                            f"Driver '{rec.driver_id.name}' is already assigned to another active trip."
                        )

    # ── Computed ──
    @api.depends('distance', 'fuel_consumed')
    def _compute_fuel_efficiency(self):
        for rec in self:
            if rec.fuel_consumed and rec.fuel_consumed > 0:
                rec.fuel_efficiency_trip = rec.distance / rec.fuel_consumed
            else:
                rec.fuel_efficiency_trip = 0.0

    # ── Onchange ──
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Filter only available vehicles and warn about capacity."""
        if self.vehicle_id and self.vehicle_id.status != 'available':
            return {
                'warning': {
                    'title': 'Vehicle Not Available',
                    'message': f"Vehicle '{self.vehicle_id.name}' is currently "
                               f"{self.vehicle_id.status.replace('_', ' ')}.",
                }
            }

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        """Warn about driver issues."""
        if self.driver_id:
            if self.driver_id.is_license_expired:
                return {
                    'warning': {
                        'title': 'Expired License',
                        'message': f"Driver '{self.driver_id.name}' has an expired license!",
                    }
                }
            if self.driver_id.status == 'suspended':
                return {
                    'warning': {
                        'title': 'Suspended Driver',
                        'message': f"Driver '{self.driver_id.name}' is suspended.",
                    }
                }

    @api.onchange('cargo_weight')
    def _onchange_cargo_weight(self):
        if self.vehicle_id and self.cargo_weight > self.vehicle_id.max_capacity:
            return {
                'warning': {
                    'title': 'Overweight',
                    'message': f"Cargo weight ({self.cargo_weight} kg) exceeds vehicle "
                               f"capacity ({self.vehicle_id.max_capacity} kg).",
                }
            }

    # ── Business Logic: Status Transitions ──
    def action_dispatch(self):
        """
        Dispatch a trip.
        - Vehicle must be AVAILABLE → changes to ON_TRIP
        - Driver must be AVAILABLE → changes to ON_TRIP
        """
        for rec in self:
            if rec.status != 'draft':
                raise ValidationError("Only draft trips can be dispatched.")
            if rec.vehicle_id.status != 'available':
                raise ValidationError(
                    f"Vehicle '{rec.vehicle_id.name}' is not available "
                    f"(current status: {rec.vehicle_id.status.replace('_', ' ')})."
                )
            if rec.driver_id.status != 'available':
                raise ValidationError(
                    f"Driver '{rec.driver_id.name}' is not available "
                    f"(current status: {rec.driver_id.status.replace('_', ' ')})."
                )
            if rec.driver_id.is_license_expired:
                raise ValidationError(
                    f"Driver '{rec.driver_id.name}' has an expired license."
                )
            if rec.cargo_weight > rec.vehicle_id.max_capacity:
                raise ValidationError(
                    f"Cargo weight ({rec.cargo_weight} kg) exceeds vehicle capacity "
                    f"({rec.vehicle_id.max_capacity} kg)."
                )

            # Atomic status transitions
            rec.write({
                'status': 'dispatched',
                'dispatched_at': fields.Datetime.now(),
            })
            rec.vehicle_id.write({'status': 'on_trip'})
            rec.driver_id.write({'status': 'on_trip'})

    def action_complete(self):
        """
        Complete a trip.
        - Vehicle status → AVAILABLE
        - Driver status → AVAILABLE
        - Update odometer if final reading provided
        """
        for rec in self:
            if rec.status != 'dispatched':
                raise ValidationError("Only dispatched trips can be completed.")

            rec.write({
                'status': 'completed',
                'completed_at': fields.Datetime.now(),
            })
            # Restore vehicle
            vals = {'status': 'available'}
            if rec.final_odometer:
                vals['odometer'] = rec.final_odometer
            rec.vehicle_id.write(vals)
            # Restore driver
            rec.driver_id.write({'status': 'available'})

    def action_cancel(self):
        """
        Cancel a trip.
        - If dispatched: restore Vehicle and Driver to AVAILABLE
        """
        for rec in self:
            if rec.status in ('completed', 'cancelled'):
                raise ValidationError(
                    f"Cannot cancel a trip that is already {rec.status}."
                )
            was_dispatched = rec.status == 'dispatched'
            rec.write({
                'status': 'cancelled',
                'cancelled_at': fields.Datetime.now(),
            })
            if was_dispatched:
                rec.vehicle_id.write({'status': 'available'})
                rec.driver_id.write({'status': 'available'})

    def action_reset_to_draft(self):
        for rec in self:
            if rec.status != 'cancelled':
                raise ValidationError("Only cancelled trips can be reset to draft.")
            rec.write({'status': 'draft'})

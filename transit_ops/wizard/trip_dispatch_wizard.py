# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TripDispatchWizard(models.TransientModel):
    """Guided wizard to create and dispatch a trip in one flow."""
    _name = 'transit.trip.dispatch.wizard'
    _description = 'Trip Dispatch Wizard'

    # Step 1: Route
    source = fields.Char(string='Origin', required=True)
    destination = fields.Char(string='Destination', required=True)
    pickup_date = fields.Datetime(
        string='Pickup Date & Time',
        default=fields.Datetime.now,
        required=True,
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

    # Step 2: Vehicle
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        domain="[('status', '=', 'available')]",
        required=True,
    )
    vehicle_capacity = fields.Float(
        related='vehicle_id.max_capacity',
        string='Vehicle Capacity (kg)',
        readonly=True,
    )

    # Step 3: Driver
    driver_id = fields.Many2one(
        'transit.driver',
        string='Driver',
        domain="[('status', '=', 'available'), ('is_license_expired', '=', False)]",
        required=True,
    )
    driver_safety_score = fields.Float(
        related='driver_id.safety_score',
        string='Safety Score',
        readonly=True,
    )

    # Step 4: Cargo
    cargo_weight = fields.Float(string='Cargo Weight (kg)', required=True)
    distance = fields.Float(string='Distance (km)')
    revenue = fields.Float(string='Revenue')

    # ── Onchange ──
    @api.onchange('cargo_weight')
    def _onchange_cargo_weight(self):
        if self.vehicle_id and self.cargo_weight > self.vehicle_id.max_capacity:
            return {
                'warning': {
                    'title': 'Overweight!',
                    'message': f'Cargo weight ({self.cargo_weight} kg) exceeds '
                               f'vehicle capacity ({self.vehicle_id.max_capacity} kg).',
                }
            }

    # ── Confirm & Dispatch ──
    def action_confirm_dispatch(self):
        """Creates a trip and immediately dispatches it."""
        self.ensure_one()

        # Validations
        if self.cargo_weight > self.vehicle_id.max_capacity:
            raise ValidationError(
                f"Cargo weight ({self.cargo_weight} kg) exceeds vehicle capacity "
                f"({self.vehicle_id.max_capacity} kg)."
            )

        Trip = self.env['transit.trip']
        trip = Trip.create({
            'source': self.source,
            'destination': self.destination,
            'pickup_date': self.pickup_date,
            'priority': self.priority,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'cargo_weight': self.cargo_weight,
            'distance': self.distance,
            'revenue': self.revenue,
        })

        # Dispatch
        trip.action_dispatch()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Dispatched Trip',
            'res_model': 'transit.trip',
            'res_id': trip.id,
            'view_mode': 'form',
            'target': 'current',
        }

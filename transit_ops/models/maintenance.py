# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransitMaintenance(models.Model):
    _name = 'transit.maintenance'
    _description = 'Vehicle Maintenance Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ── Core Fields ──
    work_order_code = fields.Char(
        string='Work Order',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
        required=True,
    )
    maintenance_type = fields.Selection(
        selection=[
            ('engine_repair', 'Engine Repair'),
            ('annual_service', 'Annual Service'),
            ('oil_change', 'Oil Change'),
            ('brake_inspection', 'Brake Inspection'),
            ('tire_rotation', 'Tire Rotation'),
            ('general', 'General'),
        ],
        string='Maintenance Type',
        default='general',
        required=True,
    )
    technician = fields.Char(string='Technician')
    cost = fields.Float(
        string='Cost',
        default=0.0,
        tracking=True,
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.context_today,
        required=True,
    )
    end_date = fields.Date(string='End Date')
    status = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        string='Status',
        default='open',
        required=True,
        tracking=True,
    )

    # ── Related ──
    vehicle_name = fields.Char(related='vehicle_id.name', string='Vehicle Name')
    vehicle_registration = fields.Char(
        related='vehicle_id.registration_number',
        string='Vehicle Plate',
    )

    # ── Sequence ──
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('work_order_code', 'New') == 'New':
                vals['work_order_code'] = self.env['ir.sequence'].next_by_code('transit.maintenance') or 'New'
        records = super().create(vals_list)
        # Creating maintenance record → Vehicle status becomes IN_SHOP
        for rec in records:
            if rec.vehicle_id.status == 'on_trip':
                raise ValidationError(
                    f"Cannot create maintenance for vehicle '{rec.vehicle_id.name}' "
                    f"while it is on a trip."
                )
            if rec.status in ('open', 'in_progress'):
                rec.vehicle_id.write({'status': 'in_shop'})
        return records

    # ── Actions ──
    def action_start(self):
        for rec in self:
            if rec.status != 'open':
                raise ValidationError("Only open work orders can be started.")
            rec.write({'status': 'in_progress'})
            rec.vehicle_id.write({'status': 'in_shop'})

    def action_complete(self):
        """
        Closing maintenance restores the vehicle to Available (unless retired).
        """
        for rec in self:
            if rec.status == 'completed':
                raise ValidationError("This work order is already completed.")
            new_status = 'available' if rec.vehicle_id.status != 'retired' else 'retired'
            rec.write({
                'status': 'completed',
                'end_date': fields.Date.context_today(self),
            })
            rec.vehicle_id.write({'status': new_status})

    def action_reopen(self):
        for rec in self:
            if rec.status != 'completed':
                raise ValidationError("Only completed work orders can be reopened.")
            rec.write({'status': 'open'})
            rec.vehicle_id.write({'status': 'in_shop'})

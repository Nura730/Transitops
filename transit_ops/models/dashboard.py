# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransitDashboard(models.TransientModel):
    """Transient model used to aggregate KPI data for the dashboard view."""
    _name = 'transit.dashboard'
    _description = 'TransitOps Dashboard'

    # ── Vehicle KPIs ──
    total_vehicles = fields.Integer(string='Total Vehicles', readonly=True)
    available_vehicles = fields.Integer(string='Available', readonly=True)
    on_trip_vehicles = fields.Integer(string='On Trip', readonly=True)
    in_shop_vehicles = fields.Integer(string='In Shop', readonly=True)
    retired_vehicles = fields.Integer(string='Retired', readonly=True)

    # ── Driver KPIs ──
    total_drivers = fields.Integer(string='Total Drivers', readonly=True)
    available_drivers = fields.Integer(string='Available Drivers', readonly=True)
    on_trip_drivers = fields.Integer(string='Drivers on Duty', readonly=True)
    expired_license_drivers = fields.Integer(string='Expired Licenses', readonly=True)

    # ── Trip KPIs ──
    active_trips = fields.Integer(string='Active Trips', readonly=True)
    pending_trips = fields.Integer(string='Pending Trips', readonly=True)
    completed_trips = fields.Integer(string='Completed Trips', readonly=True)
    cancelled_trips = fields.Integer(string='Cancelled Trips', readonly=True)

    # ── Financial KPIs ──
    fleet_utilization = fields.Float(string='Fleet Utilization (%)', readonly=True)
    total_fuel_cost = fields.Float(string='Total Fuel Cost', readonly=True)
    total_maintenance_cost = fields.Float(string='Total Maintenance Cost', readonly=True)
    total_revenue = fields.Float(string='Total Revenue', readonly=True)
    total_distance = fields.Float(string='Total Distance (km)', readonly=True)

    @api.model
    def default_get(self, fields_list):
        """Compute all KPIs when the dashboard is opened."""
        res = super().default_get(fields_list)

        Vehicle = self.env['transit.vehicle']
        Driver = self.env['transit.driver']
        Trip = self.env['transit.trip']
        FuelLog = self.env['transit.fuel.log']
        Maintenance = self.env['transit.maintenance']

        # Vehicle stats
        res['total_vehicles'] = Vehicle.search_count([])
        res['available_vehicles'] = Vehicle.search_count([('status', '=', 'available')])
        res['on_trip_vehicles'] = Vehicle.search_count([('status', '=', 'on_trip')])
        res['in_shop_vehicles'] = Vehicle.search_count([('status', '=', 'in_shop')])
        res['retired_vehicles'] = Vehicle.search_count([('status', '=', 'retired')])

        # Driver stats
        res['total_drivers'] = Driver.search_count([])
        res['available_drivers'] = Driver.search_count([('status', '=', 'available')])
        res['on_trip_drivers'] = Driver.search_count([('status', '=', 'on_trip')])
        res['expired_license_drivers'] = Driver.search_count([('is_license_expired', '=', True)])

        # Trip stats
        res['active_trips'] = Trip.search_count([('status', '=', 'dispatched')])
        res['pending_trips'] = Trip.search_count([('status', '=', 'draft')])
        res['completed_trips'] = Trip.search_count([('status', '=', 'completed')])
        res['cancelled_trips'] = Trip.search_count([('status', '=', 'cancelled')])

        # Financial stats
        active_fleet = res['total_vehicles'] - res['retired_vehicles']
        res['fleet_utilization'] = round(
            (res['on_trip_vehicles'] / active_fleet * 100) if active_fleet > 0 else 0.0, 1
        )
        res['total_fuel_cost'] = sum(FuelLog.search([]).mapped('cost'))
        res['total_maintenance_cost'] = sum(Maintenance.search([]).mapped('cost'))

        completed = Trip.search([('status', '=', 'completed')])
        res['total_revenue'] = sum(completed.mapped('revenue'))
        res['total_distance'] = sum(completed.mapped('distance'))

        return res

    def action_open_vehicles(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Registry',
            'res_model': 'transit.vehicle',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def action_open_drivers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Drivers',
            'res_model': 'transit.driver',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def action_open_trips(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trip Dispatcher',
            'res_model': 'transit.trip',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def action_open_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance',
            'res_model': 'transit.maintenance',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_open_fuel_logs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel Logs',
            'res_model': 'transit.fuel.log',
            'view_mode': 'tree,form,graph',
            'target': 'current',
        }

    def action_open_dispatch_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Dispatch',
            'res_model': 'transit.trip.dispatch.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_open_expired_licenses(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Drivers with Expired Licenses',
            'res_model': 'transit.driver',
            'view_mode': 'tree,form',
            'domain': [('is_license_expired', '=', True)],
            'target': 'current',
        }

    def action_refresh(self):
        """Reload dashboard with fresh data."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dashboard',
            'res_model': 'transit.dashboard',
            'view_mode': 'form',
            'target': 'inline',
        }

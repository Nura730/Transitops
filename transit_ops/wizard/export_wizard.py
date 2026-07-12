# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import io
import csv
from datetime import datetime


class TransitExportWizard(models.TransientModel):
    """Wizard to export data as CSV."""
    _name = 'transit.export.wizard'
    _description = 'Export Data to CSV'

    export_model = fields.Selection(
        selection=[
            ('transit.trip', 'Trips'),
            ('transit.vehicle', 'Vehicles'),
            ('transit.driver', 'Drivers'),
            ('transit.maintenance', 'Maintenance'),
            ('transit.fuel.log', 'Fuel Logs'),
            ('transit.expense', 'Expenses'),
        ],
        string='Export Data',
        default='transit.trip',
        required=True,
    )
    status_filter = fields.Selection(
        selection=[
            ('all', 'All Records'),
            ('dispatched', 'Active / Dispatched'),
            ('completed', 'Completed'),
            ('available', 'Available'),
        ],
        string='Status Filter',
        default='all',
    )
    csv_file = fields.Binary(string='CSV File', readonly=True)
    csv_filename = fields.Char(string='Filename', readonly=True)

    def action_export(self):
        self.ensure_one()
        output = io.StringIO()
        writer = csv.writer(output)

        model = self.export_model
        domain = []

        if model == 'transit.trip':
            if self.status_filter == 'dispatched':
                domain = [('status', '=', 'dispatched')]
            elif self.status_filter == 'completed':
                domain = [('status', '=', 'completed')]

            headers = ['Trip Code', 'Source', 'Destination', 'Vehicle', 'Driver',
                        'Cargo (kg)', 'Distance (km)', 'Revenue', 'Priority',
                        'Status', 'Pickup Date', 'Dispatched At', 'Completed At']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.trip_code, rec.source, rec.destination,
                    rec.vehicle_id.name or '', rec.driver_id.name or '',
                    rec.cargo_weight, rec.distance, rec.revenue,
                    dict(rec._fields['priority'].selection).get(rec.priority, ''),
                    dict(rec._fields['status'].selection).get(rec.status, ''),
                    rec.pickup_date or '', rec.dispatched_at or '', rec.completed_at or '',
                ])
            filename = f'trips_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        elif model == 'transit.vehicle':
            if self.status_filter == 'available':
                domain = [('status', '=', 'available')]

            headers = ['Registration', 'Name', 'Type', 'Capacity (kg)', 'Odometer (km)',
                        'Fuel Level (%)', 'Location', 'Home Depot', 'Status', 'Year',
                        'Acquisition Cost', 'Total Revenue', 'ROI (%)']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.registration_number, rec.name,
                    dict(rec._fields['vehicle_type'].selection).get(rec.vehicle_type, ''),
                    rec.max_capacity, rec.odometer, rec.fuel_level,
                    rec.location or '', rec.home_depot or '',
                    dict(rec._fields['status'].selection).get(rec.status, ''),
                    rec.year, rec.acquisition_cost, rec.total_revenue,
                    round(rec.vehicle_roi, 2),
                ])
            filename = f'vehicles_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        elif model == 'transit.driver':
            headers = ['Name', 'License Number', 'Category', 'License Expiry',
                        'Phone', 'Email', 'Safety Score', 'Rating',
                        'Total Trips', 'Hours/Week', 'Status', 'License Status']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.name, rec.license_number,
                    dict(rec._fields['license_category'].selection).get(rec.license_category, ''),
                    rec.license_expiry or '', rec.phone or '', rec.email or '',
                    rec.safety_score, rec.rating, rec.total_trips,
                    rec.hours_per_week,
                    dict(rec._fields['status'].selection).get(rec.status, ''),
                    rec.license_status_display or '',
                ])
            filename = f'drivers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        elif model == 'transit.maintenance':
            headers = ['Work Order', 'Vehicle', 'Plate', 'Type', 'Description',
                        'Technician', 'Cost', 'Start Date', 'End Date', 'Status']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.work_order_code, rec.vehicle_id.name or '',
                    rec.vehicle_registration or '',
                    dict(rec._fields['maintenance_type'].selection).get(rec.maintenance_type, ''),
                    rec.description or '', rec.technician or '',
                    rec.cost, rec.start_date or '', rec.end_date or '',
                    dict(rec._fields['status'].selection).get(rec.status, ''),
                ])
            filename = f'maintenance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        elif model == 'transit.fuel.log':
            headers = ['Date', 'Vehicle', 'Plate', 'Driver', 'Station',
                        'Litres', 'Cost', 'Cost/Litre', 'Mileage']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.date or '', rec.vehicle_id.name or '',
                    rec.vehicle_registration or '', rec.driver_id.name or '',
                    rec.station or '', rec.litres, rec.cost,
                    round(rec.cost_per_litre, 2), rec.mileage,
                ])
            filename = f'fuel_logs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        elif model == 'transit.expense':
            headers = ['Date', 'Vehicle', 'Plate', 'Type', 'Amount', 'Description']
            writer.writerow(headers)

            records = self.env[model].search(domain)
            for rec in records:
                writer.writerow([
                    rec.date or '', rec.vehicle_id.name or '',
                    rec.vehicle_registration or '',
                    dict(rec._fields['expense_type'].selection).get(rec.expense_type, ''),
                    rec.amount, rec.description or '',
                ])
            filename = f'expenses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        else:
            filename = 'export.csv'

        # Encode and store
        csv_data = output.getvalue().encode('utf-8')
        self.write({
            'csv_file': base64.b64encode(csv_data),
            'csv_filename': filename,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Download CSV',
            'res_model': 'transit.export.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

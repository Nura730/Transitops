# -*- coding: utf-8 -*-
{
    'name': 'TransitOps - Smart Transport Operations',
    'version': '17.0.1.0.0',
    'category': 'Fleet/Transport',
    'summary': 'End-to-end transport operations platform for vehicle, driver, dispatch, maintenance and expense management',
    'description': """
TransitOps — Smart Transport Operations Platform
=================================================
A centralized platform that allows organizations to manage the complete lifecycle
of their transport operations — from vehicle registration and driver management
to dispatching, maintenance, fuel logging, and analytics.

Key Features:
- Vehicle Registry with status tracking (Available, On Trip, In Shop, Retired)
- Driver Management with license compliance and safety scores
- Trip Dispatcher with full lifecycle (Draft → Dispatched → Completed / Cancelled)
- Maintenance workflow with automatic vehicle status transitions
- Fuel & Expense Management with operational cost computation
- Dashboard with KPIs and visual analytics
- Role-Based Access Control (Fleet Manager, Dispatcher, Safety Officer, Financial Analyst)
- CSV/PDF export for reports
- Automatic status transitions enforcing mandatory business rules
    """,
    'author': 'TransitOps Team',
    'website': 'https://transitops.io',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        # Security — must load FIRST
        'security/transit_ops_security.xml',
        'security/ir.model.access.csv',
        # Views — actions + views
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/trip_views.xml',
        'views/maintenance_views.xml',
        'views/fuel_views.xml',
        'views/expense_views.xml',
        'views/dashboard_views.xml',
        # Wizards
        'wizard/trip_dispatch_wizard_views.xml',
        'wizard/export_wizard_views.xml',
        # Menus — load AFTER actions
        'views/menu_views.xml',
        # Reports
        'reports/trip_report.xml',
        'reports/trip_report_template.xml',
        # Demo data — load last
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'transit_ops/static/src/css/transit_ops.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}

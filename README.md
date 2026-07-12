# TransitOps — Smart Transport Operations Platform (Odoo 17 Module)

TransitOps is a production-ready enterprise Odoo custom module designed to digitize vehicle, driver, dispatch, maintenance, and expense management while enforcing strict business rules and providing real-time operational insights. 

Developed as a native Odoo module for the 2026 Odoo Hackathon.

---

## 🚀 Key Features

*   **Dashboard (Control Center)**: Real-time visual KPIs for fleet status, trip operations, compliance (expired licenses), and financials with direct navigation and refreshing.
*   **Vehicle Registry**: Detailed master list tracking registration numbers (enforced unique), capacities, odometer, fuel levels, and current status (`Available`, `On Trip`, `In Shop`, `Retired`).
*   **Driver Management**: Full profiles with license details, expiry tracking, contact info, ratings, safety scores, and status (`Available`, `On Duty`, `Off Duty`, `Suspended`).
*   **Trip Dispatcher**: Full dispatch workflow (`Draft` ➔ `Dispatched` ➔ `Completed` / `Cancelled`) with automated status updates.
*   **Maintenance Logs**: Service tracking that automatically shifts vehicle status to `In Shop` and blocks dispatch allocation.
*   **Fuel & Expense Logs**: Fuel logging and operational cost tracking with auto-computed total cost of ownership per vehicle.
*   **Reports & Export**: Built-in interactive graph/pivot views, downloadable PDF trip reports, and a custom **CSV Export Wizard** for all tables.

---

## 🔒 Role-Based Access Control (RBAC)

TransitOps supports native Odoo security groups and access control lists (ACL) to restrict features based on the logged-in user:

| Role | Description | Access Rights |
| :--- | :--- | :--- |
| **Driver** | Performs delivery dispatches and logs status. | • Full access to Trips & Quick Dispatch.<br>• Read-only access to Vehicles & Drivers.<br>• *Hidden*: Maintenance, Fuel, Expenses, Reports. |
| **Safety Officer** | Monitors safety scores and handles compliance. | • Inherits Driver access.<br>• Full CRUD access to Drivers & license validity.<br>• Full access to Maintenance Logs. |
| **Financial Analyst** | Reviews costs, fuel consumption, and ROI. | • Inherits Driver access.<br>• Full access to Fuel Logs and Expenses.<br>• Full access to Reports, Analytics, and CSV Export. |
| **Fleet Manager** | Full administrator over the module. | • Full CRUD access across all models and features. |

---

## 📦 Project Structure

```bash
transit_ops/
├── data/
│   └── demo_data.xml                  # Realistic pre-loaded test data (vehicles, drivers, logs)
├── models/
│   ├── vehicle.py                     # Vehicle schema and ROI computations
│   ├── driver.py                      # Driver details and license validation
│   ├── trip.py                        # Trip status workflow and capacity constraints
│   ├── maintenance.py                 # Maintenance log and status triggers
│   ├── fuel_log.py                    # Fuel log schema and mileage calculation
│   ├── expense.py                     # Expense logs
│   └── dashboard.py                   # Dynamic transient dashboard model
├── security/
│   ├── transit_ops_security.xml       # Security groups (RBAC) and record rules
│   └── ir.model.access.csv            # Table-level CRUD access rules
├── views/
│   ├── vehicle_views.xml              # Kanban, Tree, Form, Search layouts
│   ├── driver_views.xml               # Drivers list, cards, and forms
│   ├── trip_views.xml                 # Stepper workflow and dispatches
│   ├── maintenance_views.xml          # Work orders
│   ├── fuel_views.xml                 # Fuel logs list
│   ├── expense_views.xml              # Expenses list
│   ├── dashboard_views.xml            # KPI cards & visual analytics layout
│   └── menu_views.xml                 # App navbar menus and security restrictions
├── reports/
│   ├── trip_report.xml                # PDF QWeb report action
│   └── trip_report_template.xml       # QWeb report design
├── static/
│   ├── description/icon.png           # Module logo
│   └── src/css/transit_ops.css        # Premium UI theme stylesheet
└── wizard/
    ├── trip_dispatch_wizard.py        # Fast dispatch dialog logic
    ├── trip_dispatch_wizard_views.xml # Dispatch wizard form
    ├── export_wizard.py               # CSV export wizard code
    └── export_wizard_views.xml        # Export wizard form
```

---

## 🛠️ Installation & Execution

### 1. Add Addon Path
Ensure the `transit_ops` folder parent directory is added to your Odoo configuration file (`odoo.conf`):
```ini
addons_path = C:\Program Files\Odoo 17.0\server\odoo\addons,c:\Users\sk600\Downloads\oddo
```

### 2. Launch / Update Module
Start the Odoo server using your command line to install the TransitOps module:
```powershell
& "C:\Program Files\Odoo 17.0\python\python.exe" "C:\Program Files\Odoo 17.0\server\odoo-bin" -c "c:\Users\sk600\Downloads\oddo\odoo.conf" -d transitops -i transit_ops
```

Once running, access the application in your browser at: **`http://localhost:8070`**

---

## 🧪 Testing and Verification

To test the security groups and access restrictions, sign in with one of the pre-loaded demo users:

*   **Driver User**:
    *   **Login**: `dispatcher@transitops.com` | **Password**: `dispatcher`
*   **Safety Officer User**:
    *   **Login**: `safety@transitops.com` | **Password**: `safety`
*   **Financial Analyst User**:
    *   **Login**: `finance@transitops.com` | **Password**: `finance`
*   **Fleet Manager User**:
    *   **Login**: `manager@transitops.com` | **Password**: `manager`

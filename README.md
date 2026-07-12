# 🚛 TransitOps - Smart Transport Operations Platform

> An end-to-end transport management solution built on **Odoo 17** for the **Odoo Hackathon**.

![Odoo](https://img.shields.io/badge/Odoo-17-purple)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

TransitOps is a centralized fleet and transport operations platform that digitizes the complete transportation lifecycle.

The platform eliminates manual fleet management by automating vehicle allocation, driver assignment, maintenance scheduling, fuel tracking, operational expenses, and business analytics while enforcing strict business rules.

Built during the **8-hour Odoo Hackathon**, the solution focuses on operational efficiency, compliance, and data-driven decision making.

---

## 🎯 Problem Statement

Many transport companies still rely on spreadsheets and manual logs, resulting in:

- Vehicle scheduling conflicts
- Driver compliance issues
- Missed maintenance
- Poor fleet utilization
- Hidden operational costs
- Lack of operational visibility

TransitOps solves these problems through an integrated ERP-based transport management system.

---

# ✨ Features

## 🔐 Authentication & Security

- Secure Odoo Authentication
- Role-Based Access Control (RBAC)
- User Permissions
- Protected Modules

---

## 🚚 Vehicle Management

- Vehicle Registration
- Unique Registration Validation
- Vehicle Status Tracking
- Capacity Management
- Odometer Tracking
- Acquisition Cost Tracking

Vehicle Status:

- Available
- On Trip
- In Shop
- Retired

---

## 👨‍✈️ Driver Management

- Driver Profiles
- License Management
- License Expiry Validation
- Safety Score
- Contact Information
- Driver Availability

Driver Status:

- Available
- On Trip
- Off Duty
- Suspended

---

## 📦 Trip Management

- Trip Creation
- Vehicle Assignment
- Driver Assignment
- Cargo Validation
- Distance Tracking
- Revenue Tracking
- Automatic Workflow

Trip Lifecycle

```
Draft
   ↓
Dispatched
   ↓
Completed

or

Draft
   ↓
Cancelled
```

---

## 🔧 Maintenance Management

- Maintenance Logs
- Service History
- Vehicle Availability Control
- Automatic Status Updates

---

## ⛽ Fuel & Expense Tracking

- Fuel Logs
- Toll Expenses
- Maintenance Expenses
- Operational Cost Calculation

---

## 📊 Dashboard

Real-time KPIs including

- Active Vehicles
- Available Vehicles
- Vehicles In Shop
- Active Trips
- Drivers On Duty
- Fleet Utilization
- Fuel Efficiency
- Operational Cost
- Vehicle ROI

---

## 📈 Reports & Analytics

- Fleet Utilization
- Fuel Efficiency
- Operational Cost
- Vehicle ROI
- CSV Export
- Business Insights

---

# ⚙️ Business Rules

TransitOps strictly enforces the following validations:

- ✅ Unique Vehicle Registration Number
- ✅ Prevent Dispatch of Retired Vehicles
- ✅ Prevent Dispatch of Vehicles in Maintenance
- ✅ Prevent Duplicate Vehicle Assignment
- ✅ Prevent Duplicate Driver Assignment
- ✅ License Expiry Validation
- ✅ Suspended Drivers Cannot Be Assigned
- ✅ Cargo Weight Validation
- ✅ Automatic Status Transitions
- ✅ Data Integrity

---

# 🛠️ Technology Stack

| Layer | Technology |
|--------|------------|
| ERP | Odoo 17 |
| Backend | Python |
| ORM | Odoo ORM |
| Frontend | OWL, XML, QWeb |
| Database | PostgreSQL |
| UI | Bootstrap |
| Charts | Chart.js |

---

# 📂 Project Structure

```
transitops/

├── models/
├── views/
├── security/
├── reports/
├── data/
├── static/
├── wizard/
├── controllers/
├── __manifest__.py
├── __init__.py
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Nura730/Transitops.git
```

Copy the module into your custom addons directory.

Update the addons path inside `odoo.conf`.

Restart Odoo.

Update Apps List.

Install **TransitOps**.

---

# 🧪 Demo Workflow

1. Register a Vehicle
2. Register a Driver
3. Create a Trip
4. Assign Vehicle & Driver
5. Dispatch Trip
6. Complete Trip
7. Log Fuel Expense
8. Create Maintenance Record
9. View Dashboard Analytics
10. Export Reports

---

# 👥 Team

| Name | Responsibility |
|------|----------------|
| Arun S | Frontend Development, Integration, Git Management |
| Mathesh | Backend Development |
| Sunil | Frontend Development |
| Madhan | Documentation, Testing & Reports |

---

# 🎯 Hackathon Deliverables

- Responsive Web Interface
- Authentication with RBAC
- Vehicle CRUD
- Driver CRUD
- Trip Management
- Automatic Status Workflow
- Maintenance Workflow
- Fuel & Expense Tracking
- Dashboard with KPIs
- Reports & Analytics
- CSV Export

---

# 📌 Future Enhancements

- AI Route Optimization
- Predictive Maintenance
- Email Notifications
- Vehicle Document Management
- Mobile Application
- GPS Integration
- Live Vehicle Tracking

---

# 📄 License

This project was developed exclusively for the **Odoo Hackathon** as a proof-of-concept transport operations platform.

---

## ⭐ If you like this project, consider giving the repository a Star!
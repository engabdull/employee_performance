# Employee Performance App Guide

## Overview
The **Employee Performance** app provides a comprehensive dashboard within Frappe to monitor and analyze employee productivity, CRM activities, and HR attendance in real-time. It aggregates data from multiple modules to provide a holistic view of performance.

---

## Installation & Setup

To install the Employee Performance app on your Frappe environment, follow these steps:

### 1. Get the App
```bash
bench get-app https://github.com/[your-repo]/employee_performance.git
```

### 2. Install the App
```bash
bench --site [your-site-name] install-app employee_performance
```

### 3. Build Assets
```bash
bench build --app employee_performance
```

### 4. Migrate Site
```bash
bench --site [your-site-name] migrate
```

---

## Process Cycle
The app operates on a **Pull-and-Aggregate** cycle:
1.  **User Selection**: The dashboard is filtered by a specific **Employee**.
2.  **Date Range**: Data is fetched based on a selected date range (defaulting to the current month).
3.  **Data Retrieval**: The system executes optimized SQL and ORM queries across CRM (Leads, Opportunities, Invoices), HR (Attendance, Check-ins), and custom DocTypes.
4.  **Display**: The results are visualized through KPIs and interactive charts (ApexCharts).

---

## Statistics & DocTypes Reference

The dashboard pulls statistics from the following DocTypes based on specific filtering logic:

| Statistic | DocType | Primary Filter (Qualified By) | Date Field | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Total Leads** | `Lead` | `qualified_by` (User ID) | `qualified_on` | Counts leads qualified by the employee. |
| **Opportunities** | `Opportunity` | `opportunity_owner` (User ID) | `creation` | Counts opportunities owned by the employee. |
| **Active Customers** | `Customer` | `l.qualified_by` (Via Lead) | `l.creation` | Distinct customers linked to leads qualified by the employee. |
| **Sales Invoices** | `Sales Invoice` | `owner` (User ID) | `posting_date` | Invoices created by the employee. |
| **Attendance Stats** | `tabAttendance` | `employee` (Employee ID) | `attendance_date` | Present, Absent, and Half-Day counts. |
| **Daily Reports** | `Daily Employee Report`| `employee` (Employee ID) | `date` | Total count of daily reports submitted. |
| **Appointments** | `Appointment` | `custom_qualified_by` (Emp ID) | `scheduled_time` | Total appointments qualified/scheduled. |
| **Activity Events** | `Event` | `custom_own` (Employee ID) | `starts_on` | Categorized events (Calls, Meetings, Emails). |
| **Total Tasks** | `Task` | `custom_assign_to` (User ID)| `creation` | Tasks assigned to the employee. |

---

## Filtering Logic

The dashboard uses two main identifiers for filtering:
1.  **User ID**: Used for DocTypes where the link is via the System User (e.g., `Lead`, `Opportunity`, `Sales Invoice`, `Task`).
2.  **Employee ID**: Used for HR-related DocTypes (e.g., `Attendance`, `Employee Checkin`, `Daily Employee Report`).

### Key Performance Filters:
-   **Qualified By**: Most CRM metrics are driven by the `qualified_by` field in the `Lead` DocType, which determines the "Owner" of the conversion.
-   **Conversion Rate**: Calculated as `(Active Customers / Total Leads) * 100`.
-   **Leads Pulse**: Tracks the count of qualified leads per day to show activity trends.

---

## AI Re-creation Prompt
*If you need to recreate this dashboard or build a similar one on a new site, you can use the prompt below with an AI assistant:*

> **Prompt:**
> "I need to build an 'Employee Performance Dashboard' app for Frappe. 
> 
> **Core Requirements:**
> 1. **Page**: Create a Frappe Page named `employee_performance`.
> 2. **Data Model**: The dashboard must aggregate data from:
>    - **CRM**: `Lead` (filtered by `qualified_by`), `Opportunity` (by `opportunity_owner`), `Sales Invoice` (by `owner`).
>    - **HR**: `Attendance`, `Employee Checkin` (both filtered by `employee` ID).
>    - **Custom Docs**: `Daily Employee Report`, `Appointment` (by `custom_qualified_by`), `Event` (by `custom_own`).
> 3. **UI Components**:
>    - Header with **Employee Filter** and **Date Range Picker**.
>    - **KPI Cards** for Total Leads, Conversion Rate (Active Customers / Total Leads), and Daily Report counts.
>    - **Charts (ApexCharts)**:
>      - Lead Pulse (daily trend of qualified leads).
>      - Activity Distribution (Calls, Meetings, Emails, Events).
>      - Attendance Breakdown (Present, Absent, Half-Day).
>    - **Live Feeds**: List of recent Employee Check-ins.
> 4. **API Strategy**: Implement a Whitelisted Python method `get_employee_dashboard` that accepts `employee` and `date_range` and returns a structured JSON for the frontend."

---

## Developer Notes
-   The main dashboard logic is located in: `apps/employee_performance/employee_performance/page/employee_performance/employee_performance.py`
-   The frontend UI is built using **Frappe Page** with **ApexCharts** for data visualization.
-   Custom fields (e.g., `custom_qualified_by`, `custom_own`, `custom_assign_to`) must exist in their respective DocTypes for full functionality.

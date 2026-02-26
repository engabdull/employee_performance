# Employee Performance Dashboard

A comprehensive performance tracking and analytics dashboard for Frappe/ERPNext, designed to give managers and employees a clear view of their productivity, CRM activity, and attendance.

## 🚀 Key Features

### 1. CRM Performance Analytics
* **Leads Tracking:** Total Leads assigned to the employee for the selected period.
* **Leads Pulse:** A daily distribution chart showing when leads are being created and assigned.
* **Conversion Metrics:** Track Opportunities, Customers converted from leads, and the overall Conversion Rate percentage.

### 2. Activity & Engagement
* **Monthly Activity Chart:** Visual breakdown of employee engagement including:
    * **Calls** (logged via Events)
    * **Meetings**
    * **General Events** (Public/Private)
* **Appointments:** Total count of scheduled appointments with customers.

### 3. HR & Productivity
* **Attendance Overview:** Digital donut chart showing Present vs. Absent vs. Half Day distribution.
* **Daily Employee Reports:** Integration with Daily Report doctype to track summaries of work done.
* **Task Completion:** Visual gauge or count of Pending vs. Completed tasks.

### 4. Interactive Dashboard
* **Dynamic Employee Selector:** Switch between different employees to view their specific data.
* **Automatic Period Sync:** The dashboard defaults to showing the previous full month's data (e.g., if today is Feb 26, it shows January).

## 🛠 Technical Architecture

* **Frontend:** Built with vanilla JavaScript, Chart.js for data visualization, and Frappe's Page API.
* **Backend:** Python-based API in `employee_performance.py` using optimized SQL queries for high-speed data retrieval.
* **Data Sources:** Integrates data from standard DocTypes:
    * `Lead`, `Opportunity`, `Customer`
    * `Event`, `Appointment`, `Task`
    * `Attendance`, `Daily Employee Report`

## 📊 Data Mapping
The app expects the following fields for accurate tracking:
* **Leads/Opps:** Filtered by `owner` or `lead_owner`.
* **Events:** Filtered by `owner` and categorized by `event_type` (Call, Meeting, etc.).
* **Attendance:** Filtered by the `employee` link and `attendance_date`.

## 🧪 Test Data Generator
The app includes a powerful utility for developers to populate the dashboard with realistic data.
* **Script:** `create_test_dashboard_data.py`
* **Command:** `bench execute frappe.utils.create_test_dashboard_data.create_test_data`
* **Features:**
    * Automatically handles joining date validations.
    * Generates weighted random data for Leads, Opps, Tasks, and Events.
    * Correctly maps data ownership to specific employee emails.

---
*Created for Mohammedkh97 - Employee Performance Analytics*

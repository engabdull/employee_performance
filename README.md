# Employee Performance Dashboard

A robust, real-time performance analytics dashboard for Frappe and ERPNext. This app provides managers and employees with a visual overview of CRM activity, HR attendance, and overall productivity.

## 🚀 Key Features

*   **CRM Analytics:** Real-time tracking of Leads, Opportunities, and Customer conversions.
*   **Activity Pulse:** Daily distribution charts showing lead assignments and engagement.
*   **Engagement Tracking:** Visual breakdown of Calls, Meetings, and Events.
*   **HR Integration:** Integrated Attendance monitoring (Present vs. Absent) and Daily Work Reports.
*   **Multi-Employee Support:** Dynamic selector to switch views between different employees.
*   **Intelligent Period Sync:** Automatically targets the previous full month (e.g., in February, it shows January).

---

## 📂 File Architecture & Technical Details

The app is built using Frappe's **Page API**. Below is a breakdown of the core files and their responsibilities:

### 1. `employee_performance.py` (Backend)
*   **Role:** The "Brain" of the dashboard.
*   **Logic:** Handles all SQL queries to the Frappe database (`tabLead`, `tabEvent`, `tabAttendance`, etc.).
*   **Key Functions:**
    *   Calculates date ranges for the target month.
    *   Performs data aggregation (sums, counts, averages).
    *   Explicitly type-casts data (e.g., `int()`) to ensure compatibility with JSON and frontend charts.
    *   Implements role-based filtering (filters data by `owner` or `employee_id`).

### 2. `employee_performance.js` (Frontend)
*   **Role:** The "Interface & Controller".
*   **Logic:** Manages the User Interface, handles the Employee selector, and renders all charts.
*   **Technology:** Uses **Chart.js** for visualizations.
*   **Responsibilities:**
    *   Fetches data from the Python backend via `frappe.call`.
    *   Dynamic DOM manipulation (updates cards, headers, and text).
    *   Chart Initialization: Configures colors, tooltips, and responsive behavior for the donut, bar, and pulse charts.

### 3. `employee_performance.json` (Configuration)
*   **Role:** The "App Definition".
*   **Metadata:** This file registers the page within the Frappe framework.
*   **Links:** It tells Frappe that the Page is named "Employee Performance" and points it to the associated `.js` and `.py` files.

### 4. `employee_performance.css` (Styling)
*   **Role:** The "Aesthetics".
*   **Logic:** Provides custom styling for the dashboard layout.
*   **Features:**
    *   Modern card layouts with shadows and hover effects.
    *   Custom color tokens for attendance (Green/Red) and activity charts.
    *   Responsive grid system to ensure the dashboard looks good on all screen sizes.

### 5. `create_test_dashboard_data.py` (Utility)
*   **Role:** High-speed data generator for testing.
*   **Logic:** Programmatically creates Lead, Event, Task, and Attendance records.
*   **Features:** Respects employee joining dates and prevents validation errors.

---

## 📦 Installation Guide (GitHub)

Follow these steps to install this app on a new Frappe/ERPNext server.

### 1. Requirements
*   A working Frappe Bench environment.
*   ERPNext (optional, but required for Lead/Opportunity metrics).
*   HRMS (optional, but required for Attendance metrics).

### 2. Download and Install
Run these commands in your `frappe-bench` directory:

```bash
# 1. Download the app from your GitHub
bench get-app https://github.com/KareemTarekAnwerHelmy/Employee-Performance.git

# 2. Install the app on your specific site
bench --site [your-site-name] install-app employee_performance

# 3. Build the frontend assets
bench build --app employee_performance

# 4. Restart the bench to apply changes
bench restart
```

*(Note: If using Docker, run the bench commands inside the backend container & restart the container)*

---

## 🛠 Usage & Verification
1.  Navigate to **Employee Performance** in the Frappe search bar.
2.  Select an employee from the dropdown.
3.  **Pro Tip:** If you don't see data immediately, perform a **Hard Refresh (Ctrl + Shift + R)** to clear the browser cache.

---
*Developed for Mohammedkh97 — Modern Employee Analytics*

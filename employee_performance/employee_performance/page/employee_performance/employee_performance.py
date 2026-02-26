import frappe
from frappe import _
from datetime import date, timedelta
import calendar


def get_context(context):
    pass


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _get_month_number(month):
    if str(month).isalpha():
        month_map = {
            "January": 1, "February": 2, "March": 3,
            "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9,
            "October": 10, "November": 11, "December": 12
        }
        return month_map.get(str(month).capitalize(), 1)
    return int(month)


def _get_date_range(month, year):
    month = _get_month_number(month)
    year = int(year)
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    return start_date, end_date


def _get_user_from_employee(employee):
    return frappe.db.get_value("Employee", employee, "user_id")


# ---------------------------------------------------------
# MAIN KPI API
# ---------------------------------------------------------

@frappe.whitelist()
def get_employee_dashboard(employee):
    if not employee:
        frappe.throw(_("Employee is required"))
    today = date.today()
    first_day_current = today.replace(day=1)
    last_month_end   = first_day_current - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    user_id = _get_user_from_employee(employee)

    response = {
        "crm": {
            "total_leads": 0,
            "total_opportunities": 0,
            "active_customers": 0,
            "conversion_rate": 0,
            "total_lead_trend": 0,
            "new_leads_month": 0,
            "daily_leads": 0,
            "sales_invoices": 0
        },
        "hr": {
            "present_days": 0,
            "absent_days": 0,
            "total_checkins": 0,
            "total_checkouts": 0,
            "recent_checkins": []
        },
        "visitor": {
            "total": 0,
            "daily": 0,
            "client": 0,
            "interview": 0
        },
        "daily_report": 0,
        "appointments": {
            "total": 0
        },
        "events_chart": {
            "labels": [],
            "values": []
        },
        "attendance_chart": {
            "labels": [_("Present"), _("Absent"), _("Half Day")],
            "values": [0, 0, 0]
        },
        "leads_pulse": {
            "labels": [],
            "values": []
        },
        "checkin_chart": {
            "labels": [],
            "values": []
        },
        "total_task": 0
    }

    if not user_id:
        # frappe.log_error(f"EPD: No user_id found for employee {employee}", "Employee Performance Dashboard")
        return response

    # Datetime upper bound — captures the full last day
    upper_bound = last_month_end + timedelta(days=1)

    # ------------------------------------------------------------------
    # CRM — Total Leads (Last Month)
    # ------------------------------------------------------------------
    total_leads = frappe.db.count("Lead", {
        "lead_owner": user_id,
        "creation": ["between", [last_month_start, upper_bound]]
    })
    response["crm"]["total_leads"] = total_leads

    # ------------------------------------------------------------------
    # CRM — Opportunities (Last Month)
    # ------------------------------------------------------------------
    response["crm"]["total_opportunities"] = frappe.db.count("Opportunity", {
        "opportunity_owner": user_id,
        "creation": ["between", [last_month_start, upper_bound]]
    })

    # ------------------------------------------------------------------
    # CRM — Sales Invoices (Last Month)
    # ------------------------------------------------------------------
    if frappe.db.exists("DocType", "Sales Invoice"):
        response["crm"]["sales_invoices"] = frappe.db.count("Sales Invoice", {
            "owner": user_id,
            "posting_date": ["between", [last_month_start, last_month_end]]
        })

    # ------------------------------------------------------------------
    # CRM — Active Customers converted from leads (Last Month)
    # ------------------------------------------------------------------
    active_customers = frappe.db.sql("""
        SELECT COUNT(DISTINCT c.name)
        FROM `tabCustomer` c
        JOIN `tabLead` l ON l.customer = c.name
        WHERE l.lead_owner = %s
          AND c.disabled = 0
          AND l.creation BETWEEN %s AND %s
    """, (user_id, last_month_start, upper_bound))[0][0] or 0
    response["crm"]["active_customers"] = active_customers

    if total_leads > 0:
        response["crm"]["conversion_rate"] = round(
            (active_customers / total_leads) * 100, 2
        )

    # ------------------------------------------------------------------
    # Leads Pulse Chart (Daily distribution for last month)
    # ------------------------------------------------------------------
    leads_data = frappe.db.sql("""
        SELECT DATE(creation) AS d, COUNT(*) AS cnt
        FROM `tabLead`
        WHERE lead_owner = %s
          AND creation BETWEEN %s AND %s
        GROUP BY DATE(creation)
        ORDER BY DATE(creation)
    """, (user_id, last_month_start, upper_bound), as_dict=True)

    pulse_map = {}
    for row in leads_data:
        d_val = row.get("d")
        if d_val:
            # Use frappe.utils.getdate to handle various date-like objects
            d_str = str(frappe.utils.getdate(d_val))
            pulse_map[d_str] = int(row.get("cnt") or 0)

    num_days     = (last_month_end - last_month_start).days + 1
    pulse_labels = []
    pulse_values = []
    for i in range(num_days):
        d_obj = last_month_start + timedelta(days=i)
        d_str = d_obj.strftime("%Y-%m-%d")
        pulse_labels.append(d_str)
        pulse_values.append(pulse_map.get(d_str, 0))

    response["leads_pulse"]["labels"] = pulse_labels
    response["leads_pulse"]["values"] = pulse_values

    # ------------------------------------------------------------------
    # HR & Attendance (Last Month)
    # FIX: docstatus IN (0, 1) — include both draft and submitted records
    # so attendance shows even when records haven't been formally submitted.
    # ------------------------------------------------------------------
    attendance_stats_list = frappe.db.sql("""
        SELECT
            SUM(CASE WHEN status IN ('Present', 'Work From Home') THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status = 'Absent'   THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN status = 'Half Day' THEN 1 ELSE 0 END) AS half_day
        FROM `tabAttendance`
        WHERE employee = %s
          AND docstatus IN (0, 1)
          AND attendance_date BETWEEN %s AND %s
    """, (employee, last_month_start, last_month_end), as_dict=True)

    attendance_stats = attendance_stats_list[0] if attendance_stats_list else {}

    response["hr"]["present_days"] = int(attendance_stats.get("present") or 0)
    response["hr"]["absent_days"]  = int(attendance_stats.get("absent")  or 0)
    response["attendance_chart"]["values"] = [
        int(attendance_stats.get("present")  or 0),
        int(attendance_stats.get("absent")   or 0),
        int(attendance_stats.get("half_day") or 0)
    ]

    # ------------------------------------------------------------------
    # Daily Employee Report Integration (Last Month)
    # ------------------------------------------------------------------
    reports = frappe.db.get_all(
        "Daily Employee Report",
        filters={
            "employee": employee,
            "date": ["between", [last_month_start, last_month_end]]
        },
        fields=["date", "daily_summary"],
        order_by="date desc",
        limit=20
    )

    response["daily_report"] = frappe.db.count("Daily Employee Report", {
        "employee": employee,
        "date": ["between", [last_month_start, last_month_end]]
    })

    response["hr"]["recent_checkins"] = [
        {
            "time": r.get("date"),
            "log_type": "REPORT",
            "device_id": r.get("daily_summary")
        }
        for r in reports
    ]

    # ------------------------------------------------------------------
    # Appointments (Last Month)
    # ------------------------------------------------------------------
    response["appointments"]["total"] = frappe.db.count("Appointment", {
        "owner": user_id,
        "scheduled_time": ["between", [last_month_start, upper_bound]]
    })

    # ─────────────────────────────────────────────────────
    # Events Chart — Activity Distribution (Last Month)
    # ─────────────────────────────────────────────────────
    categories  = ["Call", "Meeting", "Event", "Other"]
    counts_map  = {cat: 0 for cat in categories}

    events_filters = {
        "starts_on": ["between", [last_month_start, upper_bound]]
    }
    # Check for employee field (custom or site-specific)
    if frappe.db.has_column("Event", "employee"):
        events_filters["employee"] = employee
    else:
        events_filters["owner"] = user_id

    event_counts = frappe.db.get_list("Event", filters=events_filters, fields=["event_type", "count(*) as cnt"], group_by="event_type")

    for row in event_counts:
        etype = (row.get("event_type") or "").strip()
        cnt   = int(row.get("cnt") or 0)

        if etype == "Call":
            counts_map["Call"] += cnt
        elif etype == "Meeting":
            counts_map["Meeting"] += cnt
        elif etype in ("Public", "Private", "Event"):
            counts_map["Event"] += cnt
        else:
            counts_map["Other"] += cnt

    response["events_chart"]["labels"] = categories
    response["events_chart"]["values"] = [counts_map[cat] for cat in categories]

    # ------------------------------------------------------------------
    # Total Tasks (Last Month)
    # ------------------------------------------------------------------
    if frappe.db.exists("DocType", "Task"):
        response["total_task"] = frappe.db.count("Task", {
            "owner": user_id,
            "creation": ["between", [last_month_start, upper_bound]]
        })

    return response


# ---------------------------------------------------------
# EVENTS CHART API
# ---------------------------------------------------------
# Removed obsolete get_events_by_category in favour of unified get_employee_dashboard
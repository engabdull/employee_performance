import frappe
from frappe import _
from datetime import date, timedelta
import calendar


def get_context(context):
    pass


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _parse_date(val, fallback):
    """Return a date object from val, or fallback if val is absent/invalid."""
    if not val:
        return fallback
    try:
        return frappe.utils.getdate(val)
    except Exception:
        return fallback


def _resolve_date_range(from_date_raw, to_date_raw):
    """
    Resolve the from / to dates supplied by the caller.
    Defaults: from_date = first day of current month, to_date = today.
    """
    today = date.today()
    default_from = date(today.year, today.month, 1)
    default_to   = today

    from_date = _parse_date(from_date_raw, default_from)
    to_date   = _parse_date(to_date_raw,   default_to)

    # Sanity: from must not be after to
    if from_date > to_date:
        from_date, to_date = to_date, from_date

    return from_date, to_date


def _get_user_from_employee(employee):
    return frappe.db.get_value("Employee", employee, "user_id")


# ---------------------------------------------------------
# MAIN KPI API
# ---------------------------------------------------------

@frappe.whitelist()
def get_employee_dashboard(employee, from_date=None, to_date=None):
    if not employee:
        frappe.throw(_("Employee is required"))

    start_date, end_date = _resolve_date_range(from_date, to_date)
    upper_bound = end_date + timedelta(days=1)

    user_id = frappe.db.get_value("Employee", employee, "user_id")
    employee_name = frappe.db.get_value("Employee", employee, "employee_name") or employee

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
        "total_task": 0,
        "date_range": {
            "from_date": str(start_date),
            "to_date": str(end_date)
        }
    }

    if not user_id:
        return response

    # ------------------------------------------------------------------
    # CRM — Total Leads (Using qualified_on)
    # ------------------------------------------------------------------
    total_leads = frappe.db.count("Lead", {
        "qualified_by": user_id,
        "qualified_on": ["between", [start_date, end_date]]
    })
    response["crm"]["total_leads"] = total_leads

    # ------------------------------------------------------------------
    # CRM — Opportunities
    # ------------------------------------------------------------------
    response["crm"]["total_opportunities"] = frappe.db.count("Opportunity", {
        "opportunity_owner": user_id,
        "creation": ["between", [start_date, upper_bound]]
    })

    # ------------------------------------------------------------------
    # CRM — Sales Invoices
    # ------------------------------------------------------------------
    if frappe.db.exists("DocType", "Sales Invoice"):
        response["crm"]["sales_invoices"] = frappe.db.count("Sales Invoice", {
            "owner": user_id,
            "posting_date": ["between", [start_date, end_date]]
        })

    # ------------------------------------------------------------------
    # CRM — Active Customers (From Lead field)
    # ------------------------------------------------------------------
    active_customers = frappe.db.sql("""
        SELECT COUNT(DISTINCT c.name)
        FROM `tabCustomer` c
        JOIN `tabLead` l ON c.lead_name = l.name
        WHERE l.qualified_by = %s
          AND c.disabled = 0
          AND l.creation BETWEEN %s AND %s
    """, (user_id, start_date, upper_bound))[0][0] or 0
    response["crm"]["active_customers"] = active_customers

    if total_leads > 0:
        response["crm"]["conversion_rate"] = round(
            (active_customers / total_leads) * 100, 2
        )

    # ------------------------------------------------------------------
    # Leads Pulse Chart (Using qualified_on for activity date)
    # ------------------------------------------------------------------
    leads_data = frappe.db.sql("""
        SELECT qualified_on AS d, COUNT(*) AS cnt
        FROM `tabLead`
        WHERE qualified_by = %s
          AND qualified_on BETWEEN %s AND %s
        GROUP BY qualified_on
        ORDER BY qualified_on
    """, (user_id, start_date, end_date), as_dict=True)

    pulse_map = {}
    for row in leads_data:
        d_val = row.get("d")
        if d_val:
            d_str = str(frappe.utils.getdate(d_val))
            pulse_map[d_str] = int(row.get("cnt") or 0)

    num_days     = (end_date - start_date).days + 1
    pulse_labels = []
    pulse_values = []
    for i in range(num_days):
        d_obj = start_date + timedelta(days=i)
        d_str_full = d_obj.strftime("%Y-%m-%d")
        d_str_disp = d_obj.strftime("%d-%m")
        pulse_labels.append(d_str_disp)
        pulse_values.append(pulse_map.get(d_str_full, 0))

    response["leads_pulse"]["labels"] = pulse_labels
    response["leads_pulse"]["values"] = pulse_values

    # ------------------------------------------------------------------
    # HR & Attendance
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
    """, (employee, start_date, end_date), as_dict=True)

    attendance_stats = attendance_stats_list[0] if attendance_stats_list else {}

    response["hr"]["present_days"] = int(attendance_stats.get("present") or 0)
    response["hr"]["absent_days"]  = int(attendance_stats.get("absent")  or 0)
    response["attendance_chart"]["values"] = [
        int(attendance_stats.get("present")  or 0),
        int(attendance_stats.get("absent")   or 0),
        int(attendance_stats.get("half_day") or 0)
    ]

    # ------------------------------------------------------------------
    # Daily Employee Report (Count Only)
    # ------------------------------------------------------------------
    response["daily_report"] = frappe.db.count("Daily Employee Report", {
        "employee": employee,
        "date": ["between", [start_date, end_date]]
    })

    # ------------------------------------------------------------------
    # Recent Activity Log: Employee Checkin (IN/OUT)
    # ------------------------------------------------------------------
    checkins = frappe.db.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [start_date, upper_bound]]
        },
        fields=["time", "log_type"],
        order_by="time desc",
        limit=20
    )

    response["hr"]["recent_checkins"] = [
        {
            "time": r.get("time"),
            "log_type": r.get("log_type"),
            "device_id": _("Check {0}").format(r.get("log_type"))
        }
        for r in checkins
    ]

    # ------------------------------------------------------------------
    # Appointments (custom_qualified_by = employee ID)
    # ------------------------------------------------------------------
    response["appointments"]["total"] = frappe.db.count("Appointment", {
        "custom_qualified_by": employee,
        "scheduled_time": ["between", [start_date, upper_bound]]
    })

    # ------------------------------------------------------------------
    # Events Chart (custom_own = employee ID)
    # ------------------------------------------------------------------
    categories  = ["Call", "Meeting", "Sent/Received Email", "Event", "Other"]
    counts_map  = {cat: 0 for cat in categories}

    events_filters = {
        "custom_own": employee,
        "starts_on": ["between", [start_date, upper_bound]]
    }

    events = frappe.get_all(
        "Event",
        filters=events_filters,
        fields=["event_category"]
    )

    for row in events:
        etype = (row.get("event_category") or "").strip()
        cnt = 1
        if etype == "Call":
            counts_map["Call"] += cnt
        elif etype == "Meeting":
            counts_map["Meeting"] += cnt
        elif etype == "Sent/Received Email":
            counts_map["Sent/Received Email"] += cnt
        elif etype in ("Public", "Private", "Event"):
             counts_map["Event"] += cnt
        else:
             counts_map["Other"] += cnt

    response["events_chart"]["labels"] = categories
    response["events_chart"]["values"] = [counts_map[cat] for cat in categories]

    # ------------------------------------------------------------------
    # Total Tasks (custom_assign_to = user_id)
    # ------------------------------------------------------------------
    if frappe.db.exists("DocType", "Task"):
        response["total_task"] = frappe.db.count("Task", {
            "custom_assign_to": user_id,
            "creation": ["between", [start_date, upper_bound]]
        })

    return response
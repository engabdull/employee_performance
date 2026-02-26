"""
Employee Performance Dashboard — Comprehensive Test Data Generator
==================================================================

Creates test data for ALL dashboard fields for LAST MONTH.
Since the dashboard always shows "last month", the script auto-calculates
the correct date range based on today's date.

RUN INSIDE THE DOCKER CONTAINER:
  docker exec -it frappe-production-backend-1 bench --site <site> execute create_test_dashboard_data.create_test_data

=================================================================
DOCTYPE → DASHBOARD FIELD MAPPING
=================================================================

┌──────────────────────────────────┬─────────────────────────────┬─────────────────────────────────────────────┐
│ Dashboard Section / Field        │ DocType                     │ Filter / Key Field                          │
├──────────────────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ KPI: Total Leads                 │ Lead                        │ lead_owner = user_id, creation in range     │
│ KPI: Opportunities               │ Opportunity                 │ opportunity_owner = user_id, creation       │
│ KPI: Customers                   │ Customer                    │ Lead.customer = Customer.name, lead_owner   │
│ KPI: Conversion Rate             │ (computed)                  │ active_customers / total_leads * 100        │
├──────────────────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Chart: Monthly Activity (Call)   │ Event                       │ event_type="Call", owner=user_id            │
│ Chart: Monthly Activity (Meeting)│ Event                       │ event_type="Meeting"                        │
│ Chart: Monthly Activity (Event)  │ Event                       │ owner = user_id, starts_on in range         │
│ Chart: Monthly Activity (Send)   │ Event                       │ event_type="Email", sent_or_received="Sent" │
│ Chart: Monthly Activity (Recv)   │ Event                       │ event_type="Email", sent_or_received="Received"   │
├──────────────────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Chart: Attendance Overview       │ Attendance                  │ employee, docstatus=1, status in range      │
│ Chart: Leads Pulse               │ Lead                        │ (same leads, grouped by DATE(creation))     │
├──────────────────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Table: Total Attendance          │ Attendance                  │ (same as donut Present count)               │
│ Table: Daily Report Count        │ Daily Employee Report       │ employee, date in range                     │
│ Table: Appointments              │ Appointment                 │ owner = user_id, scheduled_time in range    │
│ Table: Total Task                │ Task                        │ owner = user_id, creation in range          │
├──────────────────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ total task                       │task                         │ count total task daily             │
└──────────────────────────────────┴─────────────────────────────┴─────────────────────────────────────────────┘
"""

import frappe
from datetime import date, timedelta, datetime
import random
import calendar


def create_test_data():
    frappe.set_user("Administrator")

    site = frappe.local.site
    print(f"\n{'='*60}")
    print(f"  EMPLOYEE PERFORMANCE — TEST DATA GENERATOR")
    print(f"  Site: {site}")
    print(f"{'='*60}\n")

    # ── Calculate LAST MONTH range (dashboard always shows last month) ──
    today = date.today()
    first_day_current = today.replace(day=1)
    last_month_end = first_day_current - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    num_days = (last_month_end - last_month_start).days + 1

    print(f"  Target period: {last_month_start} → {last_month_end} ({num_days} days)")
    print()

    # ── Target employees ──
    target_emails = [
        "mohamedelnagar@shazmlc.com",
        # Add more employee emails here as needed
    ]

    # Get or create a valid Department
    dept = frappe.db.get_value("Department", {}, "name")
    if not dept:
        try:
            d = frappe.get_doc({"doctype": "Department", "department_name": "General"})
            d.insert(ignore_permissions=True)
            dept = d.name
        except Exception:
            pass

    for email in target_emails:
        emp_ids = frappe.db.get_list("Employee", filters={"user_id": email}, fields=["name"])

        if not emp_ids:
            print(f"  ⚠  Skipping {email} — NO LINKED EMPLOYEE FOUND")
            continue

        for e_rec in emp_ids:
            emp_id = e_rec["name"]
            print(f"  ▶ Processing: {email} → Employee {emp_id}")

            # Ensure department is set
            if dept:
                frappe.db.set_value("Employee", emp_id, "department", dept)

            # ─────────────────────────────────────────────────────
            # 1. LEADS  →  KPI "Total Leads" + Chart "Leads Pulse"
            #    DocType: Lead
            #    Filter:  lead_owner = user_id, creation in range
            # ─────────────────────────────────────────────────────
            print("    [1/9] Lead ...")
            existing_leads = frappe.db.get_list("Lead", filters={"lead_owner": email}, fields=["name"])
            for l_rec in existing_leads:
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                frappe.db.set_value("Lead", l_rec["name"], "creation", f"{d} {random.randint(8,17)}:00:00")

            target_lead_count = 100
            if len(existing_leads) < target_lead_count:
                for i in range(len(existing_leads), target_lead_count):
                    d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                    lead = frappe.get_doc({
                        "doctype": "Lead",
                        "lead_name": f"Test Lead {i+1} for {email}",
                        "lead_owner": email,
                        "status": random.choice(["Open", "Replied", "Opportunity", "Converted"]),
                    })
                    lead.insert(ignore_permissions=True)
                    frappe.db.set_value("Lead", lead.name, "creation", f"{d} {random.randint(8,17)}:00:00")
            print(f"           → {max(len(existing_leads), target_lead_count)} leads in range")

            # ─────────────────────────────────────────────────────
            # 2. OPPORTUNITIES  →  KPI "Opportunities"
            #    DocType: Opportunity
            #    Filter:  opportunity_owner = user_id, creation in range
            # ─────────────────────────────────────────────────────
            print("    [2/9] Opportunity ...")
            existing_opps = frappe.db.get_list("Opportunity", filters={"opportunity_owner": email}, fields=["name"])
            for o_rec in existing_opps:
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                frappe.db.set_value("Opportunity", o_rec["name"], "creation", f"{d} 10:00:00")

            target_opp_count = 50
            if len(existing_opps) < target_opp_count:
                for i in range(len(existing_opps), target_opp_count):
                    d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                    opp = frappe.get_doc({
                        "doctype": "Opportunity",
                        "opportunity_from": "Lead",
                        "opportunity_owner": email,
                        "status": "Open",
                    })
                    try:
                        opp.insert(ignore_permissions=True)
                        frappe.db.set_value("Opportunity", opp.name, "creation", f"{d} 10:00:00")
                    except Exception as e:
                        print(f"           ⚠ Could not create Opportunity: {e}")
                        break
            print(f"           → {max(len(existing_opps), target_opp_count)} opportunities")

            # ─────────────────────────────────────────────────────
            # 3. CUSTOMERS  →  KPI "Customers" + "Conversion Rate"
            #    DocType: Customer + Lead (joined)
            #    Filter:  Lead.customer = Customer.name, lead_owner
            # ─────────────────────────────────────────────────────
            print("    [3/9] Customer (via Lead conversion) ...")
            # Find or create customers linked to leads
            converted_count = 0
            user_leads = frappe.db.get_list("Lead", filters={"lead_owner": email}, fields=["name", "customer"], limit=50) # Get enough to convert 25
            for l_rec in user_leads[:25]:  # Convert first 25 leads
                if l_rec.get("customer"):
                    converted_count += 1
                    continue
                cust_name = f"Test Customer from {l_rec['name']}"
                if not frappe.db.exists("Customer", {"customer_name": cust_name}):
                    try:
                        cust = frappe.get_doc({
                            "doctype": "Customer",
                            "customer_name": cust_name,
                            "customer_group": frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups",
                            "territory": frappe.db.get_value("Territory", {}, "name") or "All Territories",
                        })
                        cust.insert(ignore_permissions=True)
                        frappe.db.set_value("Lead", l_rec["name"], "customer", cust.name)
                        converted_count += 1
                    except Exception as e:
                        print(f"           ⚠ Could not create Customer: {e}")
                else:
                    existing_cust = frappe.db.get_value("Customer", {"customer_name": cust_name}, "name")
                    frappe.db.set_value("Lead", l_rec["name"], "customer", existing_cust)
                    converted_count += 1
            print(f"           → {converted_count} converted leads → customers")

            # ─────────────────────────────────────────────────────
            # 4. ATTENDANCE  →  Donut "Attendance Overview"
            #                   + Table "Total Attendance"
            #    DocType: Attendance
            #    Filter:  employee, docstatus=1, attendance_date in range
            #    Status:  Present / Absent / Half Day
            # ─────────────────────────────────────────────────────
            print("    [4/9] Attendance ...")
            frappe.db.sql(
                "DELETE FROM `tabAttendance` WHERE employee = %s AND attendance_date BETWEEN %s AND %s",
                (emp_id, last_month_start, last_month_end)
            )
            present_count = 0
            absent_count = 0
            half_day_count = 0
            # Ensure 25 days of Attendance as requested
            for i in range(25):
                d = last_month_start + timedelta(days=i)
                # Ensure we don't go into the future
                if d > today:
                    break
                status = "Present"
                present_count += 1

                att = frappe.get_doc({
                    "doctype": "Attendance",
                    "employee": emp_id,
                    "attendance_date": d,
                    "status": status,
                    "docstatus": 1
                })
                att.insert(ignore_permissions=True)
            print(f"           → Present={present_count}, Absent={absent_count}, HalfDay={half_day_count}")

            # ─────────────────────────────────────────────────────
            # 5. DAILY EMPLOYEE REPORT  →  Table "Daily Report Count"
            #                              + "Recent Activity Log"
            #    DocType: Daily Employee Report
            #    Filter:  employee, date in range
            # ─────────────────────────────────────────────────────
            print("    [5/9] Daily Employee Report ...")
            frappe.db.sql(
                "DELETE FROM `tabDaily Employee Report` WHERE employee = %s AND date BETWEEN %s AND %s",
                (emp_id, last_month_start, last_month_end)
            )
            report_count = 0
            summaries = [
                "Completed client follow-ups and updated CRM records.",
                "Attended team meeting. Prepared weekly report.",
                "Site visit to client premises for project review.",
                "Worked on proposal draft and sent for internal review.",
                "Cold calling and prospecting new leads.",
                "Training session on new product features.",
                "Processed purchase orders and coordinated with vendors.",
                "Prepared presentation for upcoming quarterly review.",
                "Resolved customer complaints and escalated issues.",
                "Reviewed project milestones and updated timeline.",
                "Conducted market research for new opportunities.",
                "Coordinated with logistics for shipment tracking.",
            ]
            # Ensure 30 daily reports
            for i in range(30):
                d = last_month_start + timedelta(days=i % num_days)
                if d > today:
                    continue
                rep = frappe.get_doc({
                    "doctype": "Daily Employee Report",
                    "employee": emp_id,
                    "department": dept,
                    "date": d,
                    "daily_summary": random.choice(summaries)
                })
                rep.insert(ignore_permissions=True)
                report_count += 1
            print(f"           → {report_count} daily reports")

            # ─────────────────────────────────────────────────────
            # 6. APPOINTMENTS  →  Table "Appointments"
            #    DocType: Appointment
            #    Filter:  owner = user_id, scheduled_time in range
            # ─────────────────────────────────────────────────────
            print("    [6/9] Appointment ...")
            appt_count = 0
            for i in range(20):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                scheduled = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    appt = frappe.get_doc({
                        "doctype": "Appointment",
                        "scheduled_time": scheduled,
                        "owner": email,
                    })
                    appt.insert(ignore_permissions=True)
                    frappe.db.set_value("Appointment", appt.name, "owner", email)
                    appt_count += 1
                except Exception as e:
                    print(f"           ⚠ Could not create Appointment: {e}")
                    break
            print(f"           → {appt_count} appointments")

            # ─────────────────────────────────────────────────────
            # 8. EVENT (Call, Meeting, Email, General Events)
            #    DocType: Event
            #    Filter:  owner = user_id, starts_on in range
            #    Chart Bars: "Call", "Meeting", "Event", "Send Email", "Receive Email"
            # ─────────────────────────────────────────────────────
            print("    [8/10] Event (Calls, Meetings, Emails, General) ...")
            event_stats = {"Call": 0, "Meeting": 0, "Send Email": 0, "Receive Email": 0, "General": 0}

            # 20 Calls
            for i in range(20):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                starts = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    ev = frappe.get_doc({
                        "doctype": "Event",
                        "subject": f"Call with client #{i+1}",
                        "starts_on": starts,
                        "event_type": "Call",
                        "owner": email,
                    })
                    ev.insert(ignore_permissions=True)
                    frappe.db.set_value("Event", ev.name, "owner", email)
                    event_stats["Call"] += 1
                except Exception as e:
                    print(f"           ⚠ Event (Call): {e}")

            # 18 Meetings
            for i in range(18):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                starts = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    ev = frappe.get_doc({
                        "doctype": "Event",
                        "subject": f"Meeting #{i+1}",
                        "starts_on": starts,
                        "event_type": "Meeting",
                        "owner": email,
                    })
                    ev.insert(ignore_permissions=True)
                    frappe.db.set_value("Event", ev.name, "owner", email)
                    event_stats["Meeting"] += 1
                except Exception as e:
                    print(f"           ⚠ Event (Meeting): {e}")

            # 50 Emails Sent
            for i in range(50):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                starts = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    ev = frappe.get_doc({
                        "doctype": "Event",
                        "subject": f"Email sent #{i+1}",
                        "starts_on": starts,
                        "event_type": "Email",
                        "sent_or_received": "Sent",
                        "owner": email,
                    })
                    ev.insert(ignore_permissions=True)
                    frappe.db.set_value("Event", ev.name, "owner", email)
                    event_stats["Send Email"] += 1
                except Exception as e:
                    pass

            # 50 Emails Received
            for i in range(50):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                starts = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    ev = frappe.get_doc({
                        "doctype": "Event",
                        "subject": f"Email received #{i+1}",
                        "starts_on": starts,
                        "event_type": "Email",
                        "sent_or_received": "Received",
                        "owner": email,
                    })
                    ev.insert(ignore_permissions=True)
                    frappe.db.set_value("Event", ev.name, "owner", email)
                    event_stats["Receive Email"] += 1
                except Exception as e:
                    pass

            # 7.5 General Events
            event_subjects = ["Client review", "Product demo", "Internal sync", "Workshop"]
            for i in range(random.randint(3, 7)):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                starts = datetime.combine(d, datetime.min.time()).replace(hour=random.randint(9, 16))
                try:
                    ev = frappe.get_doc({
                        "doctype": "Event",
                        "subject": f"{random.choice(event_subjects)} #{i+1}",
                        "starts_on": starts,
                        "event_type": random.choice(["Public", "Private"]), # Standard types
                        "owner": email,
                    })
                    ev.insert(ignore_permissions=True)
                    frappe.db.set_value("Event", ev.name, "owner", email)
                    event_stats["General"] += 1
                except Exception as e:
                    print(f"           ⚠ Event (General): {e}")

            print(f"           → Calls={event_stats['Call']}, Mtgs={event_stats['Meeting']}, "
                  f"Sent={event_stats['Send Email']}, Recv={event_stats['Receive Email']}, Gen={event_stats['General']}")

            # ─────────────────────────────────────────────────────
            # 9. TASK  →  Table "Total Task"
            #    DocType: Task
            #    Filter:  owner = user_id, creation in range
            # ─────────────────────────────────────────────────────
            print("    [9/10] Task ...")
            task_count = 0
            task_subjects = ["Follow up with client", "Prepare monthly report", "Draft proposal", "Review code PR"]
            # 15 Tasks
            for i in range(15):
                d = last_month_start + timedelta(days=random.randint(0, num_days - 1))
                try:
                    task = frappe.get_doc({
                        "doctype": "Task",
                        "subject": f"{random.choice(task_subjects)} #{i+1}",
                        "status": random.choice(["Open", "Working", "Completed"]),
                    })
                    task.insert(ignore_permissions=True)
                    # Manually backdate the creation logic to fall into last month
                    frappe.db.set_value("Task", task.name, "creation", f"{d} 10:00:00")
                    frappe.db.set_value("Task", task.name, "owner", email)
                    task_count += 1
                except Exception as e:
                    print(f"           ⚠ Could not create Task: {e}")
                    break
            print(f"           → {task_count} tasks")

            # ─────────────────────────────────────────────────────
            # 10. SALES INVOICE (optional)
            #     DocType: Sales Invoice
            #     Filter:  owner = user_id, posting_date in range
            #     NOTE: Not displayed on charts but tracked in response
            # ─────────────────────────────────────────────────────
            print("    [9/10] Sales Invoice (optional) ...")
            if frappe.db.exists("DocType", "Sales Invoice"):
                print("           → Sales Invoice DocType exists (skipped creation — requires items)")
            else:
                print("           → Sales Invoice DocType not found, skipping")

            print(f"\n  ✅ Done for {email} → {emp_id}\n")

    frappe.db.commit()
    print(f"{'='*60}")
    print(f"  ALL TEST DATA CREATED SUCCESSFULLY!")
    print(f"  Refresh dashboard with Ctrl+Shift+R")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    create_test_data()

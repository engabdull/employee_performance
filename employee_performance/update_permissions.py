import frappe

def get_script_content(reference_doctype, field_name='owner'):
    if reference_doctype == 'Event':
        condition_val = f"1=1 OR {field_name} in ({{val_str}})"
    else:
        condition_val = f"{field_name} in ({{val_str}})"

    return f"""user_roles = frappe.get_roles(user)
if "High Management" in user_roles or "System Manager" in user_roles:
    conditions = ""
else:
    cur_employee = frappe.db.get_value("Employee", {{"user_id": user}}, "name")
    if not cur_employee:
        conditions = "1=2"
    else:
        team_members = []
        to_check = [cur_employee]
        
        while to_check:
            current_emp = to_check.pop(0)
            direct_reports = frappe.db.get_all("Employee", filters={{"reports_to": current_emp}}, pluck="name")
            for dr in direct_reports:
                if dr and dr not in team_members:
                    team_members.append(dr)
                    to_check.append(dr)
        
        team_users = frappe.db.get_all("Employee", filters={{"name": ("in", team_members)}}, pluck="user_id") if team_members else []
        
        allowed_values = list(set([m for m in team_members if m] + [u for u in team_users if u]))
        allowed_values.extend([cur_employee, user])
        allowed_values = list(set([v for v in allowed_values if v]))
        
        if allowed_values:
            val_str = ", ".join(f"'{{v}}'" for v in allowed_values)
            conditions = f"{condition_val}"
        else:
            conditions = "1=2"
"""

def update_or_create(name, doctype, field='owner'):
    script = get_script_content(doctype, field)
    if frappe.db.exists("Server Script", name):
        doc = frappe.get_doc("Server Script", name)
        doc.script = script
        doc.save(ignore_permissions=True)
        print(f"Updated {name}")
    else:
        doc = frappe.new_doc("Server Script")
        doc.name = name
        doc.script_type = "Permission Query"
        doc.reference_doctype = doctype
        doc.script = script
        doc.insert(ignore_permissions=True)
        print(f"Created {name}")

def main():
    update_or_create("Leader Permission - Daily Employee Report", "Daily Employee Report", "employee")
    update_or_create("Leader Permission - Event", "Event", "owner")
    update_or_create("Leader Permission - Appointment", "Appointment", "owner")
    update_or_create("Leader Permission - Lead", "Lead", "owner")
    frappe.db.commit()

if __name__ == "__main__":
    main()

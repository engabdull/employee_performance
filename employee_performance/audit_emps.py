import frappe
def run():
    problem_names = ['Omar Mostafa', 'Hassan Tarek', 'Naeem Adel', 'Aline Bilal', 'Rowan Amin', 'Noor Gamal', 'Mohamed Khalaf']
    results = []
    for n in problem_names:
        # Try finding by name (ID)
        emps = frappe.get_all('Employee', filters={'name': ['like', f'%{n}%']}, fields=['name', 'employee_name', 'user_id'])
        if not emps:
            # Try finding by employee_name
            emps = frappe.get_all('Employee', filters={'employee_name': ['like', f'%{n}%']}, fields=['name', 'employee_name', 'user_id'])
        
        results.append({ 'search': n, 'found': emps })

    for r in results:
        print(f'Search: {r[search]} | Found: {r[found]}')

run()

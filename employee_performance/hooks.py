app_name = "employee_performance"
app_title = "Employee Performance"
app_publisher = "kareem"
app_description = "Employee Performance Dashboard"
app_email = "kareemtarekanwer@gmail.com"
app_license = "mit"

# Load JS and CSS globally so the page controller is registered in the desk
# Remove global hooks to let Frappe page router handle it natively

fixtures = [
    {
        "dt": "Server Script",
        "filters": [
            [
                "name",
                "in",
                [
                    "Leader Permission - Daily Employee Report",
                    "Leader Permission - Event",
                    "Leader Permission - Appointment",
                    "Leader Permission - Lead"
                ]
            ]
        ]
    }
]

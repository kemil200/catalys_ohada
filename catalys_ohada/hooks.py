app_name = "catalys_ohada"
app_title = "C-ERP OHADA"
app_publisher = "Catalys"
app_description = "Referentiel comptable SYSCOHADA revise — module C-ERP"
app_email = "contact@catalys.tg"
app_license = "gpl-3.0"

required_apps = ["frappe/erpnext"]

# Fixtures : Custom Fields et Property Setters propres au referentiel OHADA.
# Vide tant qu'aucune personnalisation n'est livree — voir README.
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["name", "like", "%-catalys_ohada_%"]],
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Catalys OHADA"]],
    },
]

after_install = "catalys_ohada.install.after_install"

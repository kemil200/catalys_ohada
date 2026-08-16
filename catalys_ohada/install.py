# Copyright (c) 2026, Catalys and contributors
# License: GNU General Public License v3. See license.txt

import frappe

from catalys_ohada.syscohada.chart import get_chart_names


def after_install() -> None:
    """Message d'orientation apres ``bench install-app catalys_ohada``.

    Le plan de comptes n'est volontairement PAS applique automatiquement :
    ERPNext le cree a la naissance de la societe, et l'ecraser sur une societe
    existante detruirait un eventuel parametrage. L'application se fait
    explicitement, societe par societe.
    """
    charts = ", ".join(get_chart_names())
    frappe.msgprint(
        frappe._(
            "Catalys OHADA est installe. Plans disponibles : {0}.<br><br>"
            "Pour l'appliquer a une societe vierge :<br>"
            "<code>bench --site &lt;site&gt; execute "
            "catalys_ohada.syscohada.chart.apply_to_company "
            "--kwargs \"{{'company': '&lt;Societe&gt;'}}\"</code>"
        ).format(charts),
        title=frappe._("Catalys OHADA"),
        indicator="green",
    )

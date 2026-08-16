# Copyright (c) 2026, Catalys and contributors
# License: GNU General Public License v3. See license.txt

"""Plan de comptes SYSCOHADA revise.

ERPNext ne decouvre les plans de comptes que dans son propre dossier
``erpnext/accounts/doctype/account/chart_of_accounts/verified/`` : il n'existe
aucun hook permettant a une application tierce d'en enregistrer un. Ce module
contourne la limite en passant l'arbre directement a ``create_charts()`` via son
parametre ``custom_chart``.
"""

import json
import os

import frappe
from frappe import _

CHARTS = {
    "Togo - SYSCOHADA Revise": "tg_syscohada_revise.json",
}


def _data_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "data")


def get_chart_names() -> list[str]:
    """Noms des plans fournis par cette application."""
    return sorted(CHARTS)


def get_chart(chart_name: str = "Togo - SYSCOHADA Revise") -> dict:
    """Retourne l'arbre du plan de comptes, au format attendu par ERPNext."""
    fname = CHARTS.get(chart_name)
    if not fname:
        frappe.throw(_("Plan de comptes inconnu : {0}").format(chart_name))

    with open(os.path.join(_data_dir(), fname), encoding="utf-8") as fh:
        return json.load(fh)["tree"]


@frappe.whitelist()
def apply_to_company(company: str, chart_name: str = "Togo - SYSCOHADA Revise") -> dict:
    """Cree le plan de comptes SYSCOHADA sur une societe existante.

    La societe doit etre vierge de toute ecriture : ERPNext refuse de recreer un
    plan de comptes des qu'un GL Entry existe.
    """
    frappe.only_for("System Manager")

    if not frappe.db.exists("Company", company):
        frappe.throw(_("Societe introuvable : {0}").format(company))

    if frappe.db.exists("GL Entry", {"company": company, "is_cancelled": 0}):
        frappe.throw(
            _("La societe {0} porte deja des ecritures comptables. "
              "Le plan de comptes ne peut plus etre remplace.").format(company)
        )

    existing = frappe.db.count("Account", {"company": company})
    if existing:
        frappe.throw(
            _("La societe {0} possede deja {1} comptes. Supprimez-les avant "
              "d'appliquer le plan SYSCOHADA.").format(company, existing)
        )

    from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
        create_charts,
    )

    create_charts(company, custom_chart=get_chart(chart_name))
    frappe.db.commit()

    return {
        "company": company,
        "chart": chart_name,
        "accounts_created": frappe.db.count("Account", {"company": company}),
    }

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

    _poser_plan(company, chart_name)
    frappe.db.commit()

    return {
        "company": company,
        "chart": chart_name,
        "accounts_created": frappe.db.count("Account", {"company": company}),
    }


def _poser_plan(company: str, chart_name: str) -> None:
    """Cree les comptes puis renseigne les comptes par defaut de la societe.

    ERPNext fait les deux dans ``Company.create_default_accounts()``. En
    appelant ``create_charts()`` directement, on doit reprendre la seconde
    partie a notre charge : sans ``default_receivable_account`` ni
    ``default_payable_account``, la premiere facture echoue.
    """
    from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
        create_charts,
    )

    frappe.local.flags.ignore_root_company_validation = True
    create_charts(company, custom_chart=get_chart(chart_name))

    for champ, type_compte in (
        ("default_receivable_account", "Receivable"),
        ("default_payable_account", "Payable"),
    ):
        compte = frappe.db.get_value(
            "Account", {"company": company, "account_type": type_compte, "is_group": 0}
        )
        if compte:
            frappe.db.set_value("Company", company, champ, compte)


@frappe.whitelist()
def creer_societe(
    company_name: str,
    country: str,
    abbr: str | None = None,
    chart_name: str = "Togo - SYSCOHADA Revise",
) -> dict:
    """Cree une societe portant directement le plan SYSCOHADA.

    Une societe ERPNext genere son plan de comptes a l'insertion. Le drapeau
    ``ignore_chart_of_accounts`` — que ``Company.on_update()`` teste avant
    d'appeler ``create_default_accounts()`` — permet de l'en empecher, puis de
    poser le notre a la place. C'est la seule facon d'obtenir une societe
    SYSCOHADA sans passer par une creation puis une suppression de comptes.
    """
    frappe.only_for("System Manager")

    if frappe.db.exists("Company", company_name):
        frappe.throw(_("La societe {0} existe deja.").format(company_name))

    from catalys_ohada.syscohada.pays import devise_du_pays

    devise = devise_du_pays(country)
    if not devise:
        frappe.throw(_("{0} n'est pas un Etat partie a l'OHADA.").format(country))

    frappe.local.flags.ignore_chart_of_accounts = True
    try:
        societe = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": company_name,
                "abbr": abbr or "".join(m[0] for m in company_name.split()[:3]).upper(),
                "country": country,
                "default_currency": devise,
            }
        )
        societe.flags.ignore_permissions = True
        societe.insert()
    finally:
        frappe.local.flags.ignore_chart_of_accounts = False

    _poser_plan(societe.name, chart_name)
    frappe.db.commit()

    return {
        "company": societe.name,
        "country": country,
        "currency": devise,
        "chart": chart_name,
        "accounts_created": frappe.db.count("Account", {"company": societe.name}),
    }

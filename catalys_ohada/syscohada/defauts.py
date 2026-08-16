# Copyright (c) 2026, Catalys and contributors
# License: GNU General Public License v3. See license.txt

"""Comptes par defaut de la societe, en correspondance SYSCOHADA.

ERPNext expose une trentaine de champs de compte sur la Company. Il ne les
renseigne que pour ses propres plans de comptes ; avec un plan tiers, ils
restent vides et l'erreur ne surgit qu'a la premiere piece :
« Please set default Stock Received But Not Billed in Company... ».

Ce module pose la correspondance. Les champs dont l'equivalent SYSCOHADA
serait discutable sont volontairement laisses vides — mieux vaut une erreur
explicite au moment utile qu'une imputation silencieusement fausse. Ils sont
listes en fin de fichier.
"""

import frappe

# champ ERPNext -> numero de compte SYSCOHADA imputable
CORRESPONDANCE: dict[str, str] = {
    # Tiers
    "default_receivable_account": "4111",   # Clients
    "default_payable_account": "4011",      # Fournisseurs
    "default_advance_paid_account": "4091",  # Fournisseurs, avances et acomptes verses
    "default_advance_received_account": "4191",  # Clients, avances et acomptes recus
    # Exploitation
    "default_income_account": "7011",       # Ventes de marchandises dans la Region
    "default_expense_account": "6011",      # Achats de marchandises dans la Region
    # Tresorerie
    "default_bank_account": "5211",         # Banques en monnaie nationale
    "default_cash_account": "5711",         # Caisse en monnaie nationale
    # Stocks
    "stock_received_but_not_billed": "4081",  # Fournisseurs, factures non parvenues
    "default_inventory_account": "3111",    # Marchandises
    "stock_adjustment_account": "6031",     # Variations des stocks de marchandises
    # Ecarts et regularisations
    "round_off_account": "6588",            # Autres charges diverses
    "write_off_account": "6511",            # Pertes sur creances clients
    "exchange_gain_loss_account": "676",    # Pertes de change financieres
    "default_deferred_expense_account": "476",   # Charges constatees d'avance
    "default_deferred_revenue_account": "477",   # Produits constatees d'avance
    # Immobilisations
    "depreciation_expense_account": "6813",  # Dotations aux amortissements corporels
    "disposal_account": "812",              # Valeurs comptables des cessions corporelles
    "asset_received_but_not_billed": "4812",  # Fournisseurs d'investissement, corporelles
}

# Laisses vides a dessein, faute d'equivalent univoque :
#
#   accumulated_depreciation_account   les comptes 28x sont ventiles par nature
#                                      d'immobilisation ; le choix revient a la
#                                      categorie d'immobilisation, pas a la societe.
#   capital_work_in_progress_account   239x distingue batiments, installations et
#                                      ouvrages : aucun ne s'impose par defaut.
#   expenses_added_to_stock_account    depend de la politique de valorisation.
#   default_provisional_account        usage rare, a poser au cas par cas.
#   unrealized_exchange_gain_loss_account   478x/479x supposent un choix de
#                                      presentation que l'entite doit arreter.
NON_MAPPES = (
    "accumulated_depreciation_account",
    "capital_work_in_progress_account",
    "expenses_added_to_stock_account",
    "default_provisional_account",
    "unrealized_exchange_gain_loss_account",
)


def poser_defauts(company: str, ecraser: bool = False) -> dict:
    """Renseigne les comptes par defaut de la societe.

    Par defaut, ne touche pas aux champs deja renseignes : un parametrage
    manuel du comptable prime sur la correspondance generique.
    """
    meta = frappe.get_meta("Company")
    doc = frappe.get_doc("Company", company)

    poses, introuvables, conserves = {}, {}, []

    for champ, numero in CORRESPONDANCE.items():
        if not meta.has_field(champ):
            continue
        if doc.get(champ) and not ecraser:
            conserves.append(champ)
            continue
        compte = frappe.db.get_value(
            "Account", {"company": company, "account_number": numero, "is_group": 0}, "name"
        )
        if not compte:
            introuvables[champ] = numero
            continue
        frappe.db.set_value("Company", company, champ, compte)
        poses[champ] = compte

    frappe.clear_cache(doctype="Company")
    return {
        "poses": poses,
        "introuvables": introuvables,
        "deja_renseignes": conserves,
        "non_mappes": list(NON_MAPPES),
    }

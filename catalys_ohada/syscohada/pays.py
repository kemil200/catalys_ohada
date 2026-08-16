# Copyright (c) 2026, Catalys and contributors
# License: GNU General Public License v3. See license.txt

"""Les 17 Etats parties a l'OHADA et leur monnaie legale.

Les libelles sont ceux du referentiel Frappe (``frappe/geo/country_info.json``)
et non les noms usuels : c'est sur eux que porte le champ ``country`` de la
Company. Les devises ont ete controlees une a une contre ce meme referentiel.
"""

OHADA: dict[str, str] = {
    # UEMOA — franc CFA BCEAO
    "Benin": "XOF",
    "Burkina Faso": "XOF",
    "Ivory Coast": "XOF",
    "Guinea-Bissau": "XOF",
    "Mali": "XOF",
    "Niger": "XOF",
    "Senegal": "XOF",
    "Togo": "XOF",
    # CEMAC — franc CFA BEAC
    "Cameroon": "XAF",
    "Central African Republic": "XAF",
    "Congo": "XAF",
    "Gabon": "XAF",
    "Equatorial Guinea": "XAF",
    "Chad": "XAF",
    # Hors zone franc. Deux pieges classiques : la Guinee (Conakry) n'est pas
    # dans la zone franc, et la RD Congo — adherente depuis 2012 — est souvent
    # omise des listes OHADA. Son libelle Frappe est inhabituel.
    "Guinea": "GNF",
    "Comoros": "KMF",
    "Congo, The Democratic Republic of the": "CDF",
}

# L'AUDCIF impose l'exercice calendaire : du 1er janvier au 31 decembre.
EXERCICE_DEBUT = "01-01"
EXERCICE_FIN = "12-31"


def devise_du_pays(pays: str | None) -> str | None:
    """Monnaie legale d'un Etat partie, ou None s'il n'est pas dans l'espace."""
    return OHADA.get(pays or "")


def est_ohada(pays: str | None) -> bool:
    return (pays or "") in OHADA

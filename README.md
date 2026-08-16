# C-ERP OHADA

Référentiel comptable **SYSCOHADA révisé**, module du progiciel **C-ERP** édité par Catalys.

Application Frappe qui apporte le plan de comptes de l'Acte uniforme relatif au droit
comptable et à l'information financière (AUDCIF, applicable depuis le 1ᵉʳ janvier 2018)
aux 17 États membres de l'OHADA.

S'installe sur toute instance [ERPNext](https://github.com/frappe/erpnext) : le module ne
dépend d'aucune spécificité de C-ERP et reste utilisable seul.

## Contenu

| | |
|---|---|
| Comptes | **1 364**, dont **1 072 imputables** et 292 de regroupement |
| Classes | 1 à 8 (voir *Choix de conception* pour la classe 9) |
| Source | Acte uniforme AUDCIF, plan de comptes officiel |

## Installation

```bash
bench get-app https://github.com/catalys/catalys_ohada
```

```bash
bench --site <site> install-app catalys_ohada
```

## Utilisation

Le plan de comptes n'est **pas** appliqué automatiquement à l'installation : ERPNext crée
le plan à la naissance de la société, et l'écraser détruirait un paramétrage existant.
L'application est donc explicite, société par société, sur une société **vierge de toute
écriture** :

```bash
bench --site <site> execute catalys_ohada.syscohada.chart.apply_to_company --kwargs "{'company': 'Ma Societe'}"
```

## Choix de conception

**Douze racines plutôt que neuf classes.** ERPNext impose un `root_type` unique par
branche de l'arbre, or les classes SYSCOHADA 1, 4, 5 et 8 sont à cheval sur l'actif et le
passif. Les classes concernées sont donc scindées à la racine — classe 1 en *Capitaux
propres* (10-14) et *Dettes financières* (15-19), classe 4 en *Créances* et *Dettes*,
classe 5 en *Trésorerie actif* et *passif*, classe 8 en *Charges* et *Produits HAO*. Les
numéros de compte sont inchangés ; seul le regroupement d'affichage diffère.

**Seize comptes détachés de leur parent numérique** parce que leur nature s'y oppose :
`409 Fournisseurs débiteurs` sort de 40, `419 Clients créditeurs` sort de 41,
`445 TVA récupérable` sort de 44, `499 Provisions pour risques` sort de 49, etc. Sans ce
détachement, la TVA récupérable serait rattachée au passif.

**Classe 9 exclue.** Les 50 comptes de comptabilité analytique et d'engagements hors bilan
n'ont pas d'équivalent dans un plan de comptes financier ERPNext. L'analytique se traite
nativement par les *Cost Centers* et les *Accounting Dimensions*, plus souples que des
comptes réfléchis.

## Limite connue

La sous-structure des comptes **479x — Écarts de conversion, passif** reste à valider :
la source officielle indique `4797 Différences d'évaluation sur instruments de trésorerie`
là où le plan diffusé porte `4797 Diminution des dettes financières`. Dix comptes sont
concernés, rarement mouvementés en PME.

## Régénérer le plan

Le JSON livré dans `catalys_ohada/syscohada/data/` est produit à partir de la source
tabulée `scripts/pcs_clean.tsv` :

```bash
python scripts/build_coa.py
```

Le script porte les règles de typage (`root_type`, `account_type`) sous forme de tables de
préfixes explicites, relisibles par un comptable sans lire le reste du code.

## Licence

[GPL-3.0-or-later](license.txt). ERPNext étant sous GPL-3.0, toute application qui en
dérive l'est également. Le copyleft est ici un choix assumé : il garantit que les
améliorations apportées au référentiel OHADA restent accessibles à tous.

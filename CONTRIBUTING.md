# Contribuer

Les contributions sont bienvenues, en particulier de la part des praticiens du SYSCOHADA.

## Ce qui est le plus utile

**Corrections du référentiel.** Un compte au mauvais numéro, un libellé tronqué, une
subdivision manquante. Ce sont les contributions les plus précieuses — merci de citer la
référence dans l'Acte uniforme AUDCIF (chapitre et page) plutôt que le seul usage local.

**Adaptations nationales.** Le plan livré est commun aux 17 États membres. Les
particularités fiscales nationales (taux de TVA, comptes d'impôts spécifiques) ont
vocation à vivre dans des fichiers distincts, pas à modifier le socle commun.

**Validation des choix de conception.** Le découpage en douze racines et les seize
détachements de comptes sont documentés dans le README. Un désaccord argumenté sur l'un
d'eux est une contribution à part entière.

## Ce que ce dépôt n'accueille pas

Les fonctionnalités propres à un produit ou à un client. Ce dépôt ne porte que le
référentiel comptable — il doit rester installable tel quel par n'importe qui.

## Modifier le plan de comptes

Ne modifiez **pas** le JSON à la main. Il est généré :

1. corrigez `scripts/pcs_clean.tsv` (format `code<TAB>libellé`), ou les tables de
   réparation en tête de `scripts/build_coa.py` ;
2. relancez `python scripts/build_coa.py` ;
3. joignez à la pull request la sortie du script — elle rapporte les doublons, les
   orphelins et les comptes détachés.

Une pull request qui modifie le JSON sans modifier la source ne sera pas fusionnée : la
correction serait perdue à la régénération suivante.

## Style

Python formaté avec `ruff` (configuration dans `pyproject.toml`). Les commentaires et la
documentation sont en français : c'est la langue de travail du référentiel.

## Licence

En contribuant, vous acceptez que votre travail soit distribué sous GPL-3.0-or-later.

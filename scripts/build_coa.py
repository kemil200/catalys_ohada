# -*- coding: utf-8 -*-
"""PCS.txt nettoye -> plan de comptes ERPNext (JSON)."""
import json, io, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pcs_clean.tsv")
OUT = os.path.join(HERE, os.pardir, "catalys_ohada", "syscohada", "data",
                   "tg_syscohada_revise.json")

# ---------------------------------------------------------------- reparations
RECODE = {   # (code actuel, debut de libelle) -> code officiel
    ("215", "MARQUES"): "214",
    ("216", "FONDS COMMERCIAL"): "215",
    ("217", "DROIT AU BAIL"): "216",
    ("218", "INVESTISSEMENTS DE CREATION"): "217",
    ("4793", "Diminution des dettes d"): "4794",
}
AJOUTS = [   # parents manquants, libelles verifies sur le PDF officiel
    ("70",  "VENTES"),
    ("88",  "SUBVENTIONS D'EQUILIBRE"),
    ("166", "INTERETS COURUS"),
    ("442", "ETAT, AUTRES IMPOTS ET TAXES"),
    ("313", "STOCKS D'ACTIFS BIOLOGIQUES"),
    ("345", "ACTIFS BIOLOGIQUES EN COURS"),
    ("4792", "Augmentation des creances HAO"),
]
# doublons 4 chiffres qui sont des codes 5 chiffres tronques -> a supprimer
SUPPRIMER = {
    ("4781", "Diminution des creances d'exploitation"),
    ("4781", "Diminution des creances HAO"),
    ("4783", "Augmentation des dettes d'exploitation"),
    ("4783", "Augmentation des dettes HAO"),
    ("4791", "Augmentation des creances d'exploitation"),
}
def nk(s):
    for a, b in [("’","'"),("é","e"),("è","e"),("ê","e"),("à","a"),("ç","c"),
                 ("ô","o"),("û","u"),("î","i"),("É","E"),("È","E"),("Ê","E")]:
        s = s.replace(a, b)
    return s

rows = []
for line in open(SRC, encoding="utf-8"):
    code, lab = line.rstrip("\n").split("\t")
    lab = lab.rstrip()
    # cesures : code du compte suivant colle en fin de libelle
    parts = lab.split()
    if len(parts) > 1 and parts[-1].isdigit() and 2 <= len(parts[-1]) <= 4:
        lab = " ".join(parts[:-1])
    for (c, pref), new in RECODE.items():
        if code == c and nk(lab).upper().startswith(pref.upper()):
            code = new
    if (code, nk(lab)) in SUPPRIMER:
        continue
    rows.append((code, lab))

have = {c for c, _ in rows}
rows += [(c, l) for c, l in AJOUTS if c not in have]
rows = [(c, l) for c, l in rows if not c.startswith("9")]      # classe 9 exclue
rows = list(dict.fromkeys(rows))
rows.sort(key=lambda r: (r[0], r[1]))

# ------------------------------------------------------- typage (regle : prefixe le plus long)
ROOT = [
    ("10","Equity"),("11","Equity"),("12","Equity"),("13","Equity"),("14","Equity"),
    ("15","Liability"),("16","Liability"),("17","Liability"),("18","Liability"),("19","Liability"),
    ("2","Asset"), ("3","Asset"),
    ("40","Liability"),("409","Asset"),
    ("41","Asset"),("419","Liability"),
    ("42","Liability"),("421","Asset"),("428","Asset"),
    ("43","Liability"),("438","Asset"),
    ("44","Liability"),("445","Asset"),("449","Asset"),
    ("45","Liability"),("452","Asset"),
    ("46","Liability"),("461","Asset"),("465","Asset"),
    ("47","Liability"),("471","Asset"),("476","Asset"),("478","Asset"),
    ("48","Liability"),("485","Asset"),("488","Asset"),
    ("49","Asset"),("499","Liability"),
    ("5","Asset"),("56","Liability"),
    ("6","Expense"),("7","Income"),
    ("81","Expense"),("82","Income"),("83","Expense"),("84","Income"),
    ("85","Expense"),("86","Income"),("87","Expense"),("88","Income"),("89","Expense"),
]
ATYPE = [
    ("21","Fixed Asset"),("22","Fixed Asset"),("23","Fixed Asset"),("24","Fixed Asset"),
    ("28","Accumulated Depreciation"),("29","Accumulated Depreciation"),
    ("31","Stock"),("32","Stock"),("33","Stock"),("34","Stock"),("35","Stock"),
    ("36","Stock"),("37","Stock"),("38","Stock"),
    ("401","Payable"),("411","Receivable"),
    ("443","Tax"),("444","Tax"),("445","Tax"),("446","Tax"),("447","Tax"),
    ("52","Bank"),("53","Bank"),("57","Cash"),
    ("601","Cost of Goods Sold"),("602","Cost of Goods Sold"),("603","Cost of Goods Sold"),
    ("604","Cost of Goods Sold"),("605","Cost of Goods Sold"),("608","Cost of Goods Sold"),
    ("681","Depreciation"),("691","Depreciation"),("851","Depreciation"),
]
def lookup(table, code, default=None):
    best = default
    for pref, val in table:
        if code.startswith(pref) and (best is None or len(pref) >= len(getattr(lookup, "_l", ""))):
            pass
    hits = [(len(p), v) for p, v in table if code.startswith(p)]
    return max(hits)[1] if hits else default

# ------------------------------------------------------------------- racines
RACINES = [
    ("1-CAPITAUX PROPRES", "Equity",    lambda c: c[:2] in ("10","11","12","13","14")),
    ("1-DETTES FINANCIERES ET RESSOURCES ASSIMILEES", "Liability", lambda c: c[:2] in ("15","16","17","18","19")),
    ("2-ACTIF IMMOBILISE", "Asset",     lambda c: c[0] == "2"),
    ("3-STOCKS",           "Asset",     lambda c: c[0] == "3"),
    ("4-TIERS - CREANCES", "Asset",     lambda c: c[0] == "4" and lookup(ROOT, c) == "Asset"),
    ("4-TIERS - DETTES",   "Liability", lambda c: c[0] == "4" and lookup(ROOT, c) == "Liability"),
    ("5-TRESORERIE ACTIF", "Asset",     lambda c: c[0] == "5" and lookup(ROOT, c) == "Asset"),
    ("5-TRESORERIE PASSIF","Liability", lambda c: c[0] == "5" and lookup(ROOT, c) == "Liability"),
    ("6-CHARGES DES ACTIVITES ORDINAIRES", "Expense", lambda c: c[0] == "6"),
    ("7-PRODUITS DES ACTIVITES ORDINAIRES","Income",  lambda c: c[0] == "7"),
    ("8-CHARGES HAO",  "Expense", lambda c: c[0] == "8" and lookup(ROOT, c) == "Expense"),
    ("8-PRODUITS HAO", "Income",  lambda c: c[0] == "8" and lookup(ROOT, c) == "Income"),
]

codes = {c for c, _ in rows}
lbl_pre = dict(rows)
def parent(c):
    p = c[:-1]
    while len(p) >= 2:
        if p in codes: return p
        p = p[:-1]
    return None

def racine_pour(c):
    for nom, rt, test in RACINES:
        if test(c): return nom
    return None

enfants = collections.defaultdict(list)
racine_de = {}
detaches = []
for c, l in rows:
    p = parent(c)
    # un enfant dont le root_type differe de son parent est detache vers sa propre racine
    if p and racine_pour(c) != racine_pour(p):
        detaches.append((c, p, racine_pour(p), racine_pour(c)))
        p = None
    if p:
        enfants[p].append(c)
    else:
        r = racine_pour(c)
        if r: racine_de[c] = r

print(f"comptes detaches (root_type != parent) : {len(detaches)}")
for c, p, rp, rc in detaches:
    print(f"   {c:6s} {lbl_pre.get(c,'')[:40]:42s} sorti de {p} [{rp}] -> [{rc}]")


lbl = dict(rows)
def noeud(c):
    d = {}
    for k in sorted(enfants.get(c, [])):
        d[f"{k}-{lbl[k]}"] = noeud(k)
    at = lookup(ATYPE, c)
    if at: d["account_type"] = at
    if enfants.get(c): d["is_group"] = 1
    return d

tree = {}
for nom, rt, _ in RACINES:
    sous = sorted(c for c, r in racine_de.items() if r == nom)
    if not sous: continue
    n = {f"{c}-{lbl[c]}": noeud(c) for c in sous}
    n["root_type"] = rt
    n["is_group"] = 1
    tree[nom] = n

# ------------- format ERPNext : libelle en cle, numero de compte en attribut
META = {"root_type", "account_type", "is_group", "tax_rate", "account_number"}

def nettoyer(lab):
    if lab.upper().startswith("REANCES ET DETTES"):
        lab = "C" + lab                        # troncature de la source
    lab = re.sub(r"\s*\(\d\)", "", lab)        # renvois de note (1)(2)(3) du PDF
    lab = re.sub(r"\s+,", ",", lab)
    return " ".join(lab.split()).strip(" ,")

def reformater(node):
    out = {}
    for k, v in node.items():
        if k in META:
            out[k] = v
            continue
        m = re.match(r"^(\d{2,5})-(.+)$", k)
        code, label = (m.group(1), m.group(2)) if m else (None, k)
        label = nettoyer(label)
        while label in out:                    # homonymes SYSCOHADA : lever par le code
            label = f"{label} ({code})"
        child = reformater(v)
        out[label] = {"account_number": code, **child} if code else child
    return out

out = {"country_code": "tg", "name": "Togo - SYSCOHADA Revise", "tree": reformater(tree)}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("ecrit ->", os.path.relpath(OUT, HERE))

print(f"comptes retenus        : {len(rows)}  (classe 9 exclue)")
print(f"comptes non rattaches  : {len(rows) - sum(1 for c,_ in rows if parent(c) or c in racine_de)}")
print(f"racines                : {len(tree)}")
for nom, rt, _ in RACINES:
    if nom in tree:
        k = sum(1 for c, r in racine_de.items() if r == nom)
        print(f"   {rt:10s} {nom:48s} {k:3d} tetes")
dups = [c for c, n in collections.Counter(c for c, _ in rows).items() if n > 1]
print(f"codes en double        : {sorted(dups) or 'aucun'}")
orph = sorted(c for c in codes if len(c) > 2 and not parent(c))
print(f"orphelins              : {len(orph)} {orph[:10]}")

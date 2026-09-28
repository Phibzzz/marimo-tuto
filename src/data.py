"""Chargement, nettoyage et validation du dataset Video Game Sales.

Source du dataset : https://www.kaggle.com/datasets/gregorut/videogamesales

Ce module contient volontairement très peu de code :
- il est importé par le notebook Marimo (notebooks/videogame_sales.py) ;
- il est testé indépendamment du notebook (tests/test_pipeline.py) ;
- il peut être exécuté seul pour vérifier le dataset avant une démo :

    python src/data.py

Les agrégations et les graphiques restent dans le notebook : c'est là que
le tutoriel se déroule.
"""

from pathlib import Path

import polars as pl

# --- Chemin du dataset --------------------------------------------------------
# Le CSV est toujours dans data/, au même niveau que src/ (jamais à la racine du
# projet ni ailleurs). On part de l'emplacement de CE fichier (src/data.py) : le
# chemin ne dépend donc pas du répertoire depuis lequel le code est lancé.
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "vgsales.csv"

# --- Schéma attendu ----------------------------------------------------------
# Colonnes du fichier vgsales.csv publié sur Kaggle.
# Les ventes sont exprimées en MILLIONS d'unités vendues.
EXPECTED_COLUMNS = [
    "Rank",
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales",
    "Global_Sales",
]

# Les 4 régions dont la somme donne (à l'arrondi près) Global_Sales.
REGION_COLUMNS = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
SALES_COLUMNS = [*REGION_COLUMNS, "Global_Sales"]


def load_sales(path: Path = DATA_PATH) -> pl.DataFrame:
    """Lit le CSV brut avec Polars.

    Pourquoi `null_values="N/A"` ?
    Le fichier utilise la chaîne "N/A" pour les valeurs manquantes (colonnes
    Year et Publisher). Sans ce paramètre, `pl.read_csv` échoue :
    `could not parse "N/A" as dtype i64 at column 'Year'`.
    En déclarant "N/A" comme valeur nulle, Year est correctement lue en entier.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {path}\n"
            "Téléchargez vgsales.csv depuis "
            "https://www.kaggle.com/datasets/gregorut/videogamesales "
            "et placez-le dans le dossier data/."
        )
    return pl.read_csv(path, null_values="N/A")


def clean_sales(raw_df: pl.DataFrame) -> pl.DataFrame:
    """Applique les seules transformations nécessaires à l'analyse.

    Problème réel constaté : 271 lignes n'ont pas d'année (Year = null).
    Décision : on les écarte, car l'application filtre et agrège par année.
    On ne les remplace PAS par une valeur arbitraire (0, moyenne...) : cela
    créerait de fausses années et fausserait la courbe temporelle.

    Year est ensuite convertie en Int32 : une année tient largement dedans et
    le type exprime clairement qu'il s'agit d'un entier, pas d'un flottant.
    """
    return raw_df.filter(pl.col("Year").is_not_null()).with_columns(
        pl.col("Year").cast(pl.Int32)
    )


def check_dataset(df: pl.DataFrame) -> list[str]:
    """Retourne la liste des problèmes de structure (liste vide = tout va bien)."""
    problems: list[str] = []

    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        problems.append(f"Colonnes manquantes : {missing}")

    for col in SALES_COLUMNS:
        if col in df.columns and not df.schema[col].is_numeric():
            problems.append(f"{col} devrait être numérique, type lu : {df.schema[col]}")

    if "Year" in df.columns and not df.schema["Year"].is_integer():
        problems.append(f"Year devrait être entière, type lu : {df.schema['Year']}")

    if df.height == 0:
        problems.append("Le DataFrame est vide.")

    return problems


if __name__ == "__main__":
    # Vérification rapide avant une démo : python src/data.py
    raw = load_sales()
    clean = clean_sales(raw)
    issues = check_dataset(raw)
    print(f"Fichier       : {DATA_PATH}")
    print(f"Lignes brutes : {raw.height}")
    print(f"Lignes propres: {clean.height} ({raw.height - clean.height} sans année écartées)")
    print("Structure     :", "OK" if not issues else issues)

# Instructions de développement

Ce document permet de **reconstruire intégralement le projet from scratch**, étape par étape,
dans l'ordre du tutoriel. Chaque étape suit le même format : Objectif · Fichiers concernés ·
Action · Code · Commande · Résultat attendu · Point pédagogique.

Progression du code :

```text
Étape 1  Marimo → Hello World                         (§8)
Étape 2  Marimo → CSV → DataFrame                     (§9–10)
Étape 3  DataFrame → Exploration → Nettoyage          (§11–12)
Étape 4  DataFrame → Polars → Agrégation              (§13–14)
Étape 5  Agrégation → Plotly → Graphique              (§14–17)
Étape 6  Marimo UI → Filtre → DataFrame → Graphique   (§18–19)
Étape 7  Application interactive                      (§20–23)
```

Versions vérifiées le 27/09/2026 : Python 3.11.5, marimo 0.25.0, polars 1.44.2,
plotly 7.1.0 (+ numpy 2.4.6), pytest 9.1.1, sous Windows 11.

**Conventions dans ce document**

- Les blocs « Cellule » contiennent le code à taper **dans une cellule de l'éditeur Marimo**
  (Marimo écrit lui-même le fichier `.py` : `@app.cell`, paramètres, `return`).
- Commandes données pour macOS/Linux (bash) et Windows (PowerShell) quand elles diffèrent.
- Toutes les commandes sont lancées depuis la racine du projet `marimo-video-games/`.
- Le dataset est toujours `data/vgsales.csv` (dans le projet, pas à sa racine ni au-dessus).
- Dans le notebook, chaque section = **une cellule Markdown** (la question) + **une cellule de
  code** (agréger → visualiser). Les noms d'axes sont centralisés dans `LABELS` et le style
  dans `px.defaults` : chaque graphique reste court.

---

## 0. Prérequis

### Objectif

Disposer des outils nécessaires avant de commencer.

### Fichiers concernés

Aucun.

### Action

Vérifier : Python ≥ 3.11, un compte Kaggle, un navigateur récent, un éditeur de code.

### Code

Aucun.

### Commande

```bash
python --version        # macOS/Linux : python3 --version ; Windows : py -3.11 --version
```

### Résultat attendu

`Python 3.11.x` ou plus récent.

### Point pédagogique

Marimo et Polars ciblent les versions récentes de Python ; 3.11 est le minimum retenu
pour ce projet (`requires-python = ">=3.11"`).

---

## 1. Créer le projet

### Objectif

Créer l'arborescence minimale.

### Fichiers concernés

`data/`, `notebooks/`, `src/`, `tests/`, `.gitignore`, `pyproject.toml`

### Action

Créer les dossiers, puis les fichiers `.gitignore` et `pyproject.toml`.

### Code

`.gitignore` :

```gitignore
# Environnement Python
.venv/
__pycache__/
*.py[cod]
.pytest_cache/

# Marimo (cache et sessions locales)
__marimo__/
.marimo/

# Dataset Kaggle : à télécharger depuis Kaggle (voir README), non redistribué dans git
data/*.csv

# Éditeurs / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
```

`pyproject.toml` :

```toml
[project]
name = "marimo-video-games"
version = "0.1.0"
description = "Tutoriel : application de datavisualisation interactive avec Marimo, Polars et Plotly (dataset Kaggle Video Game Sales)"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "marimo>=0.25",
    "polars>=1.44",
    # Plotly Express a besoin de numpy : l'extra [express] l'installe (pas de pandas).
    "plotly[express]>=7.1",
]

[dependency-groups]
dev = ["pytest>=9"]

[tool.pytest.ini_options]
# La racine du projet est ajoutée au sys.path : `import src.data` et
# `import notebooks.videogame_sales` fonctionnent dans les tests.
pythonpath = ["."]
testpaths = ["tests"]
```

### Commande

```bash
mkdir -p marimo-video-games/{data,notebooks,src,tests}
cd marimo-video-games
```

```powershell
New-Item -ItemType Directory -Force marimo-video-games/data, marimo-video-games/notebooks, marimo-video-games/src, marimo-video-games/tests
Set-Location marimo-video-games
```

### Résultat attendu

```text
marimo-video-games/
├── data/  notebooks/  src/  tests/
├── .gitignore
└── pyproject.toml
```

### Point pédagogique

Structure volontairement minimale : un notebook au centre, un petit module testable à côté.
Pas de framework web, pas de classes, pas d'architecture superflue.

---

## 2. Créer l'environnement Python

### Objectif

Isoler les dépendances du projet dans un environnement virtuel.

### Fichiers concernés

`.venv/` (ignoré par git)

### Action

Créer puis activer le venv.

### Code

Aucun.

### Commande

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Résultat attendu

Le prompt affiche `(.venv)` ; `python --version` renvoie 3.11+.

### Point pédagogique

Un environnement par projet = une installation reproductible, sans conflit avec les autres
projets. (Alternative : `uv sync` lit directement `pyproject.toml`.)

---

## 3. Installer Marimo

### Objectif

Installer Marimo et vérifier qu'il démarre.

### Fichiers concernés

Aucun.

### Action

Installer le paquet, vérifier la version.

### Code

Aucun.

### Commande

```bash
pip install "marimo==0.25.0"
marimo --version
```

Optionnel, pour découvrir l'outil : `marimo tutorial intro`.

### Résultat attendu

`0.25.0`

### Point pédagogique

Marimo est un **notebook Python réactif** : un notebook est un fichier `.py`, les cellules
dépendantes se ré-exécutent automatiquement, et le même fichier devient une application
avec `marimo run`.

---

## 4. Installer Polars

### Objectif

Installer la bibliothèque de DataFrames.

### Fichiers concernés

Aucun.

### Action

Installer Polars.

### Code

Aucun.

### Commande

```bash
pip install "polars==1.44.2"
python -c "import polars as pl; print(pl.__version__)"
```

### Résultat attendu

`1.44.2`

### Point pédagogique

Polars manipule des tables typées avec des **expressions** (`pl.col(...)`) : les
transformations se lisent comme des phrases (`filter`, `group_by`, `agg`, `sort`).

---

## 5. Installer Plotly

### Objectif

Installer Plotly **avec** Plotly Express.

### Fichiers concernés

`requirements.txt`

### Action

Installer `plotly[express]` (et non `plotly` seul), puis figer les versions.

### Code

`requirements.txt` :

```text
# Versions vérifiées le 27/09/2026 avec Python 3.11.5 (Windows 11).
marimo==0.25.0
polars==1.44.2
# Plotly Express a besoin de numpy : l'extra [express] l'installe (pandas n'est pas requis).
plotly[express]==7.1.0
# Tests du pipeline (optionnel pour suivre le tutoriel)
pytest==9.1.1
```

### Commande

```bash
pip install "plotly[express]==7.1.0" "pytest==9.1.1"
python -c "import plotly.express as px; print('Plotly Express OK')"
```

Par la suite, une installation complète se fait en une commande : `pip install -r requirements.txt`.

### Résultat attendu

`Plotly Express OK`. Avec `pip install plotly` seul, on obtiendrait :
`ImportError: Plotly Express requires numpy to be installed`.

### Point pédagogique

Plotly Express est l'API **haut niveau** de Plotly (`px.bar`, `px.line`, `px.histogram`,
`px.scatter`…). Depuis Plotly 6, elle accepte directement les DataFrames Polars : pandas est
inutile.

---

## 6. Télécharger le dataset Kaggle

### Objectif

Récupérer `vgsales.csv` depuis sa source officielle.

### Fichiers concernés

`vgsales.csv` (archive Kaggle)

### Action

**Option A — navigateur** : ouvrir <https://www.kaggle.com/datasets/gregorut/videogamesales>,
se connecter, cliquer sur **Download**, extraire `vgsales.csv` de l'archive ZIP.

**Option B — CLI Kaggle** : nécessite un jeton API (Kaggle → Settings → API → *Create New Token*,
voir <https://github.com/Kaggle/kaggle-api>).

Lire la page Kaggle : auteur *GregorySmith*, données scrapées sur vgchartz.com,
**licence « Unknown »**. Usage pédagogique ; ne pas redistribuer le fichier.

### Code

Aucun.

### Commande

Option B :

```bash
pip install kaggle
kaggle datasets download -d gregorut/videogamesales -p data --unzip
```

### Résultat attendu

Un fichier `vgsales.csv` de **1 355 781 octets** (16 599 lignes, en-tête compris).

### Point pédagogique

Toujours documenter la **provenance** et les **conditions d'utilisation** d'un dataset :
une visualisation n'est fiable que si l'on sait d'où viennent les données.

---

## 7. Placer vgsales.csv dans data/

### Objectif

Mettre le CSV à l'emplacement attendu par le code.

### Fichiers concernés

`data/vgsales.csv`

### Action

Déplacer le fichier (inutile avec l'option B, qui le place déjà dans `data/`).
Ouvrir les premières lignes pour voir le format brut.

Le code attend le fichier **exactement** à `data/vgsales.csv` (constante `DATA_PATH` de
`src/data.py`, étape 10). Un CSV laissé à la racine du projet (`marimo-video-games/vgsales.csv`)
ou dans le dossier parent n'est **pas** trouvé : le notebook affiche alors un encadré rouge.

### Code

Aucun.

### Commande

```bash
mv ~/Downloads/vgsales.csv data/        # adapter le chemin
head -3 data/vgsales.csv
```

```powershell
Move-Item $HOME\Downloads\vgsales.csv data\   # adapter le chemin
Get-Content data\vgsales.csv -TotalCount 3
```

### Résultat attendu

```text
Rank,Name,Platform,Year,Genre,Publisher,NA_Sales,EU_Sales,JP_Sales,Other_Sales,Global_Sales
1,Wii Sports,Wii,2006,Sports,Nintendo,41.49,29.02,3.77,8.46,82.74
2,Super Mario Bros.,NES,1985,Platform,Nintendo,29.08,3.58,6.81,0.77,40.24
```

```text
marimo-video-games/
└── data/
    └── vgsales.csv
```

### Point pédagogique

Regarder le fichier brut **avant** d'écrire du code : séparateur, en-têtes, unités
(millions d'unités), et plus loin, la chaîne `N/A` qui signale les valeurs manquantes.

---

## 8. Créer le premier notebook Marimo

### Objectif

Étape 1 de la progression : **Marimo → Hello World**, et observer la réactivité.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

1. Lancer l'éditeur : la commande crée le fichier s'il n'existe pas et ouvre le navigateur.
2. Dans la première cellule, taper le code « Cellule 1 », exécuter (`Ctrl/Cmd + Entrée`).
3. Créer une deuxième cellule (« Cellule 2 »), puis une troisième (« Cellule 3 »).
4. Bouger le slider : la cellule 3 se met à jour **toute seule**.
5. Supprimer les cellules 2 et 3 (elles ne servaient qu'à la démonstration).

### Code

Cellule 1 :

```python
import marimo as mo
mo.md("# Hello Marimo 👋")
```

Cellule 2 :

```python
slider = mo.ui.slider(start=1, stop=10, value=3, label="Nombre d'étoiles")
slider
```

Cellule 3 :

```python
mo.md("⭐" * slider.value)
```

Ouvrir `notebooks/videogame_sales.py` dans un éditeur de texte : c'est du Python pur.

```python
import marimo

app = marimo.App()

@app.cell
def _(mo):
    slider = mo.ui.slider(start=1, stop=10, value=3, label="Nombre d'étoiles")
    slider
    return (slider,)
```

### Commande

```bash
marimo edit notebooks/videogame_sales.py
```

### Résultat attendu

Un titre « Hello Marimo 👋 », un slider, une ligne d'étoiles qui suit le slider.

### Point pédagogique

- **Réactivité** : la cellule 3 lit `slider.value` ; Marimo le sait et la relance à chaque
  changement du slider. Pas de callback.
- **Fichier `.py`** : chaque cellule est une fonction ; ses paramètres sont les variables
  qu'elle lit, son `return` celles qu'elle définit. C'est ce qui permet à Marimo de
  construire le **graphe de dépendances**.
- Différence avec Jupyter : pas d'état caché, pas d'ordre d'exécution à retenir, diff git lisible.

> Les linters (pylint…) signalent de faux positifs sur ce format (fonctions nommées `_`,
> imports dans les cellules, expressions « sans effet » qui servent à l'affichage). Ils sont
> sans conséquence. Utilisez `marimo check notebooks/videogame_sales.py` pour le vrai contrôle.

---

## 9. Ajouter les imports

### Objectif

Réunir les imports du projet dans une cellule dédiée.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Remplacer la cellule 1 du Hello World par une **cellule d'introduction** (Markdown) et une
**cellule d'imports**. Puis, dans `notebooks/videogame_sales.py` (éditeur de texte, éditeur
Marimo fermé), régler la largeur et le titre de l'application :

```python
app = marimo.App(width="medium", app_title="Video Game Sales — Marimo")
```

### Code

Cellule d'introduction (Markdown) :

````python
mo.md(r"""
# 🎮 Video Game Sales — datavisualisation interactive avec Marimo

**Dataset** : [Video Game Sales](https://www.kaggle.com/datasets/gregorut/videogamesales)
(Kaggle), fichier `data/vgsales.csv`. Une ligne = **un jeu sur une plateforme** ;
ventes en **millions d'unités** par région (`NA`, `EU`, `JP`, `Other`) et au total (`Global`).

```
QUESTION → DONNÉES → TRANSFORMATION → VISUALISATION → INTERACTION → APPLICATION
```

| # | Question | Données | Graphique |
|---|----------|---------|-----------|
| 1 | Quelles plateformes ont généré le plus de ventes ? | catégorie + mesure | Bar chart |
| 2 | Comment les ventes évoluent-elles au fil des années ? | année + mesure | Line chart |
| 3 | Quels genres sont les plus représentés ? | catégorie + comptage | Bar chart |
| 4 | Comment les ventes sont-elles distribuées ? | variable numérique | Histogramme |
| 5 | Les ventes NA et EU sont-elles liées ? | numérique + numérique | Scatter plot |
| 6 | Quels genres dominent selon les régions ? *(bonus)* | 2 catégories + mesure | Heatmap |
""")
````

Cellule d'imports (elle sera complétée à l'étape 10 pour importer `src/data.py`) :

```python
import marimo as mo
import plotly.express as px
import polars as pl

# Style commun à tous les graphiques Plotly Express.
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#2563eb"]

# Noms d'axes lisibles, avec unités, réutilisés par tous les graphiques.
LABELS = {
    "Platform": "Plateforme",
    "Genre": "Genre",
    "Year": "Année de sortie",
    "Games": "Nombre de jeux",
    "Global_Sales": "Ventes mondiales (millions d'unités)",
    "NA_Sales": "Ventes Amérique du Nord (millions d'unités)",
    "EU_Sales": "Ventes Europe (millions d'unités)",
}
```

### Commande

Aucune (l'éditeur est déjà ouvert).

### Résultat attendu

Le titre et le tableau des questions s'affichent. La cellule Markdown fonctionne même si elle
est **au-dessus** de la cellule d'imports.

### Point pédagogique

- Premier contact avec l'ordre libre : la cellule d'introduction utilise `mo`, défini plus bas.
  Marimo exécute d'abord la cellule qui **définit** `mo`, quel que soit l'ordre à l'écran.
- **Ne pas se répéter** : `px.defaults` fixe le style une fois pour toutes, et le dictionnaire
  `LABELS` nomme les axes (avec unités) de tous les graphiques via `labels=LABELS`. Chaque
  graphique ne garde que ce qui lui est propre.

---

## 10. Charger le dataset

### Objectif

Étape 2 : **CSV → DataFrame**, avec un chemin robuste.

### Fichiers concernés

`src/data.py` (créé), `notebooks/videogame_sales.py`

### Action

1. **Démonstration du problème réel**, dans une cellule temporaire :
   `pl.read_csv("data/vgsales.csv")` → erreur
   `could not parse "N/A" as dtype i64 at column 'Year'`. Supprimer ensuite cette cellule.
2. Créer `src/data.py` : chemins, schéma attendu, chargement, nettoyage, validation.
3. Dans le notebook : compléter la cellule d'imports pour importer `src/data.py`, puis ajouter
   une cellule Markdown et une cellule de chargement.

### Code

`src/data.py` (fichier complet ; `clean_sales` et `check_dataset` servent aux étapes 11–12) :

```python
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
```

Cellule d'imports, version finale (lignes ajoutées : `import sys`, `sys.path.insert`,
`from src.data import ...`) :

```python
import sys

import marimo as mo
import plotly.express as px
import polars as pl

# Rendre src/ importable : le dossier parent de notebooks/ est la racine du projet.
sys.path.insert(0, str(mo.notebook_dir().parent))
from src.data import DATA_PATH, REGION_COLUMNS, SALES_COLUMNS, clean_sales, load_sales

# Style commun à tous les graphiques Plotly Express.
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#2563eb"]

# Noms d'axes lisibles, avec unités, réutilisés par tous les graphiques.
LABELS = {...}  # inchangé
```

Cellule Markdown :

```python
mo.md(r"""
## 1. Charger les données

`load_sales()` (dans `src/data.py`) lit le CSV avec `pl.read_csv(path, null_values="N/A")`.
Sans `null_values="N/A"`, Polars échoue : le fichier écrit les valeurs manquantes
sous forme de texte `N/A`, que la colonne `Year` (entière) ne peut pas lire.
""")
```

Cellule de chargement :

```python
# mo.stop arrête la cellule (et ses dépendantes) si le fichier est absent.
mo.stop(
    not DATA_PATH.exists(),
    mo.callout(mo.md("**Dataset introuvable** : placez `vgsales.csv` dans `data/` (voir README)."), kind="danger"),
)

raw_df = load_sales(DATA_PATH)
raw_df
```

### Commande

```bash
python src/data.py
```

### Résultat attendu

```text
Lignes brutes : 16598
Lignes propres: 16327 (271 sans année écartées)
Structure     : OK
```

Dans le notebook : un tableau interactif de 16 598 lignes × 11 colonnes. Si le CSV n'est pas
dans `data/`, un encadré rouge « Dataset introuvable » s'affiche à la place.

### Point pédagogique

- **Chemin robuste** : `Path(__file__).resolve().parent.parent` (module) et `mo.notebook_dir()`
  (notebook) ne dépendent pas du répertoire courant. `data/` est **le seul** dossier de données
  du projet : le chemin est défini une fois (`DATA_PATH`), sans détour par une notion de
  « racine du projet » qui ne servirait qu'à ça.
- **Séparer** : le chargement et le nettoyage vivent dans `src/data.py` (testable avec
  `pytest`, exécutable seul) ; le notebook garde l'exploration et les graphiques.
- **`null_values="N/A"`** : le problème de données est traité **au chargement**, explicitement.
- **`mo.stop`** : un message clair plutôt qu'une trace d'erreur si le fichier manque.
- Un DataFrame Polars s'affiche nativement dans Marimo (pagination, types de colonnes).

---

## 11. Explorer les données

### Objectif

Étape 3 : *avant de visualiser, comprendre la structure des données* — taille, types,
valeurs nulles, statistiques, anomalies.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Ajouter 3 cellules : Markdown d'intro, `describe()`, Markdown d'observations.

Pour aller plus loin en live (cellule temporaire, à supprimer ensuite) :
`raw_df.filter(pl.col("Year") >= 2013).group_by("Year").len().sort("Year")` montre la chute
du nombre de jeux après 2015.

### Code

Cellule Markdown :

```python
mo.md(r"""
## 2. Explorer — *avant de visualiser, comprendre les données*

`describe()` donne, pour chaque colonne numérique, le nombre de valeurs, de nulls,
la moyenne, la médiane (`50%`), le min et le max.
""")
```

Cellule statistiques :

```python
raw_df.select("Year", *SALES_COLUMNS).describe()
```

Cellule Markdown d'observations :

```python
mo.md(r"""
**Ce que l'on observe :**

- `Year` a **271 valeurs nulles** et va jusqu'à 2020, mais la collecte s'arrête vers 2016
  (344 jeux en 2016, 3 en 2017, 1 en 2020, contre ~600 par an avant) ;
- `Global_Sales` : **médiane 0,17 M**, moyenne 0,54 M, maximum **82,74 M** (*Wii Sports*) :
  quelques énormes succès, une majorité de petits scores.
""")
```

### Commande

Aucune.

### Résultat attendu

`describe()` : `Year` null_count 271, min 1980, max 2020 ; `Global_Sales` médiane 0.17,
moyenne ≈ 0.537, max 82.74.

### Point pédagogique

L'exploration révèle les **vrais** problèmes du dataset, sans en inventer : valeurs
manquantes, collecte incomplète après 2015, distribution très asymétrique.
Ces constats guident le nettoyage **et** la lecture des graphiques.

---

## 12. Nettoyer les données

### Objectif

Produire `clean_df` en appliquant seulement les transformations nécessaires, et documenter
chaque décision.

### Fichiers concernés

`notebooks/videogame_sales.py` (la fonction `clean_sales` existe déjà dans `src/data.py`)

### Action

Ajouter une cellule Markdown (tableau des décisions) et la cellule qui crée `clean_df`.

### Code

Cellule Markdown :

```python
mo.md(r"""
## 3. Nettoyer — uniquement ce qui est nécessaire

| Problème | Décision | Pourquoi |
|---|---|---|
| `Year` nulle (271 lignes) | lignes **écartées** | inventer une année fausserait les courbes |
| 2016 → 2020 incomplètes | **conservées**, signalées | on grise la zone sur le graphique |
| `Publisher` nul (58 lignes) | **conservé** | colonne non utilisée |
""")
```

Cellule `clean_df` :

```python
clean_df = clean_sales(raw_df)

mo.md(f"`clean_df` : **{clean_df.height} lignes** ({raw_df.height - clean_df.height} lignes sans année écartées).")
```

### Commande

Aucune.

### Résultat attendu

`clean_df : 16327 lignes (271 lignes sans année écartées).`

### Point pédagogique

- Nettoyer = **décider**, et justifier chaque décision.
- On ne remplace pas une donnée manquante par une valeur inventée.
- On ne modifie pas `raw_df` : on crée une **nouvelle variable** `clean_df`. En Marimo,
  une variable globale est définie dans une seule cellule.

---

## 13. Créer les premiers KPIs

### Objectif

Étape 4 : première agrégation Polars — quelques chiffres clés affichés avec `mo.stat`.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Ajouter une cellule Markdown et la cellule KPIs. Pour l'instant, les KPIs portent sur
`clean_df` (ils passeront sur `filtered_df` à l'étape 19).

### Code

Cellule Markdown :

```python
mo.md(r"""
## 5. Indicateurs clés
""")
```

Cellule KPIs :

```python
# Tous les KPIs en une seule requête Polars : une expression par indicateur.
kpis = clean_df.select(
    pl.len().alias("rows"),
    pl.col("Name").n_unique().alias("titles"),
    pl.col("Platform").n_unique().alias("platforms"),
    pl.col("Global_Sales").sum().alias("global_sales"),
).row(0, named=True)

mo.hstack(
    [
        mo.stat(kpis["rows"], label="Jeux × plateformes", bordered=True),
        mo.stat(kpis["titles"], label="Titres uniques", bordered=True),
        mo.stat(kpis["platforms"], label="Plateformes", bordered=True),
        mo.stat(f"{kpis['global_sales']:.0f} M", label="Ventes mondiales", bordered=True),
    ],
    widths="equal",
)
```

### Commande

Aucune.

### Résultat attendu

Quatre tuiles : **16327** jeux × plateformes · **11360** titres uniques · **31** plateformes ·
**8820 M** d'unités.

### Point pédagogique

- `select` + expressions : chaque indicateur est une expression Polars nommée (`alias`).
- `.row(0, named=True)` transforme la ligne unique en dictionnaire Python.
- « Nombre de jeux » est ambigu : 16 327 lignes (jeu × plateforme) mais 11 360 titres.
  Un KPI doit dire précisément ce qu'il compte.

---

## 14. Créer le premier graphique

### Objectif

Étape 5 : **agrégation → Plotly → graphique**. Répondre à la question 1 :
*« Quelles plateformes ont généré le plus de ventes ? »* — puis, en variante, à la question 3 :
*« Quels genres sont les plus représentés ? »*

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Chaque question suit **le même modèle à deux cellules** :

1. une cellule Markdown : la question, la nature des données, le graphique choisi ;
2. une cellule de code en deux temps : **agréger** (Polars) puis **visualiser** (Plotly).

Pour la question 1, nommer la cellule de code `platform_chart` (menu de la cellule → nom),
utile pour les tests (étape 21). Top 10 fixe pour l'instant.

### Code

Markdown question 1 :

```python
mo.md(r"""
## 6. Q1 — Quelles plateformes ont généré le plus de ventes ?

Catégorie + mesure → **bar chart**, trié et limité aux N premières :
`group_by(...).agg(...)` puis `sort(...)` puis `head(N)`.
""")
```

Cellule `platform_chart` :

```python
# 1) Agréger : clean_df → platform_sales
platform_sales = (
    clean_df.group_by("Platform")
    .agg(pl.col("Global_Sales").sum(), pl.len().alias("Games"))
    .sort("Global_Sales", descending=True)
    .head(10)
)

# 2) Visualiser : platform_sales → platform_fig
platform_fig = px.bar(
    platform_sales,
    x="Platform",
    y="Global_Sales",
    text_auto=".0f",
    hover_data=["Games"],
    labels=LABELS,
    title="Top 10 des plateformes par ventes mondiales",
)
platform_fig
```

Markdown question 3 :

```python
mo.md(r"""
## 8. Q3 — Quels genres sont les plus représentés ?

« Représenté » = **nombre de jeux** : on **compte** (`pl.len()`) au lieu de **sommer**.
Barres horizontales pour que les noms de genres restent lisibles.
""")
```

Cellule question 3 :

```python
genre_counts = clean_df.group_by("Genre").agg(pl.len().alias("Games")).sort("Games")

genre_fig = px.bar(
    genre_counts,
    x="Games",
    y="Genre",
    orientation="h",
    text_auto=True,
    labels=LABELS,
    title="Nombre de jeux par genre",
)
genre_fig
```

### Commande

Aucune.

### Résultat attendu

- Un bar chart trié décroissant : PS2 (1 233 M), X360 (970 M), PS3 (949 M), Wii, DS, PS, GBA,
  PSP, PS4, PC ; valeurs sur les barres, nombre de jeux au survol.
- Un bar chart horizontal des 12 genres, *Action* (3 253) en haut, puis *Sports* (2 304).

### Point pédagogique

- **Une visualisation répond à une question analytique.**
- `pl.col("Global_Sales").sum()` garde le nom de la colonne : pas besoin d'`alias`.
- Bar chart = **comparaison de catégories** ; toujours trié, limité (top N), axes avec unités
  (`labels=LABELS`).
- Somme vs comptage : la question précise la mesure. Trier le DataFrame (`sort("Games")`)
  suffit à ordonner les barres : en horizontal, la dernière ligne s'affiche en haut.

---

## 15. Créer le graphique temporel

### Objectif

Répondre à la question 2 : *« Comment les ventes évoluent-elles au fil des années ? »*

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Markdown, puis une cellule : agrégation par année **triée**, figure `px.line`, zone grisée
sur la période incomplète (version statique : 2016 → 2020).

### Code

Markdown :

```python
mo.md(r"""
## 7. Q2 — Comment les ventes évoluent-elles au fil des années ?

Année (ordonnée) + mesure → **line chart**. ⚠️ `Global_Sales` est le total des ventes
d'un jeu **sur toute sa vie** : la courbe montre les ventes des jeux **sortis** chaque année.
""")
```

Cellule :

```python
sales_by_year = (
    clean_df.group_by("Year")
    .agg(pl.col("Global_Sales").sum(), pl.len().alias("Games"))
    .sort("Year")  # indispensable pour une courbe : l'axe X doit être ordonné
)

yearly_sales_fig = px.line(
    sales_by_year,
    x="Year",
    y="Global_Sales",
    markers=True,
    hover_data=["Games"],
    labels=LABELS,
    title="Ventes mondiales des jeux, par année de sortie",
)

# À partir de 2016 la collecte est incomplète : la baisse n'est pas un fait de marché.
yearly_sales_fig.add_vrect(
    x0=2015.5,
    x1=2020.5,
    fillcolor="gray",
    opacity=0.15,
    line_width=0,
    annotation_text="données incomplètes",
)
yearly_sales_fig
```

### Commande

Aucune.

### Résultat attendu

Une courbe de 1980 à 2020 (39 années présentes), pic en **2008 (≈ 679 M)** et 2009 (≈ 667 M),
puis une baisse ; zone grisée à partir de 2016.

### Point pédagogique

- Line chart = **évolution** d'une mesure selon une dimension **ordonnée**.
- Un graphique peut induire en erreur : la chute finale est en grande partie un **artefact
  de collecte**, et `Global_Sales` est un cumul sur la vie du jeu. On l'annote.

---

## 16. Créer l'histogramme

### Objectif

Répondre à la question 4 : *« Comment les ventes par jeu sont-elles distribuées ? »*

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Markdown (bar chart vs histogramme), puis figure `px.histogram` avec la médiane. Version
statique : essayer `log_y=False`, puis `log_y=True` (un interrupteur le remplacera à l'étape 18).

### Code

Markdown :

```python
mo.md(r"""
## 9. Q4 — Comment les ventes par jeu sont-elles distribuées ?

Une variable numérique → **histogramme**. Un bar chart compare des **catégories** ;
un histogramme montre la **distribution** d'une valeur découpée en intervalles.
La distribution est très asymétrique : activez l'échelle log pour voir la « longue traîne ».
""")
```

Cellule :

```python
median_sales = clean_df["Global_Sales"].median()

distribution_fig = px.histogram(
    clean_df,
    x="Global_Sales",
    nbins=100,
    log_y=False,  # essayer True
    labels=LABELS,
    title="Distribution des ventes mondiales par jeu",
)
distribution_fig.add_vline(x=median_sales, line_dash="dash", annotation_text=f"médiane : {median_sales:.2f} M")
distribution_fig
```

### Commande

Aucune.

### Résultat attendu

En linéaire : une barre géante près de 0 et presque rien ailleurs. En log : une décroissance
régulière jusqu'à 82,74 M. Ligne pointillée « médiane : 0.17 M ».

### Point pédagogique

- **Un bar chart compare des catégories ; un histogramme montre la distribution d'une
  variable numérique.**
- Médiane (0,17 M) ≪ moyenne (0,54 M) : quelques best-sellers tirent la moyenne.
- Le choix de l'échelle fait partie du choix du graphique.

---

## 17. Créer le scatter plot

### Objectif

Répondre à la question 5 : *« Existe-t-il une relation entre les ventes en Amérique du Nord
et en Europe ? »*

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Markdown, puis une cellule qui calcule la corrélation (Polars) et affiche le nuage de points
avec une interprétation.

### Code

Markdown :

```python
mo.md(r"""
## 10. Q5 — Les ventes en Amérique du Nord et en Europe sont-elles liées ?

Deux variables numériques → **scatter plot** (un point = un jeu), complété par le
**coefficient de corrélation de Pearson** calculé avec Polars.
""")
```

Cellule :

```python
na_eu_correlation = clean_df.select(pl.corr("NA_Sales", "EU_Sales")).item()

na_eu_fig = px.scatter(
    clean_df,
    x="NA_Sales",
    y="EU_Sales",
    hover_name="Name",
    opacity=0.5,
    labels=LABELS,
    title="Ventes par jeu : Amérique du Nord vs Europe",
)

mo.vstack(
    [
        na_eu_fig,
        mo.callout(
            mo.md(
                f"**Corrélation NA / EU : {na_eu_correlation:.2f}** (1 = relation linéaire parfaite). "
                "**Corrélation ≠ causalité** : un facteur commun (la popularité du jeu) explique les deux."
            ),
            kind="info",
        ),
    ]
)
```

### Commande

Aucune.

### Résultat attendu

Un nuage concentré près de l'origine, orienté vers le haut à droite, *Wii Sports* isolé
en (41,5 ; 29,0). Corrélation affichée : **0.77**.

### Point pédagogique

- Scatter = **relation** entre deux variables numériques ; X et Y ont chacun un sens.
- On n'ajoute pas `color="Genre"` : 12 couleurs sur 16 000 points ne se lisent pas.
- **Corrélation ≠ causalité.**

---

## 18. Ajouter un filtre Marimo

### Objectif

Étape 6 : **Marimo UI → filtre → DataFrame**. Créer les composants interactifs et le
DataFrame filtré.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

1. Ajouter, **juste après la cellule `clean_df`**, une cellule Markdown, une cellule de filtres
   (multiselect genres + range slider années) et une cellule `filtered_df`, à **nommer**
   `filter_games` (utile pour les tests, étape 21).
2. Ajouter, juste avant la cellule `platform_chart`, un slider `top_n_slider`.
3. Ajouter, juste avant la cellule de l'histogramme, un interrupteur `log_scale_switch`.

Règle Marimo : un composant est **défini** dans une cellule et sa `.value` est **lue** dans une
**autre** cellule.

### Code

Markdown :

```python
mo.md(r"""
## 4. Filtres interactifs

Un composant `mo.ui.*` est une **variable Python** : toute cellule qui lit sa `.value`
est ré-exécutée automatiquement quand l'utilisateur interagit — **sans callback**.
""")
```

Cellule filtres :

```python
all_genres = sorted(clean_df["Genre"].unique().to_list())
first_year, last_year = int(clean_df["Year"].min()), int(clean_df["Year"].max())

genre_filter = mo.ui.multiselect(options=all_genres, value=all_genres, label="Genres", full_width=True)
year_filter = mo.ui.range_slider(
    start=first_year, stop=last_year, value=[first_year, last_year], label="Années de sortie", show_value=True
)

mo.hstack([genre_filter, year_filter], widths=[2, 1], gap=2)
```

Cellule `filter_games` :

```python
# Cette cellule lit les deux filtres : elle est relancée à chaque modification.
year_start, year_end = (int(year) for year in year_filter.value)

filtered_df = clean_df.filter(
    pl.col("Genre").is_in(genre_filter.value),
    pl.col("Year").is_between(year_start, year_end),
)

mo.stop(filtered_df.is_empty(), mo.callout("Aucun jeu ne correspond : sélectionnez au moins un genre.", kind="warn"))
mo.md(f"🔁 `filtered_df` : **{filtered_df.height} lignes** sur {clean_df.height}. Toutes les cellules suivantes en dépendent.")
```

Slider top N (avant `platform_chart`) :

```python
top_n_slider = mo.ui.slider(start=5, stop=20, value=10, label="Nombre de plateformes", show_value=True)
top_n_slider
```

Interrupteur (avant l'histogramme) :

```python
log_scale_switch = mo.ui.switch(label="Échelle logarithmique (axe Y)")
log_scale_switch
```

### Commande

Aucune.

### Résultat attendu

Un multiselect avec les 12 genres présélectionnés, un range slider 1980–2020, le message
`filtered_df : 16327 lignes sur 16327`. Désélectionner un genre met à jour le message.
Tout désélectionner affiche l'avertissement jaune.

Les graphiques ne réagissent **pas encore** : ils lisent toujours `clean_df`.

### Point pédagogique

```text
Utilisateur → Composant UI → Variable Python → DataFrame filtré
```

La valeur d'un composant est une simple variable Python. `filtered_df` est une **nouvelle**
variable : `clean_df` n'est jamais modifié.

---

## 19. Exploiter la réactivité

### Objectif

Brancher les graphiques sur `filtered_df` et les composants : **filtre → DataFrame →
agrégation → graphique**, sans aucun callback.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

1. Dans les cellules KPIs, Q1, Q2, Q3, Q4 et Q5 : remplacer `clean_df` par `filtered_df`.
2. Brancher les composants (modifications ci-dessous) : `top_n_slider` dans `platform_chart`,
   `year_start`/`year_end` dans la zone grisée, `log_scale_switch` dans l'histogramme.
3. Ajouter le tableau de données et la section « Comprendre la réactivité ».
4. Tester : changer un genre, les années, le top N, l'échelle log. Ouvrir le panneau
   **dependency graph** (barre latérale) pour voir le graphe.

### Code

Dans `platform_chart` :

```python
    .head(top_n_slider.value)                                             # au lieu de .head(10)
    title=f"Top {top_n_slider.value} des plateformes par ventes mondiales",  # titre dynamique
```

Dans la cellule Q2, la zone grisée suit désormais la plage d'années choisie :

```python
# À partir de 2016 la collecte est incomplète : la baisse n'est pas un fait de marché.
if year_end >= 2016:
    yearly_sales_fig.add_vrect(
        x0=max(2015.5, year_start - 0.5),
        x1=year_end + 0.5,
        fillcolor="gray",
        opacity=0.15,
        line_width=0,
        annotation_text="données incomplètes",
    )
```

Dans l'histogramme :

```python
    log_y=log_scale_switch.value,   # au lieu de log_y=False
```

Tableau de données (Markdown + cellule) :

```python
mo.md(r"""
## 12. Les données derrière les graphiques

Le tableau affiche `filtered_df`, la table utilisée par tous les graphiques
(recherche, tri et export intégrés).
""")
```

```python
mo.ui.table(filtered_df, page_size=10, selection=None)
```

Section réactivité (Markdown) :

````python
mo.md(r"""
## 13. Comprendre la réactivité

Marimo repère, pour chaque cellule, les variables qu'elle **définit** et celles qu'elle **lit**,
et en déduit un **graphe de dépendances**. Quand un filtre change, seules les cellules
en aval sont ré-exécutées :

```
genre_filter ─┐
year_filter ──┴→ filtered_df ─┬→ kpis
                              ├→ platform_sales (+ top_n_slider) → platform_fig
                              ├→ sales_by_year → yearly_sales_fig
                              ├→ genre_fig
                              ├→ distribution_fig (+ log_scale_switch)
                              ├→ na_eu_fig
                              ├→ genre_region_share → heatmap_fig
                              └→ tableau
```

Règles : une variable globale est définie dans **une seule** cellule ; on ne modifie pas
une variable d'une autre cellule, on en crée une nouvelle (`raw_df` → `clean_df` → `filtered_df`).
L'ordre des cellules à l'écran est libre : c'est le graphe qui fixe l'ordre d'exécution
(les filtres sont affichés en haut, bien qu'ajoutés après les graphiques dans le tutoriel).
""")
````

### Commande

Aucune.

### Résultat attendu

- Ne garder que *Role-Playing* : KPIs, top plateformes (DS et PS en tête), courbe, histogramme,
  scatter et tableau se mettent à jour ensemble.
- Bouger `top_n_slider` : seul le graphique des plateformes change.
- Activer l'échelle log : seul l'histogramme change.

### Point pédagogique

```text
Filtre Genre → filtered_df → platform_sales → platform_fig
```

Marimo construit le graphe à partir des **variables référencées** par les cellules et
ré-exécute **uniquement** les descendants de ce qui a changé. Aucun callback, aucun état
global à synchroniser : c'est le modèle réactif qui fait le travail.

---

## 20. Ajouter la heatmap — bonus

### Objectif

Répondre à la question 6 : *« Quels genres dominent selon les régions ? »* — à traiter
seulement s'il reste du temps.

### Fichiers concernés

`notebooks/videogame_sales.py`

### Action

Markdown, puis une cellule : agrégation genre × région en **parts** (%), puis `px.imshow`.

### Code

Markdown :

```python
mo.md(r"""
## 11. Bonus — Q6 : quels genres dominent selon les régions ?

Deux catégories (genre × région) + une mesure → **heatmap**. On compare des **parts** (%) :
chaque colonne totalise 100 %, sinon l'Amérique du Nord « écraserait » les autres régions.
""")
```

Cellule :

```python
genre_region_share = (
    filtered_df.group_by("Genre")
    .agg(pl.col(REGION_COLUMNS).sum())
    # Une expression appliquée aux 4 colonnes : chaque colonne divisée par son total.
    .with_columns(pl.col(REGION_COLUMNS) / pl.col(REGION_COLUMNS).sum() * 100)
    .sort("Genre")
)

heatmap_fig = px.imshow(
    genre_region_share.select(REGION_COLUMNS).to_numpy(),
    x=["Amérique du Nord", "Europe", "Japon", "Autres"],
    y=genre_region_share["Genre"].to_list(),
    text_auto=".1f",
    aspect="auto",
    color_continuous_scale="Blues",
    labels={"x": "Région", "y": "Genre", "color": "Part (%)"},
    title="Part de chaque genre dans les ventes de la région (%)",
)
heatmap_fig
```

### Commande

Aucune.

### Résultat attendu

Une grille 12 genres × 4 régions. *Role-Playing* ≈ **27,3 %** au Japon contre ≈ 7,5 % ailleurs ;
*Shooter* ≈ 3,0 % au Japon contre ≈ 13 % ailleurs ; *Action* ≈ 20 % en NA/EU.

### Point pédagogique

- Heatmap = **deux dimensions catégorielles** croisées + une mesure codée par la couleur.
- **Normaliser** avant de comparer (parts plutôt que volumes).
- Échelle **séquentielle à une teinte** (`Blues`, pas d'arc-en-ciel).
- Expansion d'expressions Polars : `pl.col([...])` applique la même opération à plusieurs colonnes.
- `px.imshow` attend une matrice : `.to_numpy()` est la seule conversion nécessaire.

---

## 21. Organiser l'application

### Objectif

Étape 7 : ordonner les cellules pour que le notebook se lise comme une histoire et s'affiche
comme une application ; ajouter les tests.

### Fichiers concernés

`notebooks/videogame_sales.py`, `tests/test_pipeline.py`

### Action

1. Vérifier l'ordre des sections (glisser-déposer les cellules si besoin) :

   ```text
   Introduction → Imports → 1. Charger → 2. Explorer → 3. Nettoyer
   → 4. Filtres → 5. KPIs → 6. Q1 plateformes (slider top N) → 7. Q2 années
   → 8. Q3 genres → 9. Q4 histogramme (switch log) → 10. Q5 scatter
   → 11. Q6 heatmap (bonus) → 12. Tableau → 13. Réactivité → 14. Application
   ```

   Chaque section suit le même modèle : **une cellule Markdown** (question, données,
   graphique) puis **une cellule de code** (agréger → visualiser), avec au besoin une petite
   cellule de composant UI entre les deux.

2. Ajouter la cellule de conclusion :

   ````python
   mo.md(r"""
   ## 14. Du notebook à l'application

   ```bash
   marimo edit notebooks/videogame_sales.py   # notebook : code + sorties
   marimo run  notebooks/videogame_sales.py   # application : sorties seules, code masqué
   ```

   **Sources** : [Marimo](https://docs.marimo.io/) · [Polars](https://docs.pola.rs/) ·
   [Plotly Express](https://plotly.com/python/plotly-express/) ·
   [Dataset Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales)
   """)
   ````

3. Créer `tests/test_pipeline.py`. Rien à modifier dans le notebook pour le tester :
   `app.run()` renvoie **toutes** les variables définies par les cellules (y compris
   `platform_fig`, alors que le `return` généré par Marimo ne liste que les variables lues par
   d'autres cellules).

### Code

`tests/test_pipeline.py` :

```python
"""Vérification du pipeline : CSV → DataFrame → clean_df → agrégation → figure.

Lancer depuis la racine du projet :  pytest
"""

from types import SimpleNamespace

import plotly.graph_objects as go
import polars as pl
import pytest

from notebooks.videogame_sales import app, filter_games, platform_chart
from src.data import DATA_PATH, EXPECTED_COLUMNS, SALES_COLUMNS, check_dataset, clean_sales, load_sales

pytestmark = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="data/vgsales.csv absent : voir la section « Télécharger le dataset » du README",
)


# --- src/data.py, testé sans le notebook ------------------------------------


def test_dataset_file_exists():
    assert DATA_PATH.is_file()


def test_load_sales_reads_expected_columns_and_types():
    raw_df = load_sales()
    assert raw_df.columns == EXPECTED_COLUMNS
    assert check_dataset(raw_df) == []
    assert all(raw_df.schema[col].is_float() for col in SALES_COLUMNS)
    assert raw_df.schema["Year"].is_integer()


def test_naive_read_fails_because_of_na_strings():
    # Le problème réel qui justifie null_values="N/A".
    with pytest.raises(pl.exceptions.ComputeError):
        pl.read_csv(DATA_PATH)


def test_clean_sales_removes_only_rows_without_year():
    raw_df = load_sales()
    clean_df = clean_sales(raw_df)
    assert clean_df["Year"].null_count() == 0
    assert clean_df.schema["Year"] == pl.Int32
    assert clean_df.height == raw_df.height - raw_df["Year"].null_count()


def test_check_dataset_detects_missing_and_non_numeric_columns():
    broken_df = pl.DataFrame({"Name": ["x"], "Global_Sales": ["beaucoup"]})
    problems = check_dataset(broken_df)
    assert any("manquantes" in p for p in problems)
    assert any("Global_Sales" in p for p in problems)


# --- Le notebook, exécuté sans navigateur ------------------------------------


@pytest.fixture(scope="module")
def notebook_defs():
    """Exécute toutes les cellules du notebook (valeurs par défaut des filtres)."""
    _outputs, defs = app.run()
    return defs


def test_notebook_aggregations_are_not_empty(notebook_defs):
    assert notebook_defs["filtered_df"].height == notebook_defs["clean_df"].height
    assert notebook_defs["platform_sales"].height == 10
    assert notebook_defs["sales_by_year"].height > 30
    assert notebook_defs["genre_region_share"].height == 12
    assert notebook_defs["kpis"]["global_sales"] > 0


def test_platform_sales_are_sorted_descending(notebook_defs):
    sales = notebook_defs["platform_sales"]["Global_Sales"].to_list()
    assert sales == sorted(sales, reverse=True)


def test_region_shares_sum_to_100(notebook_defs):
    totals = notebook_defs["genre_region_share"].drop("Genre").sum().row(0)
    assert all(total == pytest.approx(100) for total in totals)


def test_na_eu_correlation_is_positive(notebook_defs):
    assert 0 < notebook_defs["na_eu_correlation"] <= 1


@pytest.mark.parametrize(
    "figure_name",
    ["platform_fig", "yearly_sales_fig", "genre_fig", "distribution_fig", "na_eu_fig", "heatmap_fig"],
)
def test_figures_are_built(notebook_defs, figure_name):
    figure = notebook_defs[figure_name]
    assert isinstance(figure, go.Figure)
    assert len(figure.data) >= 1


# --- Réactivité : même cellule, autre valeur de filtre -----------------------


def test_filter_change_propagates_to_aggregation(notebook_defs):
    """Simule un utilisateur qui ne garde que le genre Role-Playing sur 2000–2010.

    `cell.run(**refs)` ré-exécute une cellule nommée en remplaçant ses entrées :
    c'est ce que fait Marimo quand un composant UI change de valeur.
    """
    fake_genre_filter = SimpleNamespace(value=["Role-Playing"])
    fake_year_filter = SimpleNamespace(value=[2000, 2010])

    _output, filter_defs = filter_games.run(genre_filter=fake_genre_filter, year_filter=fake_year_filter)
    filtered_df = filter_defs["filtered_df"]

    assert filtered_df["Genre"].unique().to_list() == ["Role-Playing"]
    assert filtered_df["Year"].min() >= 2000 and filtered_df["Year"].max() <= 2010

    _output, chart_defs = platform_chart.run(filtered_df=filtered_df, top_n_slider=SimpleNamespace(value=5))
    platform_sales = chart_defs["platform_sales"]
    assert platform_sales.height == 5
    assert not platform_sales.equals(notebook_defs["platform_sales"].head(5))
```

### Commande

```bash
marimo check notebooks/videogame_sales.py
pytest
```

### Résultat attendu

`marimo check` ne signale rien ; `pytest` affiche **16 passed**.

### Point pédagogique

- Un notebook Marimo est un module Python : on peut l'**importer** et l'**exécuter**
  (`app.run()`) dans des tests, sans navigateur.
- Une cellule **nommée** peut être relancée seule avec d'autres entrées (`cell.run(...)`) :
  on teste la propagation d'un changement de filtre.
- Construire une **petite application** plutôt qu'un gros notebook d'analyse.

---

## 22. Lancer l'application

### Objectif

Passer du **notebook** à l'**application**.

### Fichiers concernés

`notebooks/videogame_sales.py` (aucune modification)

### Action

Fermer l'éditeur (ou utiliser un autre terminal), lancer le mode application.

### Code

Aucun.

### Commande

```bash
marimo run notebooks/videogame_sales.py
```

Options utiles : `--port 8080`, `--host 0.0.0.0` (réseau local), `--include-code`
(montrer le code aux visiteurs).

### Résultat attendu

Le navigateur s'ouvre sur `http://localhost:2718` (port par défaut, affiché dans le terminal) :
titres, KPIs, filtres, graphiques et tableau, **sans le code**. Les filtres fonctionnent comme
dans l'éditeur.

### Point pédagogique

```text
Notebook (marimo edit) → Application (marimo run)
```

Même fichier, même code : aucune réécriture, aucun framework web supplémentaire.
Chaque visiteur a sa propre session.

---

## 23. Vérifier le résultat

### Objectif

Contrôler que tout le projet est fonctionnel et reproductible.

### Fichiers concernés

Tous.

### Action

Dérouler la checklist.

### Code

Aucun.

### Commande

```bash
python src/data.py                                  # dataset trouvé dans data/ et conforme
marimo check notebooks/videogame_sales.py           # notebook valide
pytest                                              # 16 tests
marimo export html notebooks/videogame_sales.py -o /tmp/export.html   # exécution complète sans navigateur
marimo run notebooks/videogame_sales.py             # application
```

### Résultat attendu

| Vérification | Attendu |
|---|---|
| `python src/data.py` | 16598 lignes brutes, 16327 propres, Structure OK |
| `marimo check` | aucune sortie, code retour 0 |
| `pytest` | 16 passed |
| KPIs (sans filtre) | 16327 · 11360 · 31 · 8820 M |
| Q1 bar chart | PS2 > X360 > PS3 > Wii > DS > PS > GBA > PSP > PS4 > PC |
| Q2 line chart | pic en 2008 (≈ 679 M), zone grisée après 2015 |
| Q3 bar chart | Action (3253) > Sports (2304) > Misc (1710) |
| Q4 histogramme | médiane 0.17 M, longue traîne visible en log |
| Q5 scatter | corrélation 0.77 |
| Q6 heatmap | Role-Playing ≈ 27 % au Japon |
| Filtre genre | tous les graphiques, KPIs et le tableau se mettent à jour |
| Tout désélectionner | avertissement jaune, graphiques non calculés |
| `marimo run` | application sans code, filtres fonctionnels |

Arborescence finale :

```text
marimo-video-games/
├── data/vgsales.csv
├── notebooks/videogame_sales.py
├── src/data.py
├── tests/test_pipeline.py
├── instructions-dev.md
├── README.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

### Point pédagogique

```text
QUESTION → DONNÉES → TRANSFORMATION → VISUALISATION → INTERACTION → APPLICATION
```

Chaque graphique répond à une question ; chaque transformation est justifiée par une
observation des données ; l'interactivité découle du modèle réactif, pas de callbacks.

# Video Game Sales — Marimo Data Visualization

Tutoriel d'**une heure** pour développeurs Python : construire une petite application de
datavisualisation interactive avec **Marimo**, **Polars** et **Plotly Express**, à partir du
dataset Kaggle *Video Game Sales*.

```text
QUESTION → DONNÉES → TRANSFORMATION → VISUALISATION → INTERACTION → APPLICATION
```

> **Une datavisualisation pertinente commence par une question et une compréhension des
> données, puis conduit au choix du graphique approprié.**

---

## Objectif

À la fin du tutoriel, vous saurez :

- ce qu'est Marimo et en quoi il diffère d'un notebook Jupyter ;
- comment fonctionne sa **réactivité** (graphe de dépendances entre cellules) ;
- charger, explorer et nettoyer un CSV avec **Polars** ;
- construire des agrégations avec `group_by(...).agg(...)` ;
- créer des graphiques **Plotly Express** (bar, line, histogram, scatter, heatmap) ;
- rendre l'analyse interactive avec les composants `mo.ui` ;
- transformer le notebook en **application** avec `marimo run`.

Ce n'est pas une application de production : la simplicité et la compréhension priment.

## Dataset

| | |
|---|---|
| Nom | Video Game Sales |
| Page | <https://www.kaggle.com/datasets/gregorut/videogamesales> |
| Auteur | GregorySmith (`gregorut`), version 2 |
| Origine | scraping de [vgchartz.com](https://www.vgchartz.com/) ([script](https://github.com/GregorUT/vgchartzScrape)) |
| Fichier | `vgsales.csv` — 16 598 lignes, 11 colonnes, 1 355 781 octets |
| Licence | **« Unknown »** selon les métadonnées Kaggle (vérifié le 27/09/2026) |

**Conditions d'utilisation** : la licence n'étant pas précisée, reportez-vous à la
[page Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales) et aux conditions
d'utilisation de Kaggle et de vgchartz.com. Par prudence, le CSV **n'est pas versionné**
(`data/*.csv` est dans `.gitignore`) : chaque participant le télécharge depuis Kaggle.
Usage ici : pédagogique, non commercial.

Colonnes :

| Colonne | Type Polars | Description |
|---|---|---|
| `Rank` | i64 | rang selon les ventes mondiales |
| `Name` | str | nom du jeu |
| `Platform` | str | plateforme (PS2, Wii, PC…) |
| `Year` | i64 (nullable) | année de sortie |
| `Genre` | str | genre (12 valeurs) |
| `Publisher` | str (nullable) | éditeur |
| `NA_Sales`, `EU_Sales`, `JP_Sales`, `Other_Sales` | f64 | ventes par région, **en millions d'unités** |
| `Global_Sales` | f64 | ventes mondiales, en millions d'unités |

Une ligne = **un jeu sur une plateforme** (16 598 lignes, mais 11 493 titres distincts).

## Architecture

```text
                     ┌─────────────────┐
                     │   Kaggle CSV    │  data/vgsales.csv
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │     Polars      │  src/data.py
                     │ Load / Clean    │  load_sales() · clean_sales() · check_dataset()
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │     Marimo      │  notebooks/videogame_sales.py
                     │ Reactive cells  │
                     └────────┬────────┘
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
             KPI / stats   Filtres     Agrégations
             (mo.stat)    (mo.ui.*)   (group_by/agg)
                 └────────────┼────────────┘
                              ▼
                     ┌─────────────────┐
                     │     Plotly      │  plotly.express
                     │ Interactive viz │
                     └─────────────────┘
```

**Répartition du code** :

- `src/data.py` : chargement, nettoyage, validation. Court, **testable sans le notebook**
  (`pytest`), exécutable seul (`python src/data.py`) pour vérifier le dataset avant une démo.
- `notebooks/videogame_sales.py` : **le cœur du tutoriel** — exploration, filtres,
  agrégations et graphiques, écrits explicitement, cellule par cellule. Chaque section suit
  le même modèle : **une cellule Markdown** (la question) puis **une cellule de code**
  (agréger avec Polars → visualiser avec Plotly).

## Stack technique

| Outil | Version vérifiée | Rôle |
|---|---|---|
| Python | 3.11.5 (≥ 3.11 requis) | langage |
| [Marimo](https://docs.marimo.io/) | 0.25.0 | notebook réactif, composants UI, mode application |
| [Polars](https://docs.pola.rs/) | 1.44.2 | chargement CSV, nettoyage, agrégations |
| [Plotly](https://plotly.com/python/) (`plotly[express]`) | 7.1.0 | graphiques interactifs |
| numpy | 2.4.6 (installé par `plotly[express]`) | requis par Plotly Express |
| pytest | 9.1.1 (optionnel) | vérification du pipeline |

**Pas de pandas.** Plotly Express (≥ 6) et `mo.ui.table` acceptent directement un DataFrame
Polars (via la bibliothèque [narwhals](https://narwhals-dev.github.io/narwhals/)).

**Attention** : `pip install plotly` seul ne suffit pas. Sans numpy,
`import plotly.express` lève `ImportError: Plotly Express requires numpy`. Installez
`plotly[express]`, comme l'indique la [documentation Plotly](https://plotly.com/python/getting-started/).

### Pourquoi Polars ici ?

Polars est utilisé là où il apporte une vraie valeur pédagogique :

- `pl.read_csv(..., null_values="N/A")` rend explicite la gestion des valeurs manquantes ;
- `group_by(...).agg(...)` exprime chaque agrégation comme une phrase lisible ;
- les **expressions** (`pl.col`, `pl.len()`, `.n_unique()`, `pl.corr`) calculent tous les KPIs
  en une seule requête ;
- une expression sur plusieurs colonnes (`pl.col(REGION_COLUMNS) / pl.col(REGION_COLUMNS).sum()`)
  calcule les parts régionales de la heatmap en une ligne.

Ce qui ne passe **pas** par Polars, et pourquoi :

- la mise en forme des graphiques (titres, axes, zone grisée, ligne médiane) relève de Plotly ;
- `px.imshow` attend une **matrice** : on convertit la table genre × région avec `.to_numpy()` ;
- les petites manipulations Python (`sorted(...)`, f-strings) restent en Python pur.

## Prérequis

- Python **3.11 ou plus** (`python --version`) ;
- un compte Kaggle (gratuit) pour télécharger le dataset ;
- un navigateur récent ;
- connaissances Python de base. Aucune connaissance de Marimo, Polars ou Plotly n'est requise.

## Installation

Depuis la racine du projet (`marimo-video-games/`) :

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Alternative avec [uv](https://docs.astral.sh/uv/) : `uv sync` (lit `pyproject.toml`).

## Télécharger le dataset

Le CSV n'est pas fourni dans le dépôt git.

**Option A — navigateur**

1. Ouvrir <https://www.kaggle.com/datasets/gregorut/videogamesales> et se connecter.
2. Cliquer sur **Download** : on obtient une archive ZIP contenant `vgsales.csv`.
3. Extraire `vgsales.csv` dans `data/` → `data/vgsales.csv`.

> **Emplacement** : le code attend le fichier exactement à `data/vgsales.csv`
> (constante `DATA_PATH` dans `src/data.py`). Un CSV laissé à la racine du projet ou dans le
> dossier parent n'est pas trouvé.

**Option B — CLI Kaggle** (nécessite un jeton API Kaggle, voir la
[documentation Kaggle API](https://github.com/Kaggle/kaggle-api)) :

```bash
pip install kaggle
kaggle datasets download -d gregorut/videogamesales -p data --unzip
```

**Vérifier** :

```bash
python src/data.py
```

```text
Fichier       : .../marimo-video-games/data/vgsales.csv
Lignes brutes : 16598
Lignes propres: 16327 (271 sans année écartées)
Structure     : OK
```

Si le fichier manque, le notebook affiche un message rouge avec le lien de téléchargement
au lieu de planter (`mo.stop`).

## Lancer Marimo

```bash
marimo edit notebooks/videogame_sales.py   # mode notebook (édition)
marimo run  notebooks/videogame_sales.py   # mode application (lecture seule, code masqué)
pytest                                     # vérification du pipeline (16 tests)
```

Les commandes fonctionnent quel que soit le répertoire courant : le chemin du CSV est
calculé à partir de l'emplacement des fichiers (`pathlib` + `mo.notebook_dir()`).

## Comprendre le notebook

Un notebook Marimo est un **fichier Python pur** : chaque cellule est une fonction décorée
par `@app.cell`, dont les paramètres sont les variables lues et le `return` les variables
définies. Marimo génère ce format : dans l'éditeur, on écrit seulement le corps des cellules.

| Section | Contenu | Variables clés |
|---|---|---|
| Introduction | dataset, pipeline, les 6 questions | — |
| Imports | `marimo`, `polars`, `plotly.express`, `src.data` ; style `px.defaults` ; noms d'axes | `mo`, `pl`, `px`, `LABELS` |
| 1. Charger | `load_sales()` (+ `mo.stop` si le CSV manque) | `raw_df` |
| 2. Explorer | `describe()` + observations | — |
| 3. Nettoyer | tableau des décisions, `clean_sales()` | `clean_df` |
| 4. Filtres | multiselect genres + range slider années | `genre_filter`, `year_filter`, `filtered_df` |
| 5. KPIs | `mo.stat` | `kpis` |
| 6–11. Questions 1 à 6 | une cellule par question : agrégation Polars → figure Plotly | `platform_sales`, `sales_by_year`, … |
| 12. Données | `mo.ui.table(filtered_df)` | — |
| 13. Réactivité | graphe de dépendances, règles | — |
| 14. Application | `marimo run`, sources | — |

Deux choix gardent le notebook court et lisible :

- **`px.defaults`** fixe une seule fois le thème et la couleur de tous les graphiques ;
- **`LABELS`** (dictionnaire défini dans la cellule d'imports) nomme les axes avec leurs unités :
  chaque graphique passe simplement `labels=LABELS`.

### Différences avec Jupyter

| Jupyter | Marimo |
|---|---|
| fichier `.ipynb` (JSON) | fichier `.py` (diff git lisible, importable) |
| exécution manuelle, dans l'ordre choisi | exécution **automatique** des cellules dépendantes |
| état caché possible (cellule supprimée, variable toujours en mémoire) | pas d'état caché : supprimer une cellule supprime ses variables |
| widgets + callbacks (`ipywidgets`) | `mo.ui.*` : la valeur est une variable Python, pas de callback |
| app = outil supplémentaire (Voilà, Streamlit…) | `marimo run` sur le même fichier |

## Exploration des données

*Avant de visualiser, comprendre la structure des données.* Problèmes **réellement**
constatés dans `vgsales.csv` :

| Constat | Détail |
|---|---|
| `N/A` textuels | `pl.read_csv` sans option échoue : `could not parse "N/A" as dtype i64 at column 'Year'` |
| `Year` manquante | 271 lignes (100,1 M d'unités, 1,1 % des ventes) |
| `Publisher` manquant | 58 lignes |
| Années récentes incomplètes | 614 jeux en 2015, 344 en 2016, **3 en 2017**, **1 en 2020** |
| Doublons (Name, Platform, Year) | 2 paires : *Madden NFL 13* (PS3, 2012), *Wii de Asobu: Metroid Prime* (Wii, sans année) |
| Distribution très asymétrique | médiane 0,17 M, moyenne 0,54 M, max 82,74 M (*Wii Sports*) |
| Arrondis | `Global_Sales` ≈ somme des 4 régions (écart max 0,02 M, dû aux arrondis) |

## Transformation avec Polars

Nettoyage minimal et justifié (`src/data.py`) :

```python
raw_df = pl.read_csv(DATA_PATH, null_values="N/A")        # "N/A" → null
clean_df = (
    raw_df
    .filter(pl.col("Year").is_not_null())                  # 271 lignes sans année écartées
    .with_columns(pl.col("Year").cast(pl.Int32))            # année = entier
)
```

On **ne remplace pas** les années manquantes par 0 ou par une moyenne : cela créerait de
fausses années. Les doublons sont conservés ; les années 2016 à 2020, incomplètes, sont
conservées et grisées sur le graphique temporel.

Cellule type (question 1) — agréger, puis visualiser :

```python
# 1) Agréger : filtered_df → platform_sales
platform_sales = (
    filtered_df.group_by("Platform")
    .agg(pl.col("Global_Sales").sum(), pl.len().alias("Games"))
    .sort("Global_Sales", descending=True)
    .head(top_n_slider.value)
)

# 2) Visualiser : platform_sales → platform_fig
platform_fig = px.bar(platform_sales, x="Platform", y="Global_Sales", labels=LABELS, ...)
```

## Visualisations Plotly

| # | Question | Données | Graphique | Fonction |
|---|---|---|---|---|
| 1 | Quelles plateformes ont généré le plus de ventes ? | catégorie + mesure | Bar chart | `px.bar` |
| 2 | Comment les ventes évoluent-elles au fil des années ? | année + mesure | Line chart | `px.line` |
| 3 | Quels genres sont les plus représentés ? | catégorie + comptage | Bar chart horizontal | `px.bar(orientation="h")` |
| 4 | Comment les ventes par jeu sont-elles distribuées ? | variable numérique | Histogramme | `px.histogram` |
| 5 | Les ventes NA et EU sont-elles liées ? | numérique + numérique | Scatter plot | `px.scatter` |
| 6 *(bonus)* | Quels genres dominent selon les régions ? | 2 catégories + mesure | Heatmap | `px.imshow` |

Tableau de choix, à retenir :

| Question | Données | Graphique |
| --- | --- | --- |
| Comparer des plateformes | catégorie + mesure | Bar chart |
| Voir une évolution | année + mesure | Line chart |
| Comprendre une distribution | variable numérique | Histogram |
| Chercher une relation | numérique + numérique | Scatter plot |
| Comparer deux dimensions | catégories + mesure | Heatmap |

> **Le graphique est choisi en fonction de la question et de la nature des données.**

Points de lecture à souligner pendant la démo :

- **Bar vs histogramme** : un bar chart compare des catégories ; un histogramme montre la
  distribution d'une variable numérique découpée en intervalles.
- **Line chart** : `Global_Sales` est un total **sur la vie du jeu**. La courbe montre les ventes
  des jeux *sortis* chaque année ; la chute après 2015 est largement un artefact de collecte
  (zone grisée).
- **Scatter** : corrélation NA/EU ≈ **0,77** sur l'ensemble des données. **Corrélation ≠ causalité** :
  un facteur commun (la popularité du jeu) explique les deux.
- **Heatmap** : on compare des **parts** (%), pas des volumes. Le *Role-Playing* pèse ~27 % des
  ventes au Japon contre ~7,5 % ailleurs ; le *Shooter* ~3 % au Japon contre ~13 % ailleurs.

### Bonnes pratiques appliquées

- titres explicites, axes nommés **avec unités** (millions d'unités), centralisés dans `LABELS` ;
- bar charts **triés** et **limités** (top N) ;
- une seule couleur quand la couleur ne porte pas d'information ; échelle séquentielle à une
  teinte (`Blues`) pour la heatmap ; pas d'arc-en-ciel ;
- pas de camembert pour comparer 12 genres (angles difficiles à comparer) ;
- pas de `color="Genre"` sur le scatter : 12 couleurs sur 16 000 points ne se lisent pas ;
- informations au survol (nombre de jeux, nom du jeu…) ;
- distinguer **comparaison**, **évolution**, **distribution** et **relation**.

## Interactivité avec Marimo

| Composant | Variable | Effet |
|---|---|---|
| `mo.ui.multiselect` | `genre_filter` | genres inclus |
| `mo.ui.range_slider` | `year_filter` | plage d'années de sortie |
| `mo.ui.slider` | `top_n_slider` | nombre de plateformes du bar chart |
| `mo.ui.switch` | `log_scale_switch` | échelle log de l'histogramme |
| `mo.ui.table` | — | recherche, tri, filtres, export de `filtered_df` |

```python
genre_filter = mo.ui.multiselect(options=all_genres, value=all_genres, label="Genres")
```

```python
# Dans une AUTRE cellule : lire .value suffit à créer la dépendance.
filtered_df = clean_df.filter(
    pl.col("Genre").is_in(genre_filter.value),
    pl.col("Year").is_between(year_start, year_end),
)
```

Un composant UI doit être **défini dans une cellule** et sa `.value` **lue dans une autre**.

## Réactivité

```text
Utilisateur → Composant UI → Variable Python → DataFrame filtré → Agrégation → Graphique
```

```text
genre_filter ─┐
year_filter ──┴→ filtered_df ─┬→ kpis
                              ├→ platform_sales (+ top_n_slider) → platform_fig
                              ├→ sales_by_year → yearly_sales_fig
                              ├→ genre_fig
                              ├→ distribution_fig (+ log_scale_switch)
                              ├→ na_eu_fig
                              ├→ genre_region_share → heatmap_fig
                              └→ table
```

Marimo analyse chaque cellule (variables **définies** et **lues**) et construit un graphe de
dépendances. Quand `genre_filter` change, il ré-exécute `filtered_df`, puis `platform_sales`,
puis `platform_fig`, etc. **Seules** les cellules en aval sont relancées : bouger `top_n_slider`
ne relance ni le chargement, ni le filtre.

Règles qui en découlent :

- une variable globale est définie dans **une seule** cellule ;
- les noms préfixés par `_` sont locaux à la cellule ;
- on ne modifie pas un objet d'une autre cellule, on crée une nouvelle variable ;
- l'ordre des cellules à l'écran est libre (les filtres sont affichés en haut, bien qu'ajoutés
  en fin de tutoriel) ;
- `mo.stop(condition, message)` interrompt une cellule et ses dépendantes (fichier absent,
  filtre vide).

Dans l'éditeur, le panneau **dependency graph** de la barre latérale affiche ce graphe.

## Passer du notebook à l'application

```bash
marimo run notebooks/videogame_sales.py
```

Même fichier, même code. En mode `run`, Marimo sert **uniquement les sorties** (code masqué,
non modifiable) : titres, KPIs, filtres, graphiques, tableau. Chaque visiteur a sa propre
session et ses propres filtres. Options utiles : `--port 8080`, `--host 0.0.0.0`,
`--include-code` (afficher le code). Voir [Run as an app](https://docs.marimo.io/guides/apps/).

## Structure du projet

```text
marimo-video-games/
├── data/
│   └── vgsales.csv              # à télécharger depuis Kaggle (non versionné)
├── notebooks/
│   └── videogame_sales.py       # le notebook / l'application Marimo
├── src/
│   └── data.py                  # load_sales, clean_sales, check_dataset
├── tests/
│   └── test_pipeline.py         # CSV → DataFrame → clean_df → agrégation → figure
├── instructions-dev.md          # reconstruire le projet pas à pas
├── README.md
├── pyproject.toml
├── requirements.txt             # versions exactes vérifiées
└── .gitignore
```

## Déroulé en 60 minutes

| Temps | Séquence | Contenu |
|---|---|---|
| 0–5 min | Introduction | Marimo vs Jupyter, dataset, architecture, les 6 questions |
| 5–15 min | Installation & premier notebook | venv, `pip install`, `marimo edit`, Hello World réactif avec un slider |
| 15–25 min | Exploration | `read_csv` qui échoue puis `null_values="N/A"`, `describe()`, années incomplètes, `clean_df` |
| 25–40 min | Datavisualisation | KPIs ; bar (Q1, + Q3 en variante), line (Q2), histogram (Q4), scatter (Q5) |
| 40–50 min | Interactivité | filtres genre/années, `filtered_df`, slider top N, switch log, graphe de dépendances |
| 50–55 min | Application | `marimo run`, tableau de données |
| 55–60 min | Synthèse | Question → Données → Transformation → Visualisation → Interaction ; heatmap si le temps le permet |

La **heatmap** (Q6) est un bonus : à montrer uniquement s'il reste du temps.

## Limites

- **Licence** : « Unknown » sur Kaggle. Données non redistribuées dans ce dépôt.
- **Fraîcheur** : données scrapées vers 2016 ; 2016 est partielle et 2017/2020 quasi vides.
- **Seuil de ventes** : Kaggle annonce des jeux à plus de 100 000 exemplaires, mais le fichier
  contient des `Global_Sales` à 0,01 M (10 000). On travaille avec les données telles quelles.
- **Définition des ventes** : estimations publiées par vgchartz, cumulées sur la vie du jeu,
  sans ventilation par année de vente.
- **Unité d'analyse** : une ligne = un jeu × une plateforme. Un titre multi-plateforme compte
  plusieurs fois dans « nombre de jeux ».
- **Nettoyage minimal** : doublons conservés ; 271 lignes sans année exclues de toute l'analyse
  (y compris des graphiques non temporels, pour garder une seule table filtrée cohérente).
- **Tests** : les tests vérifient le pipeline et la propagation d'un changement de filtre
  (`cell.run()`), pas le rendu visuel dans le navigateur.

## Sources

Documentation officielle (liens vérifiés le 27/09/2026) :

- **Marimo** — <https://docs.marimo.io/>
  - Réactivité : <https://docs.marimo.io/guides/reactivity/>
  - Interactivité (`mo.ui`) : <https://docs.marimo.io/guides/interactivity/>
  - Composants d'entrée : <https://docs.marimo.io/api/inputs/>
  - Mise en page (`hstack`, `vstack`…) : <https://docs.marimo.io/api/layouts/>
  - `mo.stop` : <https://docs.marimo.io/api/control_flow/>
  - `mo.notebook_dir` : <https://docs.marimo.io/api/miscellaneous/>
  - Mode application : <https://docs.marimo.io/guides/apps/>
  - Tests : <https://docs.marimo.io/guides/testing/>
  - Venir de Jupyter : <https://docs.marimo.io/guides/coming_from/jupyter/>
- **Polars** — <https://docs.pola.rs/>
  - Lecture CSV : <https://docs.pola.rs/user-guide/io/csv/> ·
    [`read_csv`](https://docs.pola.rs/api/python/stable/reference/api/polars.read_csv.html)
  - Agrégations : <https://docs.pola.rs/user-guide/expressions/aggregation/>
  - Expansion d'expressions (plusieurs colonnes) : <https://docs.pola.rs/user-guide/expressions/expression-expansion/>
- **Plotly Python** — <https://plotly.com/python/> · installation : <https://plotly.com/python/getting-started/>
  - Plotly Express : <https://plotly.com/python/plotly-express/>
  - [Bar](https://plotly.com/python/bar-charts/) · [Line](https://plotly.com/python/line-charts/) ·
    [Histogram](https://plotly.com/python/histograms/) · [Scatter](https://plotly.com/python/line-and-scatter/) ·
    [Heatmap `imshow`](https://plotly.com/python/imshow/)
- **Dataset** — <https://www.kaggle.com/datasets/gregorut/videogamesales> (source primaire :
  <https://www.vgchartz.com/>)

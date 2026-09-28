import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Video Game Sales — Marimo")


@app.cell
def _(mo):
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
    return


@app.cell
def _():
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
    LABELS = {
        "Platform": "Plateforme",
        "Genre": "Genre",
        "Year": "Année de sortie",
        "Games": "Nombre de jeux",
        "Global_Sales": "Ventes mondiales (millions d'unités)",
        "NA_Sales": "Ventes Amérique du Nord (millions d'unités)",
        "EU_Sales": "Ventes Europe (millions d'unités)",
    }
    return (
        DATA_PATH,
        LABELS,
        REGION_COLUMNS,
        SALES_COLUMNS,
        clean_sales,
        load_sales,
        mo,
        pl,
        px,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Charger les données

    `load_sales()` (dans `src/data.py`) lit le CSV avec `pl.read_csv(path, null_values="N/A")`.
    Sans `null_values="N/A"`, Polars échoue : le fichier écrit les valeurs manquantes
    sous forme de texte `N/A`, que la colonne `Year` (entière) ne peut pas lire.
    """)
    return


@app.cell
def _(DATA_PATH, load_sales, mo):
    # mo.stop arrête la cellule (et ses dépendantes) si le fichier est absent.
    mo.stop(
        not DATA_PATH.exists(),
        mo.callout(mo.md("**Dataset introuvable** : placez `vgsales.csv` dans `data/` (voir README)."), kind="danger"),
    )

    raw_df = load_sales(DATA_PATH)
    raw_df
    return (raw_df,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Explorer — *avant de visualiser, comprendre les données*

    `describe()` donne, pour chaque colonne numérique, le nombre de valeurs, de nulls,
    la moyenne, la médiane (`50%`), le min et le max.
    """)
    return


@app.cell
def _(SALES_COLUMNS, raw_df):
    raw_df.select("Year", *SALES_COLUMNS).describe()
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Ce que l'on observe :**

    - `Year` a **271 valeurs nulles** et va jusqu'à 2020, mais la collecte s'arrête vers 2016
      (344 jeux en 2016, 3 en 2017, 1 en 2020, contre ~600 par an avant) ;
    - `Global_Sales` : **médiane 0,17 M**, moyenne 0,54 M, maximum **82,74 M** (*Wii Sports*) :
      quelques énormes succès, une majorité de petits scores.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Nettoyer — uniquement ce qui est nécessaire

    | Problème | Décision | Pourquoi |
    |---|---|---|
    | `Year` nulle (271 lignes) | lignes **écartées** | inventer une année fausserait les courbes |
    | 2016 → 2020 incomplètes | **conservées**, signalées | on grise la zone sur le graphique |
    | `Publisher` nul (58 lignes) | **conservé** | colonne non utilisée |
    """)
    return


@app.cell
def _(clean_sales, mo, raw_df):
    clean_df = clean_sales(raw_df)

    mo.md(f"`clean_df` : **{clean_df.height} lignes** ({raw_df.height - clean_df.height} lignes sans année écartées).")
    return (clean_df,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Filtres interactifs

    Un composant `mo.ui.*` est une **variable Python** : toute cellule qui lit sa `.value`
    est ré-exécutée automatiquement quand l'utilisateur interagit — **sans callback**.
    """)
    return


@app.cell
def _(clean_df, mo):
    all_genres = sorted(clean_df["Genre"].unique().to_list())
    first_year, last_year = int(clean_df["Year"].min()), int(clean_df["Year"].max())

    genre_filter = mo.ui.multiselect(options=all_genres, value=all_genres, label="Genres", full_width=True)
    year_filter = mo.ui.range_slider(
        start=first_year, stop=last_year, value=[first_year, last_year], label="Années de sortie", show_value=True
    )

    mo.hstack([genre_filter, year_filter], widths=[2, 1], gap=2)
    return genre_filter, year_filter


@app.cell
def filter_games(clean_df, genre_filter, mo, pl, year_filter):
    # Cette cellule lit les deux filtres : elle est relancée à chaque modification.
    year_start, year_end = (int(year) for year in year_filter.value)

    filtered_df = clean_df.filter(
        pl.col("Genre").is_in(genre_filter.value),
        pl.col("Year").is_between(year_start, year_end),
    )

    mo.stop(filtered_df.is_empty(), mo.callout("Aucun jeu ne correspond : sélectionnez au moins un genre.", kind="warn"))
    mo.md(f"🔁 `filtered_df` : **{filtered_df.height} lignes** sur {clean_df.height}. Toutes les cellules suivantes en dépendent.")
    return filtered_df, year_end, year_start


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Indicateurs clés
    """)
    return


@app.cell
def _(filtered_df, mo, pl):
    # Tous les KPIs en une seule requête Polars : une expression par indicateur.
    kpis = filtered_df.select(
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
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. Q1 — Quelles plateformes ont généré le plus de ventes ?

    Catégorie + mesure → **bar chart**, trié et limité aux N premières :
    `group_by(...).agg(...)` puis `sort(...)` puis `head(N)`.
    """)
    return


@app.cell
def _(mo):
    top_n_slider = mo.ui.slider(start=5, stop=20, value=10, label="Nombre de plateformes", show_value=True)
    top_n_slider
    return (top_n_slider,)


@app.cell
def platform_chart(LABELS, filtered_df, pl, px, top_n_slider):
    # 1) Agréger : filtered_df → platform_sales
    platform_sales = (
        filtered_df.group_by("Platform")
        .agg(pl.col("Global_Sales").sum(), pl.len().alias("Games"))
        .sort("Global_Sales", descending=True)
        .head(top_n_slider.value)
    )

    # 2) Visualiser : platform_sales → platform_fig
    platform_fig = px.bar(
        platform_sales,
        x="Platform",
        y="Global_Sales",
        text_auto=".0f",
        hover_data=["Games"],
        labels=LABELS,
        title=f"Top {top_n_slider.value} des plateformes par ventes mondiales",
    )
    platform_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Q2 — Comment les ventes évoluent-elles au fil des années ?

    Année (ordonnée) + mesure → **line chart**. ⚠️ `Global_Sales` est le total des ventes
    d'un jeu **sur toute sa vie** : la courbe montre les ventes des jeux **sortis** chaque année.
    """)
    return


@app.cell
def _(LABELS, filtered_df, pl, px, year_end, year_start):
    sales_by_year = (
        filtered_df.group_by("Year")
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
    if year_end >= 2016:
        yearly_sales_fig.add_vrect(
            x0=max(2015.5, year_start - 0.5),
            x1=year_end + 0.5,
            fillcolor="gray",
            opacity=0.15,
            line_width=0,
            annotation_text="données incomplètes",
        )
    yearly_sales_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8. Q3 — Quels genres sont les plus représentés ?

    « Représenté » = **nombre de jeux** : on **compte** (`pl.len()`) au lieu de **sommer**.
    Barres horizontales pour que les noms de genres restent lisibles.
    """)
    return


@app.cell
def _(LABELS, filtered_df, pl, px):
    genre_counts = filtered_df.group_by("Genre").agg(pl.len().alias("Games")).sort("Games")

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
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 9. Q4 — Comment les ventes par jeu sont-elles distribuées ?

    Une variable numérique → **histogramme**. Un bar chart compare des **catégories** ;
    un histogramme montre la **distribution** d'une valeur découpée en intervalles.
    La distribution est très asymétrique : activez l'échelle log pour voir la « longue traîne ».
    """)
    return


@app.cell
def _(mo):
    log_scale_switch = mo.ui.switch(label="Échelle logarithmique (axe Y)")
    log_scale_switch
    return (log_scale_switch,)


@app.cell
def _(LABELS, filtered_df, log_scale_switch, px):
    median_sales = filtered_df["Global_Sales"].median()

    distribution_fig = px.histogram(
        filtered_df,
        x="Global_Sales",
        nbins=100,
        log_y=log_scale_switch.value,
        labels=LABELS,
        title="Distribution des ventes mondiales par jeu",
    )
    distribution_fig.add_vline(x=median_sales, line_dash="dash", annotation_text=f"médiane : {median_sales:.2f} M")
    distribution_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 10. Q5 — Les ventes en Amérique du Nord et en Europe sont-elles liées ?

    Deux variables numériques → **scatter plot** (un point = un jeu), complété par le
    **coefficient de corrélation de Pearson** calculé avec Polars.
    """)
    return


@app.cell
def _(LABELS, filtered_df, mo, pl, px):
    na_eu_correlation = filtered_df.select(pl.corr("NA_Sales", "EU_Sales")).item()

    na_eu_fig = px.scatter(
        filtered_df,
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
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 11. Bonus — Q6 : quels genres dominent selon les régions ?

    Deux catégories (genre × région) + une mesure → **heatmap**. On compare des **parts** (%) :
    chaque colonne totalise 100 %, sinon l'Amérique du Nord « écraserait » les autres régions.
    """)
    return


@app.cell
def _(REGION_COLUMNS, filtered_df, pl, px):
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
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 12. Les données derrière les graphiques

    Le tableau affiche `filtered_df`, la table utilisée par tous les graphiques
    (recherche, tri et export intégrés).
    """)
    return


@app.cell
def _(filtered_df, mo):
    mo.ui.table(filtered_df, page_size=10, selection=None)
    return


@app.cell
def _(mo):
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
    return


@app.cell
def _(mo):
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
    return


if __name__ == "__main__":
    app.run()

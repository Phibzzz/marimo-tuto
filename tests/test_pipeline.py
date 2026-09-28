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

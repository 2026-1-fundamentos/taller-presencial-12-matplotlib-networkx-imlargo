"""Plot a collaboration network between countries."""

from __future__ import annotations

import itertools
import os
from collections import Counter
from typing import Iterable

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

DATA_URL = (
    "https://raw.githubusercontent.com/jdvelasq/datalabs/master/datasets/"
    "scopus-papers.csv"
)


def _split_countries(values: Iterable[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for value in values:
        if not isinstance(value, str):
            continue
        countries: set[str] = set()
        for affiliation in value.split(";"):
            if not affiliation.strip():
                continue
            country = affiliation.split(",")[-1].strip()
            if country:
                countries.add(country)
        if countries:
            rows.append(sorted(countries))
    return rows


def make_plot(n_countries: int = 20) -> None:
    """Builds the country collaboration outputs in the files/ folder."""

    os.makedirs("files", exist_ok=True)

    dataframe = pd.read_csv(DATA_URL)
    country_lists = _split_countries(dataframe["Affiliations"])

    country_counts: Counter[str] = Counter()
    for countries in country_lists:
        country_counts.update(countries)

    top_counts = country_counts.most_common(n_countries)
    top_countries = {name for name, _ in top_counts}

    countries_df = pd.DataFrame(top_counts, columns=["countries", "count"])
    countries_df.to_csv("files/countries.csv", index=False)

    edge_counts: Counter[tuple[str, str]] = Counter()
    for countries in country_lists:
        filtered = sorted({c for c in countries if c in top_countries})
        if len(filtered) < 2:
            continue
        for left, right in itertools.combinations(filtered, 2):
            edge_counts[(left, right)] += 1

    edges_df = pd.DataFrame(
        [(left, right, weight) for (left, right), weight in edge_counts.items()],
        columns=["source", "target", "weight"],
    ).sort_values(by="weight", ascending=False)
    edges_df.to_csv("files/co_occurrences.csv", index=False)

    graph = nx.Graph()
    for country, count in top_counts:
        graph.add_node(country, count=count)
    for (left, right), weight in edge_counts.items():
        graph.add_edge(left, right, weight=weight)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42)
    node_sizes = [graph.nodes[node]["count"] * 5 for node in graph.nodes]
    nx.draw_networkx(
        graph,
        pos=pos,
        node_size=node_sizes,
        with_labels=True,
        font_size=8,
        edge_color="#6d6d6d",
        node_color="#4c72b0",
    )
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("files/network.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    make_plot()

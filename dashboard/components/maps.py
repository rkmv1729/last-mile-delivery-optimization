import random

import h3
import pandas as pd


def build_color_palette(
    values,
) -> dict:
    """
    Generate a deterministic color palette for unique values.

    Parameters
    ----------
    values
        Iterable containing unique values such as zone IDs.

    Returns
    -------
    dict
        Mapping:
            value -> [R, G, B, A]
    """

    random.seed(42)

    palette = {}

    for value in sorted(values):

        palette[value] = [
            random.randint(40, 230),
            random.randint(40, 230),
            random.randint(40, 230),
            180,
        ]

    return palette




def build_h3_polygons(
    dataframe: pd.DataFrame,
    color_column: str,
) -> pd.DataFrame:
    """
    Convert H3 cells into polygon records for visualization.

    Parameters
    ----------
    dataframe
        DataFrame containing:
            - h3_cell_8
            - color_column
            - any additional metadata

    color_column
        Column used to assign polygon colors.

    Returns
    -------
    pd.DataFrame
        Original dataframe with additional columns:
            - polygon
            - color
    """

    palette = build_color_palette(
        dataframe[color_column].unique()
    )

    polygon_rows = []

    for row in dataframe.itertuples(index=False):

        boundary = h3.cell_to_boundary(
            row.h3_cell_8
        )

        polygon = [
            [lng, lat]
            for lat, lng in boundary
        ]

        record = row._asdict()

        record["polygon"] = polygon

        record["color"] = palette[
            record[color_column]
        ]

        polygon_rows.append(record)

    return pd.DataFrame(polygon_rows)


import pydeck as pdk


def build_view_state(
    polygon_df: pd.DataFrame,
) -> pdk.ViewState:
    """
    Compute the initial map view from H3 polygons.

    Parameters
    ----------
    polygon_df
        DataFrame returned by build_h3_polygons().

    Returns
    -------
    pdk.ViewState
        Initial camera position.
    """

    latitudes = []
    longitudes = []

    for polygon in polygon_df["polygon"]:

        for lng, lat in polygon:

            longitudes.append(lng)
            latitudes.append(lat)

    return pdk.ViewState(
        latitude=sum(latitudes) / len(latitudes),
        longitude=sum(longitudes) / len(longitudes),
        zoom=10,
        pitch=0,
    )



import streamlit as st


def draw_h3_map(
    dataframe: pd.DataFrame,
    color_column: str,
    tooltip: dict,
):
    """
    Render an interactive H3 polygon map.

    Parameters
    ----------
    dataframe
        Input dataframe containing:
            - h3_cell_8
            - color_column
            - tooltip fields

    color_column
        Column used for coloring polygons.

    tooltip
        PyDeck tooltip configuration.
    """

    polygon_df = build_h3_polygons(
        dataframe=dataframe,
        color_column=color_column,
    )

    layer = pdk.Layer(
        "PolygonLayer",
        data=polygon_df,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=build_view_state(
            polygon_df
        ),
        tooltip=tooltip,
    )

    st.pydeck_chart(
        deck,
        use_container_width=True,
    )
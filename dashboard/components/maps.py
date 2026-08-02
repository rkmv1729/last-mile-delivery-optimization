import random
import streamlit as st
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

def build_heat_color(
    value: float,
    minimum: float,
    maximum: float,
):
    """
    Continuous Blue → Green → Yellow → Red color scale.
    """

    if maximum == minimum:
        t = 0.5
    else:
        t = (value - minimum) / (maximum - minimum)

    t = max(0.0, min(1.0, t))

    if t < 0.33:

        p = t / 0.33

        r = 0
        g = int(255 * p)
        b = 255

    elif t < 0.66:

        p = (t - 0.33) / 0.33

        r = int(255 * p)
        g = 255
        b = int(255 * (1 - p))

    else:

        p = (t - 0.66) / 0.34

        r = 255
        g = int(255 * (1 - p))
        b = 0

    return [r, g, b, 180]




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

    numeric_heatmap = (
        dataframe[color_column]
        .dtype.kind
        in "if"
    )

    if numeric_heatmap:

        minimum = dataframe[color_column].min()

        # Prevent one hotspot from compressing all colors
        maximum = dataframe[color_column].quantile(0.95)

    else:

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

        if numeric_heatmap:

            record["color"] = build_heat_color(
                record[color_column],
                minimum,
                maximum,
            )

        else:

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


def draw_heatmap_legend(
    minimum: float,
    maximum: float,
):
    """
    Display continuous heatmap legend.
    """

    st.markdown(
        f"""
        <div style="padding-top:35px;">

        <b>Demand</b>

        <div style="
        height:260px;
        width:24px;
        background:linear-gradient(
        to top,
        blue,
        green,
        yellow,
        red
        );
        border-radius:5px;
        margin:auto;
        ">
        </div>

        <div style="text-align:center;font-size:13px;">
        {maximum:.1f}
        </div>

        <div style="
        height:180px;
        ">
        </div>

        <div style="text-align:center;font-size:13px;">
        {minimum:.1f}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
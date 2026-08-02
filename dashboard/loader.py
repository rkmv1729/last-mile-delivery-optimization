import streamlit as st
import pandas as pd
from helpers import (
    load_forecast_model,
    load_scaler,
    load_metadata
)
from config import DATA_DIR
from pathlib import Path




@st.cache_data
def load_data():

    retained_batches_path = DATA_DIR / "retained_batches.parquet"

    if retained_batches_path.exists():
        retained_batches_df = pd.read_parquet(
            retained_batches_path
        )
    else:
        retained_batches_df = pd.DataFrame()

    return {

        "zone_mapping_df":
            pd.read_parquet(
                DATA_DIR / "zone_mapping.parquet"
            ),

        "ahsi_history_df":
            pd.read_parquet(
                DATA_DIR / "ahsi_algorithm.parquet"
            ),

        "zone_forecast_df":
            pd.read_parquet(
                DATA_DIR / "zone_forecast.parquet"
            ),

        "orders_df":
            pd.read_parquet(
                DATA_DIR / "orders.parquet"
            ),

        "retained_batches_df": retained_batches_df,  

        "selected_batches_df":
            pd.read_parquet(
                DATA_DIR / "selected_batches.parquet"
            ),

        "retained_orders_df":
            pd.read_parquet(
                DATA_DIR / "retained_orders.parquet"
            ),

        "zone_assignment_df":
            pd.read_parquet(
                DATA_DIR / "zone_assignment.parquet"
            ),
    }


@st.cache_resource
def load_static_resources():

    lade_hz_df = pd.read_parquet(
        DATA_DIR / "lade_hangzhou.parquet"
    )

    familiarity_df = pd.read_parquet(
        DATA_DIR / "driver_h3_cell_8_familiarity.parquet"
    )

    products_df = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    dispatch_centres_df = pd.read_csv(
        DATA_DIR / "dispatch_centres.csv"
    )

    metadata = load_metadata(
        metadata_path=DATA_DIR / "models" / "model_metadata.json"
    )

    scaler = load_scaler(
        scaler_path=DATA_DIR / "models" / "demand_scaler.pkl"
    )

    model = load_forecast_model(
        model_path=DATA_DIR / "models" / "demand_lstm.pth",
        metadata=metadata,
    )

    return {
        "lade_hz_df": lade_hz_df,
        "familiarity_df": familiarity_df,
        "products_df": products_df,
        "dispatch_centres_df": dispatch_centres_df,
        "metadata": metadata,
        "scaler": scaler,
        "model": model,
    }
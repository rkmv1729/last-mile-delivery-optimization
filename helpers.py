import pandas as pd
import numpy as np
import random
import json
import joblib
import torch
from demand_forecast.model import DemandForecastLSTM
from math import radians, sin, cos, sqrt, atan2

SHIFT_ORDER = {
    "Morning": 0,
    "Afternoon": 1,
    "Evening": 2
}

def load_forecast_model(
    model_path: str,
    metadata: dict,
    device: str = "cpu",
):
    """
    Load the trained LSTM forecasting model.

    Parameters
    ----------
    model_path : str
        Path to the trained model (.pth).

    metadata : dict
        Loaded model metadata.

    device : str, default="cpu"
        Device used for inference.

    Returns
    -------
    DemandLSTM
        Loaded model ready for inference.
    """

    model = DemandForecastLSTM(
        input_size=len(metadata["feature_columns"]),
        hidden_size=metadata["hidden_size"],
        num_layers=metadata["num_layers"],
        dropout=metadata["dropout"],
    )

    state_dict = torch.load(
        model_path,
        map_location=device,
    )

    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    return model

# =====================================================

def load_scaler(
    scaler_path: str,
):
    """
    Load the fitted MinMaxScaler.

    Parameters
    ----------
    scaler_path : str
        Path to demand_scaler.pkl.

    Returns
    -------
    MinMaxScaler
        Fitted scaler used during training.
    """

    return joblib.load(scaler_path)


# =====================================================

def load_metadata(
    metadata_path: str,
) -> dict:
    """
    Load model metadata.

    Parameters
    ----------
    metadata_path : str
        Path to model_metadata.json.

    Returns
    -------
    dict
        Model configuration including:
            - lookback
            - features
            - hidden_size
            - num_layers
            - dropout
            - batch_size
            - learning_rate
    """

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    return metadata


def prepare_operational_state(
    lade_df: pd.DataFrame,
    metadata,
    ds,
    shift: str,
):
    """
    Prepare the operational state for the selected date and shift.

    Parameters
    ----------
    lade_df : pd.DataFrame
        Master LaDe operational dataset.

    ds : str or datetime
        Selected operational date.

    shift : str
        Selected shift.

    lookback : int, default=12
        Number of previous shifts used for demand forecasting.

    Returns
    -------
    current_shift_df : pd.DataFrame
        Current operational state.

    forecast_history_df : pd.DataFrame
        Previous lookback shifts restricted to the active H3 cells.
    """

    ds = pd.to_datetime(ds)

    # ------------------------------------------------------------
    # Current operational shift
    # ------------------------------------------------------------

    current_shift_df = (
        lade_df[
            (lade_df["ds"] == ds)
            & (lade_df["shift"] == shift)
        ][[
            "order_id",
            "courier_id",
            "ds",
            "shift",
            "accept_gps_time",
            "delivery_gps_lat",
            "delivery_gps_lng",
            "h3_cell_8",
            "is_weekend",
            "day_index",
            "day_of_week"
        ]]
        .copy()
        .sort_values("accept_gps_time")
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # Active H3 cells
    # ------------------------------------------------------------

    active_cells = current_shift_df["h3_cell_8"].unique()

    # ------------------------------------------------------------
    # Chronological shift timeline
    # ------------------------------------------------------------

    timeline = (
        lade_df[["ds", "shift"]]
        .drop_duplicates()
        .assign(
            shift_order=lambda x: x["shift"].map(SHIFT_ORDER)
        )
        .sort_values(["ds", "shift_order"])
        .reset_index(drop=True)
    )

    current_idx = timeline[
        (timeline["ds"] == ds)
        & (timeline["shift"] == shift)
    ].index[0]

    history = timeline.iloc[
        max(0, current_idx - metadata["lookback"]): current_idx
    ][["ds", "shift"]]

    # ------------------------------------------------------------
    # Forecast history
    # ------------------------------------------------------------

    forecast_df = (
        lade_df.merge(
            history,
            on=["ds", "shift"],
            how="inner"
        )
    )

    forecast_df = (
        forecast_df[
            forecast_df["h3_cell_8"].isin(active_cells)
        ][[
            "order_id",
            "ds",
            "shift",
            "accept_gps_time",
            "delivery_gps_lat",
            "delivery_gps_lng",
            "h3_cell_8",
            "is_weekend",
            "day_index",
            "day_of_week"
        ]]
        .copy()
        .sort_values("accept_gps_time")
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # Aggregate demand
    # ------------------------------------------------------------

    forecast_df = (
        forecast_df
        .groupby(
            [
                "h3_cell_8",
                "ds",
                "shift",
                "day_index",
                "day_of_week",
                "is_weekend",
            ],
            as_index=False,
        )
        .agg(
            demand=("order_id", "count")
        )
    )

    # ------------------------------------------------------------
    # Complete missing Cell × Shift combinations
    # ------------------------------------------------------------

    grid = (
        history.assign(key=1)
        .merge(
            pd.DataFrame(
                {
                    "h3_cell_8": active_cells,
                    "key": 1,
                }
            ),
            on="key",
        )
        .drop(columns="key")
    )

    grid = grid.merge(
        timeline[["ds", "shift"]].drop_duplicates(),
        on=["ds", "shift"],
        how="left",
    )

    forecast_df = (
        grid.merge(
            forecast_df,
            on=["ds", "shift", "h3_cell_8"],
            how="left",
        )
    )

    forecast_df["demand"] = (
        forecast_df["demand"]
        .fillna(0)
        .astype(int)
    )

    forecast_df["day_index"] = (
        forecast_df.groupby("ds")["ds"]
        .transform("first")
        .factorize()[0]
    )


    return current_shift_df, forecast_df

# ----------------------------------------------------
def build_h3_demand(
    current_shift_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Build H3 demand required by the AHSI layer.

    Parameters
    ----------
    current_shift_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame

        h3_cell_8
        demand
    """

    h3_demand_df = (
        current_shift_df
        .groupby("h3_cell_8", as_index=False)
        .agg(
            demand=("order_id", "count")
        )
        .sort_values(
            "demand",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return h3_demand_df

# ---------------------------------------------

def attach_zone_ids(
    current_shift_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Attach operational zone IDs to the current shift.

    Parameters
    ----------
    current_shift_df

        order_id
        courier_id
        ds
        shift
        accept_gps_time
        delivery_gps_lat
        delivery_gps_lng
        h3_cell_8

    zone_mapping_df

        zone_id
        h3_cell_8

    Returns
    -------
    current_shift_zone_df
    """

    current_shift_zone_df = (
        current_shift_df.merge(
            zone_mapping_df,
            on="h3_cell_8",
            how="left"
        )
        .sort_values("accept_gps_time")
        .reset_index(drop=True)
    )

    return current_shift_zone_df

# -----------------------------------------------

def build_zone_forecast(
    cell_forecast_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build zone-level demand forecasts and Forecast Opportunity scores.

    Parameters
    ----------
    cell_forecast_df
        h3_cell_8
        shift
        predicted_demand

    forecast_df
        Historical operational state used for forecasting.
        Required columns:
            - h3_cell_8
            - shift
            - order_id

    zone_mapping_df
        h3_cell_8
        zone_id

    Returns
    -------
    zone_forecast_df
        zone_id
        shift
        forecast_demand
        forecast_opportunity
    """

    # --------------------------------------------------
    # Aggregate predicted demand to zones
    # --------------------------------------------------

    zone_forecast_df = (
        cell_forecast_df
        .merge(
            zone_mapping_df,
            on="h3_cell_8",
            how="left",
        )
        .groupby(
            ["zone_id", "shift"],
            as_index=False,
        )["predicted_demand"]
        .sum()
        .rename(
            columns={
                "predicted_demand": "forecast_demand"
            }
        )
    )

    # --------------------------------------------------
    # Historical mean demand per zone
    # --------------------------------------------------

    historical_mean = (
        forecast_df
        .merge(
            zone_mapping_df,
            on="h3_cell_8",
            how="left",
        )
        .groupby(
            ["zone_id", "shift"],
            as_index=False,
        )["demand"]
        .mean()
        .rename(
            columns={
                "demand": "historical_mean"
            }
        )
    )

    # --------------------------------------------------
    # Forecast Opportunity
    # --------------------------------------------------

    zone_forecast_df = zone_forecast_df.merge(
        historical_mean,
        on=["zone_id", "shift"],
        how="left",
    )

    zone_forecast_df["historical_mean"] = (
        zone_forecast_df["historical_mean"]
        .fillna(1e-6)
        .clip(lower=1e-6)
    )

    zone_forecast_df["forecast_opportunity"] = (
        zone_forecast_df["forecast_demand"]
        / zone_forecast_df["historical_mean"]
    )

    # Preserve the raw opportunity ratio before normalization
    zone_forecast_df["forecast_ratio"] = (
        zone_forecast_df["forecast_opportunity"]
    )

    fo = zone_forecast_df["forecast_opportunity"]

    if fo.max() > fo.min():
        zone_forecast_df["forecast_opportunity"] = (
            (fo - fo.min())
            / (fo.max() - fo.min())
        )
    else:
        zone_forecast_df["forecast_opportunity"] = 0.5

    zone_forecast_df["demand_change"] = (
        (zone_forecast_df["forecast_ratio"] - 1.0)
        * 100
    ).round(2)

    return zone_forecast_df[
        [
            "zone_id",
            "shift",
            "forecast_demand",
            "forecast_opportunity",
            "demand_change"
        ]
    ]

# ---------------------------------------------


def denormalize_dataframe(
    df: pd.DataFrame,
    scaler,
    metadata,
    columns_to_denormalize,
    column_mapping=None
) -> pd.DataFrame:
    """
    Inverse transform selected normalized columns.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing normalized values.

    scaler : fitted sklearn scaler
        Scaler used during training.

    feature_columns : list
        Ordered feature list used to fit the scaler.

    columns_to_denormalize : list
        Columns to inverse transform.

    Returns
    -------
    pd.DataFrame
        Dataframe with denormalized columns.
    """

    result = df.copy()

    if column_mapping is None:
        column_mapping = {}

    dummy = np.zeros(
        (len(result), len(metadata["feature_columns"]))
    )

    # ---------------------------------------------
    # Fill dummy matrix
    # ---------------------------------------------

    for column in columns_to_denormalize:

        feature_name = column_mapping.get(column, column)
        feature_idx = metadata["feature_columns"].index(feature_name)

        dummy[:, feature_idx] = result[column]

    dummy = scaler.inverse_transform(dummy)

    # ---------------------------------------------
    # Copy back denormalized values
    # ---------------------------------------------

    for column in columns_to_denormalize:

        feature_name = column_mapping.get(column, column)
        feature_idx = metadata["feature_columns"].index(feature_name)

        values = dummy[:, feature_idx]

        if np.issubdtype(result[column].dtype, np.integer):
            values = np.round(values).astype(int)

        result[column] = values

    return result


# -----------------------------------------------
def build_product_distribution(
    products_df,
    max_quantity_per_item=20,
    temperature=0.7
):
    """
    Generate a random product basket for a single order.

    Parameters
    ----------
    products_df

        product_id
        priority_score

    Returns
    -------
    dict

        {
            "1001": 2,
            "1007": 1
        }
    """

    ITEM_COUNT_WEIGHTS = {
        1: 0.45,
        2: 0.30,
        3: 0.15,
        4: 0.07,
        5: 0.03
    }

    n_items = random.choices(
        population=list(ITEM_COUNT_WEIGHTS.keys()),
        weights=list(ITEM_COUNT_WEIGHTS.values()),
        k=1
    )[0]

    smoothed_weights = np.exp(products_df["priority_score"] / temperature)

    sampled = products_df.sample(
        n=min(n_items, len(products_df)),
        replace=False,
        weights=smoothed_weights,
        random_state=None
    )

    basket = {}

    for _, row in sampled.iterrows():

        basket[str(row["product_id"])] = random.randint(
            1,
            max_quantity_per_item
        )

    return basket

# --------------------------------------------
def generate_orders(
    h3_demand_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
    current_shift_df: pd.DataFrame,
    products_df: pd.DataFrame,
    max_quantity_per_item: int = 20,
    temperature: float = 0.7,
) -> pd.DataFrame:
    """
    Generate synthetic orders for the current operational state.

    Parameters
    ----------
    h3_demand_df
        h3_cell_8
        demand

    zone_mapping_df
        h3_cell_8
        zone_id

    current_shift_df
        Current operational shift containing:
            - h3_cell_8
            - accept_gps_time
            - delivery_gps_lat
            - delivery_gps_lng

    products_df
        Product catalogue.

    Returns
    -------
    orders_df
        order_id
        h3_cell_8
        zone_id
        accept_gps_time
        delivery_gps_lat
        delivery_gps_lng
        retention_cycles
        products
    """

    zone_lookup = dict(
        zip(
            zone_mapping_df["h3_cell_8"],
            zone_mapping_df["zone_id"]
        )
    )

    records = []
    order_id = 1

    for row in h3_demand_df.itertuples():

        h3_cell = row.h3_cell_8
        demand = int(row.demand)

        zone_id = zone_lookup.get(h3_cell)

        cell_orders = current_shift_df[
            current_shift_df["h3_cell_8"] == h3_cell
        ]

        if cell_orders.empty:
            continue

        for _ in range(demand):

            sample = cell_orders.sample(1).iloc[0]

            basket = build_product_distribution(
                products_df=products_df,
                max_quantity_per_item=max_quantity_per_item,
                temperature=temperature,
            )

            records.append(
                {
                    "order_id": order_id,
                    "h3_cell_8": h3_cell,
                    "zone_id": zone_id,
                    "accept_gps_time": sample["accept_gps_time"],
                    "delivery_gps_lat": sample["delivery_gps_lat"],
                    "delivery_gps_lng": sample["delivery_gps_lng"],
                    "retention_cycles": 0,
                    "products": basket,
                }
            )

            order_id += 1

    return pd.DataFrame(records)
# -------------------------------------------

def extract_retained_orders(
    retained_batch_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extracts retained orders from retained batches.

    Increments the retention cycle of every retained order
    before returning them for the next dispatch cycle.
    """
    

    retained_orders = []

    for batch in retained_batch_df.itertuples():

        for order in batch.orders:

            order_dict = order._asdict()

            order_dict["retention_cycles"] += 1

            retained_orders.append(order_dict)

    if not retained_orders:
        return retained_batch_df.iloc[0:0].copy()

    return pd.DataFrame(retained_orders)


# -------------------------------------------

def enrich_orders(
    new_orders_df,
    products_df,
):
    """
    Add priority_score and load_factor to each product
    inside every order.
    """

    product_lookup = (
        products_df
        .set_index("product_id")
        [
            [
                "priority_score",
                "load_factor",
            ]
        ]
        .to_dict("index")
    )



    def enrich(products):

        enriched = []

        for product_id, quantity in products.items():

            product_id = int(product_id)

            meta = product_lookup[product_id]

            enriched.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "priority_score": meta["priority_score"],
                    "load_factor": meta["load_factor"],
                }
            )

        return enriched

    new_orders_df = new_orders_df.copy()

    new_orders_df["products"] = (
        new_orders_df["products"]
        .apply(enrich)
    )

    return new_orders_df



def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * R * atan2(sqrt(a), sqrt(1 - a))



def assign_dispatch_centers(
    new_orders_df,
    dispatch_centers_df,
):
    centers = dispatch_centers_df.to_dict("records")

    dispatch_ids = []

    for order in new_orders_df.itertuples():

        nearest = min(
            centers,
            key=lambda dc: haversine(
                order.delivery_gps_lat,
                order.delivery_gps_lng,
                dc["gps_lat"],
                dc["gps_lng"],
            ),
        )

        dispatch_ids.append(
            nearest["dispatch_center_id"]
        )

    orders_df = new_orders_df.copy()
    orders_df["dispatch_center_id"] = dispatch_ids

    return orders_df


def recycle_retained_orders(
        new_orders_df: pd.DataFrame,
        retained_orders_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Merges retained orders from the previous dispatch cycle
        with newly arrived orders.
        """

        if retained_orders_df.empty:
            return new_orders_df.copy()

        return pd.concat(
            [
                retained_orders_df,
                new_orders_df,
            ],
            ignore_index=True,
        )


# -----------------------------------------------------
def get_available_couriers(
    current_shift_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Extract available couriers for the current shift.
    """

    return (
        current_shift_df[
            ["courier_id"]
        ]
        .drop_duplicates()
        .sort_values("courier_id")
        .reset_index(drop=True)
    )


# ---------------------------------------------------
def replace_objects_with_ids(
    df: pd.DataFrame,
    source_column: str,
    id_key: str = "order_id",
    target_column: str | None = None,
) -> pd.DataFrame:
    """
    Replace a list of dictionaries with a list of IDs.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    source_column : str
        Column containing a list of dictionaries.

    id_key : str, default="order_id"
        Key to extract from each dictionary.

    target_column : str, optional
        Name of the output column.
        Defaults to '<source_column>_ids'.

    Returns
    -------
    pd.DataFrame
    """

    result = df.copy()

    if target_column is None:
        target_column = f"{source_column}_ids"

    result[target_column] = result[source_column].apply(
        lambda items: [
            item[id_key] if isinstance(item,dict)
            else getattr(item, id_key)
            for item in items
        ]
    )

    result = result.drop(columns=[source_column])

    return result



def serialize_object_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

    result = df.copy()

    if result.empty or column not in result.columns:
        return result

    result[column] = result[column].apply(json.dumps)

    return result

def deserialize_object_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

    df = df.copy()

    if column in df.columns:
        df[column] = df[column].apply(
            lambda x: json.loads(x)
            if isinstance(x, str)
            else x
        )

    return df


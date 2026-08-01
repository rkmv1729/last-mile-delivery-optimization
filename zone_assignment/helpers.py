import pandas as pd


def build_zone_familiarity(
    driver_familiarity_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
    aggregation: str = "mean"
) -> pd.DataFrame:
    """
    Aggregate driver familiarity from H3 cells to operational zones.

    Inputs
    ------
    driver_familiarity_df
        courier_id
        h3_cell_8
        familiarity_score

    cell_mapping_df
        h3_cell_8
        zone_id

    Returns
    -------
    courier_id
    zone_id
    familiarity_score
    """

    df = driver_familiarity_df.merge(
        zone_mapping_df,
        on="h3_cell_8",
        how="inner"
    )

    group = df.groupby(
        ["courier_id", "zone_id"],
        as_index=False
    )["familiarity_score"]

    aggregation = aggregation.lower()

    if aggregation == "mean":
        return group.mean()

    if aggregation == "median":
        return group.median()

    if aggregation == "max":
        return group.max()

    raise ValueError(f"Unknown aggregation: {aggregation}")


def filter_active_zones(
    zone_familiarity_df: pd.DataFrame,
    batch_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Keep only zones present in the current dispatch batch.
    """

    active_zones = batch_df["zone_id"].unique()

    return zone_familiarity_df[
        zone_familiarity_df["zone_id"].isin(active_zones)
    ].reset_index(drop=True)



def filter_available_drivers(
    zone_familiarity_df: pd.DataFrame,
    available_drivers_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Keep only currently available drivers.
    """

    drivers = available_drivers_df["courier_id"].unique()

    return zone_familiarity_df[
        zone_familiarity_df["courier_id"].isin(drivers)
    ].reset_index(drop=True)


def build_familiarity_matrix(
    zone_familiarity_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert long-format familiarity into Driver × Zone matrix.
    """

    return (
        zone_familiarity_df
        .pivot(
            index="courier_id",
            columns="zone_id",
            values="familiarity_score"
        )
        .fillna(0.0)
        .sort_index()
        .sort_index(axis=1)
    )

def prepare_inputs(
    selected_batches_df: pd.DataFrame,
    available_drivers_df: pd.DataFrame,
    driver_familiarity_df: pd.DataFrame,
    zone_mapping_df: pd.DataFrame,
    aggregation: str = "mean"
) -> pd.DataFrame:
    """
    Complete preprocessing for the assignment algorithm.

    Returns
    -------
    Driver × Zone familiarity matrix.
    """

    familiarity = build_zone_familiarity(
        driver_familiarity_df,
        zone_mapping_df,
        aggregation
    )

    familiarity = filter_available_drivers(
        familiarity,
        available_drivers_df
    )

    familiarity = filter_active_zones(
        familiarity,
        selected_batches_df
    )

    return build_familiarity_matrix(familiarity)
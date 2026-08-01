from ahsi.algorithms import *


def run_ahsi(
    h3_demand_df,
    num_zones,
    seed_spacing,
):
    """
    Execute the complete Adaptive H3 Spatial Indexing pipeline.

    Parameters
    ----------
    h3_demand_df : pd.DataFrame
        Columns:
            - h3_cell_8
            - orders

    num_zones : int
        Number of operational zones to create.

    seed_spacing : int, default=2
        Minimum H3 graph distance between seed cells.

    Returns
    -------
    pd.DataFrame
        Columns:
            - h3_cell_8
            - zone_id
    """

    seed_df = initialize_seeds(
        h3_demand_df=h3_demand_df,
        num_zones=num_zones,
        seed_spacing=seed_spacing,
    )

    zone_df = grow_regions(
        h3_demand_df=h3_demand_df,
        seed_df=seed_df,
    )

    zone_mapping_df = refine_boundaries(
        h3_demand_df=h3_demand_df,
        zone_df=zone_df,
    )

    return zone_mapping_df
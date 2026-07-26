"""
Orchestrates the Adaptive H3 Spatial Indexing (AHSI) pipeline.

Pipeline
--------
1. Load H3 demand data
2. Validate input
3. Compute demand statistics
4. Derive adaptive thresholds
5. Build neighborhood graph
6. Merge sparse cells
7. Split hotspot cells
8. Construct operational zones
9. Validate output
10. Save zone mapping
"""


# TODO : make the ahsi module OOP class oriented

from time import perf_counter

from common.logs.logger import setup_logger

from config import ZONE_MAPPING_FILE

import pandas as pd

from ahsi.config import LOG_FILE
from ahsi.io import load_h3_demand, save_zone_mapping
from ahsi.merge import merge_sparse_cells
from ahsi.neighbors import build_neighbor_graph
from ahsi.split import split_hotspot_cells
from ahsi.statistics import compute_demand_statistics
from ahsi.thresholds import compute_thresholds
from ahsi.validator import validate_input, validate_output
from ahsi.zone_builder import build_zone_mapping


logger = setup_logger(LOG_FILE)


def run_ahsi(
    h3_demand: pd.DataFrame
) -> pd.DataFrame:
    """Execute the complete AHSI pipeline."""

    start_time = perf_counter()

    try:
        logger.info("Loaded H3 demand data...")

        logger.info("Validating input...")
        validate_input(h3_demand)

        logger.info("Computing demand statistics...")
        stats = compute_demand_statistics(h3_demand)

        logger.info(stats)

        logger.info("Computing adaptive thresholds...")
        sparse_threshold, hotspot_threshold = compute_thresholds(
            h3_demand
        )

        logger.info("Building H3 neighborhood graph...")
        neighbor_graph = build_neighbor_graph(
            h3_demand)

        logger.info("Merging sparse cells...")
        merge_plan = merge_sparse_cells(
            h3_demand,
            neighbor_graph,
            sparse_threshold
        )

        logger.info("Splitting hotspot cells...")
        split_plan = split_hotspot_cells(
            h3_demand,
            hotspot_threshold
        )

        logger.info("Constructing operational zones...")
        zone_mapping = build_zone_mapping(
            h3_demand,
            merge_plan,
            split_plan
        )

        logger.info("Validating output...")
        validate_output(
            zone_mapping
        )

        logger.info(zone_mapping["zone_id"].nunique())
        logger.info((zone_mapping["resolution"] == 7).sum())
        logger.info((zone_mapping["resolution"] == 8).sum())

        logger.info(f"Merged groups: {len(merge_plan)}")
        logger.info(f"Split parents: {len(split_plan)}")

        logger.info(zone_mapping.duplicated(
            subset=["cell_id", "resolution"]
        ).sum())

        logger.info("Saving zone mapping...")
        save_zone_mapping(
            zone_mapping,
            ZONE_MAPPING_FILE
        )

        elapsed = perf_counter() - start_time

        logger.info(
            "AHSI completed successfully in %.2f seconds.",
            elapsed
        )

        return zone_mapping

    except Exception:
        logger.exception("AHSI pipeline failed.")
        raise

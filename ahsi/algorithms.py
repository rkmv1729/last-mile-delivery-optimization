import pandas as pd
from ahsi.helpers import *

# =============================================================

def initialize_seeds(
    h3_demand_df: pd.DataFrame,
    num_zones: int,
    seed_spacing: int
) -> pd.DataFrame:
    """
    Algorithm 1: AHSI Seed Initialization

    Selects high-demand H3-8 cells as initial zone seeds while ensuring
    that no two seeds are immediate neighbors.

    Parameters
    ----------
    h3_demand_df : pd.DataFrame
        Required columns:
            - h3_cell_8 : str
            - orders    : int

    Returns
    -------
    pd.DataFrame
        Columns:
            - zone_id
            - seed_cell
            - seed_orders
    """

    # Highest demand cells are considered first
    sorted_cells = h3_demand_df.sort_values(
        by="demand",
        ascending=False
    ).reset_index(drop=True)

    covered_cells = set()
    seeds = []

    for _, row in sorted_cells.iterrows():

        if len(seeds) == num_zones:
            break

        cell = row["h3_cell_8"]

        if cell in covered_cells:
            continue

        seeds.append({
            "zone_id": len(seeds) + 1,
            "seed_cell": cell,
            "seed_orders": row["demand"]
        })

        covered_cells.update(
            h3.grid_disk(cell, seed_spacing)
        )

    return pd.DataFrame(seeds)


# =============================================================
# grow_regions

def grow_regions(
    h3_demand_df: pd.DataFrame,
    seed_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Algorithm 2: AHSI Simultaneous Region Growing

    Parameters
    ----------
    h3_demand_df : pd.DataFrame
        Required columns:
            - h3_cell_8
            - demand

    seed_df : pd.DataFrame
        Required columns:
            - zone_id
            - seed_cell
            - seed_orders

    Returns
    -------
    pd.DataFrame
        Columns:
            - h3_cell_8
            - zone_id
    """

    # Lookup table for workloads
    workload_map = dict(
        zip(
            h3_demand_df["h3_cell_8"],
            h3_demand_df["demand"]
        )
    )

    all_cells = set(workload_map.keys())

    zones = {}
    assigned = {}
    zone_workloads = {}

    # Initialize zones with seeds
    for _, row in seed_df.iterrows():

        zone_id = row["zone_id"]
        seed = row["seed_cell"]

        zones[zone_id] = {seed}
        assigned[seed] = zone_id
        zone_workloads[zone_id] = row["seed_orders"]

    unassigned = all_cells - set(assigned.keys())

    while unassigned:

        best_cell = None
        best_zone = None
        best_score = float("inf")

        # Evaluate every candidate assignment
        for zone_id, zone_cells in zones.items():

            candidate_cells = set()

            # Adjacent unassigned cells
            for cell in zone_cells:

                for neighbor in h3.grid_disk(cell, 1):

                    if neighbor in unassigned:
                        candidate_cells.add(neighbor)

            # Evaluate every neighboring candidate
            for cell in candidate_cells:

                score = compute_workload_imbalance(
                    zone_workloads,
                    zone_id,
                    workload_map[cell]
                )

                if score < best_score:

                    best_score = score
                    best_cell = cell
                    best_zone = zone_id

        # No feasible expansion
        if best_cell is None:

            # Pick any remaining cell
            cell = next(iter(unassigned))

            # Assign it to the currently lightest zone
            best_zone = min(zone_workloads, key=zone_workloads.get)

            zones[best_zone].add(cell)
            assigned[cell] = best_zone
            zone_workloads[best_zone] += workload_map[cell]
            unassigned.remove(cell)

            continue

        # Perform the best assignment
        zones[best_zone].add(best_cell)

        assigned[best_cell] = best_zone

        zone_workloads[best_zone] += workload_map[best_cell]

        unassigned.remove(best_cell)

    return pd.DataFrame({
        "h3_cell_8": list(assigned.keys()),
        "zone_id": list(assigned.values())
    })


# =============================================================


# =============================================================
# refine_boundaries


def refine_boundaries(
    h3_demand_df: pd.DataFrame,
    zone_df: pd.DataFrame
):
    """
    Algorithm 3:
    AHSI Boundary Refinement
    """

    workload_map = dict(
        zip(
            h3_demand_df["h3_cell_8"],
            h3_demand_df["demand"]
        )
    )

    zones = {}

    for zone_id, group in zone_df.groupby("zone_id"):

        zones[zone_id] = set(group["h3_cell_8"])

    zone_workloads = {}

    for zone_id, cells in zones.items():

        zone_workloads[zone_id] = sum(
            workload_map[cell]
            for cell in cells
        )

    improved = True

    while improved:

        improved = False

        best_transfer = None
        best_score = max(zone_workloads.values()) - min(zone_workloads.values())

        boundary_cells = find_boundary_cells(zones)

        for cell, source_zone in boundary_cells:

            if not is_connected(
                zones[source_zone],
                cell
            ):
                continue

            neighbors = h3.grid_disk(cell, 1)

            adjacent_zones = set()

            for neighbor in neighbors:

                for zone_id, zone_cells in zones.items():

                    if zone_id == source_zone:
                        continue

                    if neighbor in zone_cells:
                        adjacent_zones.add(zone_id)

            for destination_zone in adjacent_zones:

                score = compute_boundary_transfer(
                    zone_workloads,
                    source_zone,
                    destination_zone,
                    workload_map[cell]
                )

                if score < best_score:

                    best_score = score

                    best_transfer = (
                        cell,
                        source_zone,
                        destination_zone
                    )

        if best_transfer is None:
            break

        cell, source_zone, destination_zone = best_transfer

        zones[source_zone].remove(cell)
        zones[destination_zone].add(cell)

        zone_workloads[source_zone] -= workload_map[cell]
        zone_workloads[destination_zone] += workload_map[cell]

        improved = True

    records = []

    for zone_id, cells in zones.items():

        for cell in cells:

            records.append({
                "h3_cell_8": cell,
                "zone_id": zone_id
            })

    return pd.DataFrame(records)
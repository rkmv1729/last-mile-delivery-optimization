import h3 

# Helper for grow_regions

def compute_workload_imbalance(
    zone_workloads: dict,
    zone_id: int,
    cell_workload: float
) -> float:
    """
    Computes the global workload imbalance if a cell is assigned
    to the specified zone.

    Parameters
    ----------
    zone_workloads : dict
        Current workload of each zone.
        Example:
            {1: 230, 2: 185, 3: 210}

    zone_id : int
        Candidate zone.

    cell_workload : float
        Workload of the candidate H3 cell.

    Returns
    -------
    float
        Global workload imbalance after assignment.
    """

    updated_workloads = zone_workloads.copy()

    updated_workloads[zone_id] += cell_workload

    workloads = list(updated_workloads.values())

    imbalance = max(workloads) - min(workloads)

    return imbalance


# =============================================================
# Helpers for refine_boundaries

# find_boundary_cells
def find_boundary_cells(zones: dict):
    """
    Identifies all boundary cells.

    Parameters
    ----------
    zones : dict
        {
            zone_id: {h3_cells}
        }

    Returns
    -------
    list
        [
            (cell, zone_id),
            ...
        ]
    """

    # Reverse lookup
    zone_map = {}

    for zone_id, cells in zones.items():
        for cell in cells:
            zone_map[cell] = zone_id

    boundary_cells = []

    for cell, zone_id in zone_map.items():

        for neighbor in h3.grid_disk(cell, 1):

            if neighbor not in zone_map:
                continue

            if zone_map[neighbor] != zone_id:

                boundary_cells.append((cell, zone_id))
                break

    return boundary_cells

from collections import deque


# is_connected
def is_connected(
    zone_cells: set,
    removed_cell: str
):
    """
    Checks whether removing a cell keeps
    the remaining zone connected.
    """

    remaining = zone_cells - {removed_cell}

    if len(remaining) <= 1:
        return True

    start = next(iter(remaining))

    visited = set()
    queue = deque([start])

    while queue:

        current = queue.popleft()

        if current in visited:
            continue

        visited.add(current)

        for neighbor in h3.grid_disk(current, 1):

            if neighbor in remaining and neighbor not in visited:
                queue.append(neighbor)

    return len(visited) == len(remaining)


# compute_boundary_transfer
def compute_boundary_transfer(
    zone_workloads: dict,
    source_zone: int,
    destination_zone: int,
    cell_workload: float
):
    """
    Computes the global workload imbalance
    after moving a boundary cell.
    """

    updated = zone_workloads.copy()

    updated[source_zone] -= cell_workload
    updated[destination_zone] += cell_workload

    workloads = list(updated.values())

    return max(workloads) - min(workloads)
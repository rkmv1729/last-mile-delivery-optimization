"""
===========================================================================
Batch Optimizer
===========================================================================

Performs Stage-1 Batch Formation Optimization.

Responsibilities
----------------
1. Merge retained products from previous cycle.
2. Group products by dispatch centre and destination zone.
3. Compute Effective Product Score (EPS).
4. Perform EPS-guided capacity-aware packing.
5. Return optimized product groups.

This module generates feasible candidate batches only.
Resource allocation and dispatch decisions are handled in Stage-2.
=========================DISPATCH_CENTER_STORAGE_CAPACITY==================================================
"""

import pandas as pd

from dispatch_engine.config import (
    MAX_BATCH_SIZE,
    EPS_PRIORITY_WEIGHT,
    EPS_RETENTION_WEIGHT,
    RETENTION_INCREMENT,
    MAX_RETENTION_PENALTY,
)


class BatchOptimizer:
    """
    Stage-1 Batch Formation Optimizer.
    """

    # ------------------------------------------------------------------ #
    # Public API                                                            
    # ------------------------------------------------------------------ #

    def optimize(self,
    transfer_orders_df: pd.DataFrame,
    retained_orders_df: pd.DataFrame | None = None,
    ) -> list[dict]:
        """
        Generate optimized candidate batches.

        Parameters
        ----------
        transfer_df : pd.DataFrame

        retained_products : pd.DataFrame | None

        Returns
        -------
        list[dict]
            Optimized groups.
        """
        # TODO: validate input dataframe columns

        # Merge retained products from previous cycle
        merged_orders_df = self._merge_retained_products(
            transfer_orders_df,
            retained_orders_df,
        )

        # Group by dispatch centre and destination zone
        groups = self._group_orders(merged_orders_df)

        candidate_batches = []

        # Optimize each group independently
        for group in groups:

            candidate_batches.extend(
                self._optimize_group(group)
            )

        return candidate_batches

    # ------------------------------------------------------------------ #
    # Private Methods
    # ------------------------------------------------------------------ #

    def _merge_retained_products(
        self,
        transfer_orders_df,
        retained_orders_df,
    ):
        """
        Merge retained products from the previous dispatch cycle.

        Parameters
        ----------
        transfer_df : pd.DataFrame
            Newly transferred products.

        retained_products : pd.DataFrame | None
            Products retained from the previous cycle.

        Returns
        -------
        pd.DataFrame
            Combined working dataframe.
        """

        if retained_orders_df is None or retained_orders_df.empty:

            return transfer_orders_df.copy().reset_index(drop=True)

        merged_orders_df = (
            pd.concat(
                [transfer_orders_df, retained_orders_df],
                ignore_index=True,
            )
            .reset_index(drop=True)
        )

        return merged_orders_df

    def _group_orders(self, merged_orders_df):
        """
        Group orders by dispatch centre and destination zone.

        Parameters
        ----------
        df : pd.DataFrame

        Returns
        -------
        list[tuple]
            Each element contains

            (
                dispatch_center,
                destination_zone,
                grouped_dataframe
            )
        """

        grouped = []

        # make sure to update dipatch center and destination zone immediately after 
        # zone before dispatch is feeded inputs
        grouped_df = merged_orders_df.groupby(
            [
                "dispatch_center",
                "destination_zone",
            ],
            sort=False,
        )

        for (
            dispatch_center,
            destination_zone,
        ), group in grouped_df:

            grouped.append(
            {
            "dispatch_center": dispatch_center,
            "destination_zone": destination_zone,
            "orders": group["orders"].reset_index(drop=True),
            }
        )

        return grouped

    def _compute_eps(self, group_df):
        """
        Compute Effective Product Score (EPS).

        EPS =
            (Priority Score × EPS_PRIORITY_WEIGHT)
            +
            (Retention Penalty × EPS_RETENTION_WEIGHT)

        Parameters
        ----------
        group_df : pd.DataFrame

        Returns
        -------
        pd.DataFrame
            DataFrame sorted by descending EPS.
        """

        df = group_df.copy()


        assert "priority_score" in df.columns

        # Compute EPS
        df["eps"] = (
            EPS_PRIORITY_WEIGHT * df["priority_score"]
            +
            EPS_RETENTION_WEIGHT * df["retention_penalty"]
        )

        # Highest priority products first
        df = df.sort_values(
            by="eps",
            ascending=False
        ).reset_index(drop=True)

    
        return df
    

    def _update_retention_penalty(self, group_df):
        """
        Update carry-over retention penalty.

        Parameters
        ----------
        group_df : pd.DataFrame
            Product group.

        Returns
        -------
        pd.DataFrame
            Updated dataframe containing:
            - retention_cycles
            - retention_penalty
        """

        df = group_df.copy()

        # Ensure required columns exist
        if "retention_cycles" not in df.columns:
            df["retention_cycles"] = 0

        # Compute retention penalty
        df["retention_penalty"] = (
            df["retention_cycles"] * RETENTION_INCREMENT
        ).clip(upper=MAX_RETENTION_PENALTY)

        return df
    

    def _optimize_group(
        self,
        group,
    ):
        """
        Optimize one
        (dispatch_center, destination_zone)
        group.

        Returns
        -------
        list[dict]
            Optimized groups (candidate batches).
        """

        candidate_batches = []

        dispatch_center = group["dispatch_center"]
        destination_zone = group["destination_zone"]
        group_df = group["orders"]

        # Step 1
        group_df = self._update_retention_penalty(group_df)

        # Step 2
        group_df = self._compute_eps(group_df)

        remaining_products = group_df.copy()

        # Step 3
        while not remaining_products.empty:

            (
                batch_products,
                remaining_products,
                remaining_capacity,
            ) = self._seed_batch(
                remaining_products
            )

            (
                batch_products,
                remaining_products,
                remaining_capacity,
            ) = self._fill_batch(
                batch_products,
                remaining_products,
                remaining_capacity,
            )

            candidate_batches.append(

                self._build_candidate_batches(
                    batch_products,
                    dispatch_center,
                    destination_zone,
                )

            )

        return candidate_batches
    

    def _seed_batch(self, remaining_products):
        """
        Initialize a batch with the highest EPS product.

        Parameters
        ----------
        remaining_products : pd.DataFrame

        Returns
        -------
        tuple
            (
                batch_products,
                remaining_products,
                remaining_capacity
            )
        """

        if remaining_products.empty:
            return [], remaining_products, MAX_BATCH_SIZE

        # Highest EPS product (already sorted by EPS)
        seed_product = remaining_products.iloc[0]

        units = seed_product["normalized_units"]

        # sanity check, does not happen very often
        if units > MAX_BATCH_SIZE:
            raise ValueError(
                f"Product requires {units} units, "
                f"which exceeds MAX_BATCH_SIZE={MAX_BATCH_SIZE}."
            )

        batch_products = [seed_product.to_dict()]

        remaining_capacity = (
            MAX_BATCH_SIZE
            - seed_product["normalized_units"]
        )

        remaining_products = remaining_products.iloc[1:].reset_index(drop=True)

        return (
            batch_products,
            remaining_products,
            remaining_capacity,
        )

    def _fill_batch(
        self,
        batch_products,
        remaining_products,
        remaining_capacity,
    ):
        """
        Fill remaining batch capacity using an EPS-guided greedy strategy.

        Products are considered in descending EPS order. A product is added
        only if it fits in the remaining capacity.

        Parameters
        ----------
        batch_products : list
            Current batch.

        remaining_products : pd.DataFrame

        remaining_capacity : float

        Returns
        -------
        tuple
            (
                batch_products,
                remaining_products,
                remaining_capacity
            )
        """

        if remaining_products.empty:
            return (
                batch_products,
                remaining_products,
                remaining_capacity,
            )

        selected_indices = []

        for idx, product in remaining_products.iterrows():

            units = product["normalized_units"]

            if units <= remaining_capacity:

                batch_products.append(product.to_dict())

                remaining_capacity -= units

                selected_indices.append(idx)

                # Perfect utilization
                if remaining_capacity <= 0:
                    break

        if selected_indices:
            remaining_products = (
                remaining_products
                .drop(index=selected_indices)
                .reset_index(drop=True)
            )

        return (
            batch_products,
            remaining_products,
            remaining_capacity,
        )

    def _build_candidate_batches(
        self,
        batch,
        dispatch_center,
        destination_zone,
    ):
        """
        Construct an optimized group summary.

        Parameters
        ----------
        batch_products : list[dict]
        dispatch_center : str
        destination_zone : str

        Returns
        -------
        dict
            Optimized group.
        """

        batch_size = sum(
            order["normalized_units"]
            for order in batch
        )

        return {

            "dispatch_center": dispatch_center,

            "destination_zone": destination_zone,

            "batch": batch,

            "batch_size": batch_size,

            "remaining_capacity": MAX_BATCH_SIZE - batch_size,
        }
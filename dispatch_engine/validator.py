"""
===========================================================================
Dispatch Engine Validator
===========================================================================

Performs sanity checks on dispatch engine inputs and outputs.

Responsibilities
----------------
1. Validate incoming transfer products.
2. Validate generated candidate batches.
3. Validate available resources.
4. Validate demand forecast.
5. Validate optimization output.
===========================================================================
"""

from dispatch_engine.config import MAX_BATCH_SIZE


class DispatchValidator:
    """
    Dispatch Engine Validator.
    """

    # ------------------------------------------------------------------ #
    # Products
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_products(
        transfer_df,
    ):
        """
        Validate incoming transfer products.
        """

        if transfer_df.empty:
            raise ValueError(
                "No transfer products received."
            )

        required_columns = {
            "dispatch_center",
            "destination_zone",
            "priority_score",
            "normalized_units",
        }

        missing = (
            required_columns
            - set(transfer_df.columns)
        )

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        if transfer_df["priority_score"].isnull().any():
            raise ValueError(
                "Priority scores contain missing values."
            )

        if (
            transfer_df["normalized_units"] <= 0
        ).any():
            raise ValueError(
                "All normalized_units must be positive."
            )

        if (
            transfer_df["normalized_units"]
            > MAX_BATCH_SIZE
        ).any():
            raise ValueError(
                "One or more products exceed MAX_BATCH_SIZE."
            )

    # ------------------------------------------------------------------ #
    # Candidate Batches
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_batches(
        batches,
    ):
        """
        Validate generated candidate batches.
        """

        if not batches:
            raise ValueError(
                "No batches generated."
            )

        required_keys = {
            "dispatch_center",
            "destination_zone",
            "products",
            "batch_size",
        }

        for batch in batches:

            missing = (
                required_keys
                - set(batch.keys())
            )

            if missing:
                raise ValueError(
                    f"Batch missing keys: {sorted(missing)}"
                )

    # ------------------------------------------------------------------ #
    # Resources
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_resources(
        available_vehicles,
        available_drivers,
    ):
        """
        Validate resource availability.
        """

        total_vehicles = sum(
            available_vehicles.values()
        )

        if total_vehicles <= 0:
            raise ValueError(
                "No vehicles available."
            )

        if (
            available_drivers is None
            or available_drivers <= 0
        ):
            raise ValueError(
                "No drivers available."
            )

    # ------------------------------------------------------------------ #
    # Forecast
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_forecast(
        forecast,
    ):
        """
        Validate demand forecast.
        """

        if forecast is None:
            return

        if not isinstance(
            forecast,
            dict,
        ):
            raise ValueError(
                "Forecast must be a dictionary."
            )

    # ------------------------------------------------------------------ #
    # Output
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_output(
        selected_batches,
        retained_batches,
    ):
        """
        Validate optimization output.
        """

        if (
            len(selected_batches)
            + len(retained_batches)
            == 0
        ):
            raise ValueError(
                "Dispatch optimization produced no batches."
            )
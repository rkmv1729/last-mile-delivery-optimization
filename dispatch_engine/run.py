"""
Dispatch Engine Runner
----------------------
Runs the complete dispatch optimization pipeline.
"""

from common.logs.logger import setup_logger

from dispatch_engine.io import DispatchDataLoader
from dispatch_engine.dispatch_engine import DispatchEngine

from dispatch_engine.config import (
    VAN,
    BIKE,
    LOG_FILE
)


def main():

    logger = setup_logger(
        LOG_FILE
    )

    logger.info(
        "=" * 70
    )
    logger.info(
        "Starting Dispatch Engine..."
    )

    try:

        loader = DispatchDataLoader()

        transfer_products = (
            loader.load_transfer_products()
        )

        retained_products = (
            loader.load_retained_products()
        )

        dispatch_center_state = (
            loader.load_dispatch_center_state()
        )

        forecast = (
            loader.load_forecast()
        )

        # ----------------------------------------------------------
        # Temporary Simulation Resources
        # ----------------------------------------------------------

        available_vehicles = {
            VAN: 5,
            BIKE: 10,
        }

        available_drivers = 15

        # ----------------------------------------------------------

        engine = DispatchEngine()

        (
            selected_batches,
            retained_batches,
        ) = engine.dispatch(
            transfer_products=transfer_products,
            retained_products=retained_products,
            dispatch_center_state=dispatch_center_state,
            forecast=forecast,
            available_vehicles=available_vehicles,
            available_drivers=available_drivers,
        )

        logger.info(
            "Dispatch optimization completed successfully."
        )

        logger.info(
            "Selected Batches : %d",
            len(selected_batches),
        )

        logger.info(
            "Retained Batches : %d",
            len(retained_batches),
        )

        logger.info(
            "Total Batches    : %d",
            len(selected_batches)
            + len(retained_batches),
        )

        dispatched_units = sum(
            batch.batch_size
            for batch in selected_batches
        )

        retained_units = sum(
            batch.batch_size
            for batch in retained_batches
        )

        logger.info(
            "Dispatched Units : %.2f",
            dispatched_units,
        )

        logger.info(
            "Retained Units   : %.2f",
            retained_units,
        )

        logger.info(
            "=" * 70
        )

    except Exception:

        logger.exception(
            "Dispatch Engine execution failed."
        )

        raise


if __name__ == "__main__":

    main()
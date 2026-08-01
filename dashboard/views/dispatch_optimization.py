import streamlit as st

from dashboard.components.cards import metric_cards

from dashboard.components.plots import (
    draw_dispatch_summary,
    draw_batch_priority,
)

from dashboard.components.tables import (
    draw_dispatch_table,
    draw_retained_orders_table,
)

def show_dispatch_optimization(
    data: dict,
):
    """
    Display the Dispatch Optimization dashboard.
    """

    st.title("🚚 Dispatch Optimization")

    selected_batches_df = data[
        "selected_batches_df"
    ]

    retained_batches_df = data[
        "retained_batches_df"
    ]

    retained_orders_df = data[
        "retained_orders_df"
    ]

    metrics = {

        "Selected Batches":
            len(
                selected_batches_df
            ),

        "Retained Batches":
            len(
                retained_batches_df
            ),

        "Average Batch Priority":
            round(
                selected_batches_df[
                    "batch_priority"
                ].mean(),
                3,
            ),

        "Average Retention Penalty":
            round(
                retained_orders_df[
                    "retention_penalty"
                ].mean(),
                3,
            ),
    }

    metric_cards(metrics)

    st.divider()


    draw_dispatch_summary(
        selected_batches_df,
        retained_batches_df,
    )

    st.divider()

    draw_batch_priority(
        selected_batches_df,
    )

    st.divider()

    draw_dispatch_table(
        selected_batches_df,
    )

    st.divider()

    draw_retained_orders_table(
        retained_orders_df,
    )
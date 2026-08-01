import streamlit as st


def prepare_metrics(
    metrics: dict,
) -> list[tuple]:
    """
    Convert metric dictionary into
    ordered (label, value) pairs.
    """

    return list(metrics.items())




def metric_cards(
    metrics: dict,
):
    """
    Display KPI cards.
    """

    metric_items = prepare_metrics(
        metrics
    )

    columns = st.columns(
        len(metric_items)
    )

    for column, (label, value) in zip(
        columns,
        metric_items,
    ):

        column.metric(
            label=label,
            value=value,
        )
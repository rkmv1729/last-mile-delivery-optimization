import streamlit as st


def show_home(
    data: dict,
):
    """
        Display the project overview page.
        """

    st.title("🚚 Last Mile Delivery Operations")


    st.markdown(
            """
    An end-to-end decision support framework for last-mile delivery operations.
    The dashboard demonstrates the complete operational pipeline, including
    adaptive zone partitioning, demand forecasting, dispatch optimization,
    and courier assignment.
    """
        )

    st.divider()

        # --------------------------------------------------
        # Pipeline Workflow
        # --------------------------------------------------

    st.subheader(
            "Pipeline Workflow"
        )

    st.markdown(
            """
    ```text
    Customer Orders
            │
            ▼
    Adaptive H3 Spatial Indexing
            │
            ▼
    Demand Forecasting
            │
            ▼
    Dispatch Optimization
            │
            ▼
    Zone Assignment
            │
            ▼
    Delivery Operations
    """
    )


    st.divider()

    # --------------------------------------------------
    # Quick Statistics
    # --------------------------------------------------

    orders_df = data["orders_df"]

    zone_mapping_df = data["zone_mapping_df"]

    metrics = {

        "Orders":
            len(
                orders_df
            ),

        "Operational Zones":
            zone_mapping_df[
                "zone_id"
            ].nunique(),

        "H3 Cells":
            zone_mapping_df[
                "h3_cell_8"
            ].nunique(),

        "Dispatch Centres":
            orders_df[
                "dispatch_center_id"
            ].nunique(),
    }

    columns = st.columns(4)

    for column, (
        label,
        value,
    ) in zip(
        columns,
        metrics.items(),
    ):

        column.metric(
            label,
            value,
        )

    st.divider()


    # --------------------------------------------------
    # Dashboard Modules
    # --------------------------------------------------

    st.subheader(
        "Dashboard Modules"
    )

    st.markdown(
        """
    📍 Adaptive H3 Spatial Indexing

    Constructs balanced operational delivery zones using adaptive H3 region growing.

    📈 Demand Forecast

    Predicts shift-wise demand for each operational zone using an LSTM model.

    👷 Zone Assignment

    Assigns operational zones to couriers by maximizing familiarity while maintaining workload balance.

    🚚 Dispatch Optimization

    Determines which batches should be dispatched immediately and which orders should be retained for future consolidation.
    """
    )

    st.divider()


    # --------------------------------------------------
    # Dataset
    # --------------------------------------------------

    st.subheader(
        "Dataset"
    )

    st.markdown(
        """
    Dataset: LaDe (Large-scale Delivery Dataset)
    City: Hangzhou
    Operational Days: 184
    Spatial Representation: Uber H3 Grid
    Dashboard: Streamlit
    """
    )

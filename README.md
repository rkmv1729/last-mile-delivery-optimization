# Last Mile Delivery Operations

An end-to-end intelligent last-mile delivery framework integrating spatial partitioning, demand forecasting, dispatch optimization, and courier zone assignment.

## Pipeline Overview

The backend pipeline consists of four operational layers:

1. **Adaptive H3 Spatial Indexing (AHSI)**
   - Partitions the operational area into balanced delivery zones.

2. **Demand Forecasting**
   - Predicts next-shift demand for each H3 cell using an LSTM model.
   - Aggregates forecasts into operational zone forecasts.

3. **Dispatch Optimization**
   - Generates customer orders.
   - Forms delivery batches using the Effective Priority Score (EPS).
   - Selects optimal batches using the Batch Utility Score (BUS).

4. **Zone Assignment**
   - Assigns available couriers to operational zones using the Hungarian Algorithm based on historical familiarity.

---

## Project Structure

```
.
├── ahsi/
├── demand_forecast/
├── dispatch_optimization/
├── zone_assignment/
├── data/
│   ├── dispatch_centres.csv
│   ├── products.csv
│   ├── lade_hangzhou.parquet
│   ├── driver_h3_cell_8_familiarity.parquet
│   └── models/
│       ├── demand_lstm.pth
│       ├── demand_scaler.pkl
│       └── model_metadata.json
├── helpers.py
├── config.py
├── pipeline.py
└── README.md
```

---

## Requirements

Install the project dependencies.

```bash
pip install -r requirements.txt
```

---

### Selecting the Operational Shift

The pipeline processes one operational shift at a time. The execution date and shift can be modified by updating the following constants in `pipeline.py` before running the pipeline:

```python
ds = "YYYY-MM-DD"
shift = "<shift_name>"
```

**Available date range**

```
1900-05-01  →  1900-10-31
```

**Available shift values**

- `"Morning"`
- `"Afternoon"`
- `"Evening"`

After updating these values, execute:

```bash
python pipeline.py
```

to generate the outputs corresponding to the selected operational shift.



The pipeline automatically performs:

1. Operational state preparation
2. Adaptive H3 Spatial Indexing (AHSI)
3. Demand forecasting
4. Order generation
5. Dispatch optimization
6. Zone assignment

---

## Generated Outputs

After successful execution, the following files are generated:

```
zone_mapping.parquet
zone_forecast.parquet
orders.parquet
selected_batches.parquet
retained_orders.parquet
zone_assignment.parquet
```

These files serve as inputs to the visualization dashboard and simulation engine.

---

## Notes

- The pipeline executes one operational shift at a time
- Retained orders are recycled into subsequent dispatch cycles.
- All trained models and metadata are stored under `data/models/`.
- The generated outputs are intended for downstream visualization and simulation.

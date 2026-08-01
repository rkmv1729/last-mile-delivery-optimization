# Last Mile Delivery Optimization

🚀 **Live Demo:** https://last-mile-delivery-optimization-pwjap8vigqxztu9wpfc9t5.streamlit.app/
<img width="1750" height="961" alt="Screenshot from 2026-08-02 03-37-53" src="https://github.com/user-attachments/assets/eff0bdd7-a875-47a1-805d-0bd7c9abd00c" />

<img width="1616" height="1074" alt="Screenshot from 2026-08-02 03-38-28" src="https://github.com/user-attachments/assets/cc6934df-fee7-4de9-82ec-6f4a43353cea" />

<img width="1616" height="1074" alt="Screenshot from 2026-08-02 03-38-47" src="https://github.com/user-attachments/assets/e857e706-d31d-4a41-b3b4-a7a62391a37a" />

<img width="1616" height="1074" alt="Screenshot from 2026-08-02 03-38-57" src="https://github.com/user-attachments/assets/c176e6e3-0201-4c2a-a022-925101033dd8" />

<img width="1616" height="1074" alt="Screenshot from 2026-08-02 03-39-05" src="https://github.com/user-attachments/assets/ee61ea51-fd6e-4e08-b6b3-7cf0e632bcd8" />
An end-to-end prototype for intelligent last-mile delivery optimization integrating adaptive spatial partitioning, demand forecasting, dispatch optimization, and driver assignment.

---

## Features

- Adaptive H3 Spatial Indexing (AHSI)
- LSTM-based Demand Forecasting
- BUS-based Dispatch Optimization
- Hungarian Algorithm for Zone Assignment
- Interactive Streamlit Dashboard

---

## Project Structure

```text
last-mile-delivery-optimization/
│
├── ahsi/                     # Adaptive H3 Spatial Indexing
├── demand_forecast/          # LSTM demand forecasting
├── dispatch_optimization/    # Batch formation & dispatch optimization
├── zone_assignment/          # Driver-zone assignment
├── dashboard/                # Streamlit dashboard
├── data/                     # Input datasets & generated outputs
├── config.py
├── helpers.py
├── pipeline.py               # End-to-end pipeline
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/rkmv1729/last-mile-delivery-optimization.git

cd last-mile-delivery-optimization

python -m venv .venv

source .venv/bin/activate        # Linux / macOS

pip install -r requirements.txt
```

---

## Running the Dashboard

```bash
streamlit run dashboard/app.py
```

---

## Dependencies

- Python 3.12+
- Streamlit
- Pandas
- NumPy
- PyTorch
- Scikit-learn
- PuLP
- SciPy
- H3
- PyArrow

All required packages are listed in `requirements.txt`.

---

## Dashboard Modules

- Adaptive H3 Spatial Indexing
- Demand Forecast Visualization
- Dispatch Optimization
- Zone Assignment
- Performance Metrics

---

## Technologies

- Python
- Streamlit
- PyTorch
- H3 Spatial Indexing
- PuLP
- SciPy
- Pandas
- NumPy

---

## License

This project was developed as part of an internship/research prototype.

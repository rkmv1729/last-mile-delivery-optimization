import pandas as pd

sel = pd.read_parquet("data/selected_batches.parquet")
ret = pd.read_parquet("data/retained_orders.parquet")
print(sel.columns.tolist())
print(ret.columns.tolist())

import pandas as pd
import json

"""

Exploring the dataset.

"""

train_df = pd.read_csv("data/raw/train.csv")
test_df = pd.read_csv("data/raw/test.csv")

with open("data/raw/clinc150/data_oos_plus.json" , encoding="utf-8") as f:
    clinc_data = json.load(f)

print("CLINC150")
print(len(clinc_data["oos_train"]))
print(len(clinc_data["oos_val"]))
print(len(clinc_data["oos_test"]))

print("Banking77")
print("Training shape:", train_df.shape)
print("Test shape:", test_df.shape)

print("\nColumns:")
print(train_df.columns.tolist())

print("\nFirst training example:")
print(train_df.iloc[0].to_dict())

print("\nNumber of categories:")
print(train_df["category"].nunique())

print("\nExamples per category:")
print(train_df["category"].value_counts())
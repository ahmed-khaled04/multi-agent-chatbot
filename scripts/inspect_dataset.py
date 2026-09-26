import pandas as pd

"""

Exploring the dataset.

"""

train_df = pd.read_csv("data/raw/train.csv")
test_df = pd.read_csv("data/raw/test.csv")

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
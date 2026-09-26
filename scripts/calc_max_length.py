import numpy as np
import pandas as pd

from src.data.text_processing import tokenize

""" 

from this calculation I saw that the dataset gets covered well by 40 43 48
we will take the three values as candidates and test them on the network which performs well.


"""

train_df = pd.read_csv("data/raw/train.csv")

# Tokenize every message
train_df["tokens"] = train_df["text"].apply(tokenize)

# Count token in every message
train_df["token_count"] = train_df["tokens"].apply(len)

lengths = train_df["token_count"].to_numpy()

print("Number of messages:", len(lengths))
print("Minimum:", lengths.min())
print("Mean:", lengths.mean())
print("Median:", np.median(lengths))
print("Maximum:", lengths.max())

for percentile in [75, 90, 95, 97, 98, 99, 99.5]:
    value = np.percentile(lengths, percentile)
    print(f"{percentile}th percentile: {value:.1f}")

# AI to see how each length cover the entire data
for max_length in [16, 20, 24, 28, 32, 36, 40 , 43 ,48, 64]:
    fully_preserved = (lengths <= max_length).sum()
    truncated = (lengths > max_length).sum()
    coverage = fully_preserved / len(lengths) * 100

    print(
        f"{max_length:2} tokens: "
        f"{coverage:.2f}% covered, "
        f"{truncated} truncated"
    )
# AI

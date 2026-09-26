from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .mapping import INTENT_TO_ROUTE

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
RANDOM_SEED = 42
VALIDATION_SIZE = 0.15

def add_agent_route(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    dataframe["agent_route"] = dataframe["category"].map(INTENT_TO_ROUTE)

    # A Check to see if any unmapped intent to raise an error
    if dataframe["agent_route"].isna().any():
        missing = sorted(
            dataframe.loc[
                dataframe["agent_route"].isna(),
                "category",
            ].unique()
        )
        raise ValueError(f"Unmapped intents {missing}")
    return dataframe

def main() -> None:
    train_df = pd.read_csv(RAW_DATA_DIR / "train.csv")
    test_df = pd.read_csv(RAW_DATA_DIR / "test.csv")

    # Add agent routes to both
    train_df = add_agent_route(train_df)
    test_df = add_agent_route(test_df)

    # Split Train into train and validation
    development_train_df , validation_df = train_test_split(
        train_df,
        test_size=VALIDATION_SIZE,
        random_state=RANDOM_SEED,
        stratify=train_df["category"],
    )

    PROCESSED_DATA_DIR.mkdir(parents=True , exist_ok=True)

    development_train_df.to_csv(
        PROCESSED_DATA_DIR / "train.csv",
        index=False
    )
    validation_df.to_csv(
        PROCESSED_DATA_DIR / "validation.csv",
        index=False
    )
    test_df.to_csv(
        PROCESSED_DATA_DIR / "test.csv",
        index=False
    )
    print("Development train:", len(development_train_df))
    print("Validation:", len(validation_df))
    print("Official test:", len(test_df))

if __name__ == "__main__":
    main()

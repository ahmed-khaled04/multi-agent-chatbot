from torch.utils.data import DataLoader , Dataset
import pandas as pd
from pathlib import Path

from .dataset import RoutingDataset
from .vocabulary import Vocabulary
from .mapping import ROUTE_TO_ID

def create_loader(
        dataset: Dataset,
        batch_size: int = 32,
        num_workers: int = 0,
        shuffle: bool = False,
) -> DataLoader:
    loader = DataLoader(dataset=dataset,
                        batch_size=batch_size,
                        num_workers=num_workers,
                        shuffle=shuffle)
    return loader

# Testing the loader functionality
if __name__ == "__main__":

    PROCESSED_DATA_DIR = Path("data/processed")

    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")

    vocab = Vocabulary(min_freq=2,
                       max_size=10_000)
    vocab.build_vocab(train_df["text"])
    print(f"Vocabulary Size: {len(vocab.stoi)}")

    train_data = RoutingDataset(dataframe=train_df,
                                vocabulary=vocab,
                                max_seq=48,
                                route_to_id=ROUTE_TO_ID,)
    input_id, seq_length , label = train_data[0]
    print(f"Token IDs: {input_id}")
    print(f"Sequence Length: {seq_length}")
    print(f"Label: {label}")
    print("===============")

    train_loader = create_loader(dataset=train_data,
                                 batch_size=32,
                                 num_workers=0,
                                 shuffle=True)
    
    input_batch, seq_batch , label_batch = next(iter(train_loader))

    print(f"The shape of input: {input_batch.shape}")
    print(f"The shape of Sequence: {seq_batch.shape}")
    print(f"The shape of Label: {label_batch.shape}")

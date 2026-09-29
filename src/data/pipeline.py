import pandas as pd

from .dataset import RoutingDataset
from .dataloader import create_loader



def run_pipeline(
        train_df: pd.DataFrame,
        validation_df: pd.DataFrame,
        vocab,
        seq_length,
        batch_size,
        num_workers,
        route_to_id       
):  
   
    train_data = RoutingDataset(
        dataframe=train_df,
        vocabulary=vocab,
        max_seq=seq_length, 
        route_to_id=route_to_id
    )

    validation_data = RoutingDataset(
        dataframe=validation_df,
        vocabulary=vocab,
        max_seq=seq_length, 
        route_to_id=route_to_id
    )

    train_loader = create_loader(
        dataset=train_data,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=True
    )

    validation_loader = create_loader(
        dataset=validation_data,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=False
    )
    return (train_loader , validation_loader)

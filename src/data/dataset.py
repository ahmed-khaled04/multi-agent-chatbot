from torch.utils.data import Dataset
import torch
import pandas as pd

def pad_or_truncate(
        token_ids: list[int],
        pad_id: int,
        max_length: int = 48
) -> tuple[list[int] , int]:
    # Truncate Message
    token_ids = token_ids[:max_length] 
    sequence_length = len(token_ids)

    padding_needed = max_length - sequence_length
    token_ids = token_ids + [pad_id] * padding_needed

    return token_ids , sequence_length


class RoutingDataset(Dataset):
    """ Banking 77 with the added agent route Data set """

    def __init__(self,
                 dataframe: pd.DataFrame,
                 vocabulary,
                 max_seq,
                 route_to_id: dict[str , int],
                 transform = None):
        self.dataframe = dataframe
        self.vocab = vocabulary
        self.max_seq = max_seq
        self.route_to_id = route_to_id
        self.transform = transform

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self , idx):
        row = self.dataframe.iloc[idx]
        text , agent_route = row["text"] , row["agent_route"]
        input_ids = self.vocab.numericalize(text)
        input_ids , sequence_length = pad_or_truncate(token_ids=input_ids,
                        pad_id=self.vocab.stoi[self.vocab.pad_token],
                        max_length=self.max_seq)
        label = self.route_to_id[agent_route]
        # if self.transform:
        #     input_ids = self.transform(input_ids)
        input_ids = torch.tensor(input_ids , dtype=torch.long)
        sequence_length = torch.tensor(sequence_length,
                                       dtype=torch.long)
        label = torch.tensor(label , dtype=torch.long)
        
        return input_ids , sequence_length , label
from torch import nn
import torch

class IntentClassifier(nn.Module):
    def __init__(self,
                 vocab_size: int,
                 embed_dim: int = 100,
                 hidden_dim: int = 128,
                 num_classes: int = 4,
                 pretrained_embeddings: torch.Tensor = None,
                 n_layers: int = 1) -> None:
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size,
                                      embedding_dim=embed_dim,
                                      padding_idx=0)
        if pretrained_embeddings is not None:
            self.embedding.weight.data.copy_(pretrained_embeddings)

        self.rnn = nn.LSTM(input_size=embed_dim,
                           hidden_size=hidden_dim,
                           num_layers=n_layers,
                           batch_first=True,
                           bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(in_features=hidden_dim * 2,
                            out_features=num_classes)
    def forward(self,
                x: torch.Tensor,
                lengths: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        packed = nn.utils.rnn.pack_padded_sequence(
            embedded, lengths.cpu() , batch_first=True,
            enforce_sorted=False
        )
        _ , (hidden , _) = self.rnn(packed)
        h = torch.cat((hidden[-2] , hidden[-1]) , dim=1)
        return self.fc(self.dropout(h))


# Test the model
if __name__ == "__main__":
    vocab_size = 10_000
    batch_size = 32
    sequence_length = 48


    model = IntentClassifier(vocab_size=vocab_size,
                             embed_dim=100,
                             hidden_dim=128,
                             num_classes=4)
    x = torch.randint(low=0,
                      high=vocab_size - 1,
                      size=(batch_size , sequence_length),
                      dtype=torch.long)
    lengths = torch.randint(
        low=1,
        high=sequence_length + 1,
        size=(batch_size,),
        dtype=torch.long
    )

    print(f"Model is on: {next(model.parameters()).device}")

    model.eval()
    with torch.inference_mode():
        output = model(x , lengths)

    print(f"The Input ID Batch Shape: {x.shape}")       
    print(f"The Lengths Shape: {lengths.shape}") 
    print(f"The Output Shape: {output.shape}")  
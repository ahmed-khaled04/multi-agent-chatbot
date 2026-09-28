from pathlib import Path
from tqdm.auto import tqdm
from torchinfo import summary
from torch import nn
from torchmetrics import Accuracy
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
import pandas as pd
import torch

from src.data.mapping import ROUTE_TO_ID
from src.data.vocabulary import Vocabulary 
from src.data.dataset import RoutingDataset
from src.data.dataloader import create_loader
from src.models.model import IntentClassifier

PROCESSED_DATA_DIR = Path("data/processed")
CHECKPOINT_DIR = Path("models/checkpoints")

CHECKPOINT_DIR.mkdir(parents=True , exist_ok=True)

# Hyperparameters
SEQUENCE_LENGTH = 48
BATCH_SIZE = 32
NUM_WORKERS = 0
EMBED_DIM = 100
HIDDEN_DIM = 128    
N_LAYERS = 1
EPOCHS = 5

RANDOM_SEED = 42


train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
validation_df = pd.read_csv(PROCESSED_DATA_DIR / "validation.csv")

vocab = Vocabulary(
    min_freq=2,
    max_size=10_000,
)
vocab.build_vocab(train_df["text"])
print(f"Vocab size: {len(vocab.stoi)}")

train_data = RoutingDataset(
    dataframe=train_df,
    vocabulary=vocab,
    max_seq=SEQUENCE_LENGTH, 
    route_to_id=ROUTE_TO_ID
)

validation_data = RoutingDataset(
    dataframe=validation_df,
    vocabulary=vocab,
    max_seq=SEQUENCE_LENGTH, 
    route_to_id=ROUTE_TO_ID
)

train_loader = create_loader(
    dataset=train_data,
    batch_size=BATCH_SIZE,
    num_workers=NUM_WORKERS,
    shuffle=True
)

validation_loader = create_loader(
    dataset=validation_data,
    batch_size=BATCH_SIZE,
    num_workers=NUM_WORKERS,
    shuffle=False
)

torch.manual_seed(RANDOM_SEED)

model = IntentClassifier(
    vocab_size=len(vocab.stoi),
    embed_dim=EMBED_DIM,
    hidden_dim=HIDDEN_DIM,
    num_classes=len(ROUTE_TO_ID),
    pretrained_embeddings=None,
    n_layers=N_LAYERS
)

dummy_input = torch.randint(
    low=0,
    high=len(vocab.stoi),
    size=(BATCH_SIZE , SEQUENCE_LENGTH),
    dtype=torch.long
)
dummy_lengths = torch.full(
    size=(BATCH_SIZE,),
    fill_value=SEQUENCE_LENGTH,
    dtype=torch.long
)

summary(model , input_data=(dummy_input ,  dummy_lengths))

# Create loss function and optimizer
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(
    params=model.parameters(),
    lr=1e-3
)
accuracy_fn = Accuracy(
    task="multiclass",
    num_classes=len(ROUTE_TO_ID)
)


# Create Write for ploting
run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

writer = SummaryWriter(
    log_dir=Path("runs") / run_name
)

best_validation_loss = float("inf")

# Training Loop
for epoch in tqdm(range(EPOCHS)):
    # Train
    model.train()
    train_loss = 0
    train_examples = 0
    accuracy_fn.reset()

    for inputs,lengths,labels in train_loader:
        y_logits = model(inputs , lengths)

        loss = loss_fn(y_logits , labels)

        batch_size = labels.size(0)
        train_loss += loss.item() * batch_size
        train_examples += batch_size

        accuracy_fn.update(y_logits.argmax(dim=1) , labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    train_loss /= train_examples
    train_acc = accuracy_fn.compute().item()


    # Eval
    model.eval()
    validation_loss = 0
    validation_examples = 0
    accuracy_fn.reset()
    
    with torch.inference_mode():
        for inputs, lengths, labels in validation_loader:
            y_logits = model(inputs , lengths)

            loss = loss_fn(y_logits , labels)

            batch_size = labels.size(0)
            validation_loss += loss.item() * batch_size
            validation_examples += batch_size

            accuracy_fn.update(y_logits.argmax(dim=1) , labels)

        validation_loss /= validation_examples
        validation_acc = accuracy_fn.compute().item()

    if validation_loss < best_validation_loss:
        best_validation_loss = validation_loss

        torch.save({
            "epoch": epoch + 1,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "validation_loss": validation_loss,
            "vocab_stoi": vocab.stoi,
            "vocab_itos": vocab.itos,
            "route_to_id": ROUTE_TO_ID,
            "model_config": {
                "vocab_size": len(vocab.stoi),
                "embed_dim": EMBED_DIM,
                "hidden_dim": HIDDEN_DIM,
                "num_classes": len(ROUTE_TO_ID),
                "n_layers": N_LAYERS,
            },
        } , CHECKPOINT_DIR / "best_model.pt")
        print("Best Model Saved")

    writer.add_scalar(
        "Loss/train",
        train_loss,
        epoch + 1
    )
    writer.add_scalar(
        "Loss/validation",
        validation_loss,
        epoch + 1
    )
    writer.add_scalar(
        "Accuracy/train",
        train_acc,
        epoch + 1
    )
    writer.add_scalar(
        "Accuracy/validation",
        validation_acc,
        epoch + 1
    )
    

    print(
        f"Epoch {epoch + 1}/{EPOCHS} | "
        f"train loss: {train_loss:.4f} | "
        f"train accuracy: {train_acc:.4f} | "
        f"validation loss: {validation_loss:.4f} | "
        f"validation accuracy: {validation_acc:.4f}"
    )
writer.close()
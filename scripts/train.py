from pathlib import Path
from tqdm.auto import tqdm
from torchinfo import summary
from torch import nn
from torchmetrics import Accuracy , ConfusionMatrix
from torchmetrics.classification import MulticlassF1Score
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
from mlxtend.plotting import plot_confusion_matrix
import pandas as pd
import torch

from src.data.mapping import ROUTE_TO_ID , ID_TO_ROUTE
from src.data.vocabulary import Vocabulary 
from src.models.model import IntentClassifier
from src.data.pipeline import run_pipeline


PROCESSED_DATA_DIR = Path("data/processed")
CHECKPOINT_DIR = Path("models/checkpoints")

CHECKPOINT_DIR.mkdir(parents=True , exist_ok=True)

# Hyperparameters
SEQUENCE_LENGTH = 48
BATCH_SIZE = 16
NUM_WORKERS = 0
EMBED_DIM = 256
HIDDEN_DIM = 64    
N_LAYERS = 1
EPOCHS = 20

RANDOM_SEED = 42

# Early Stopping
PATIENCE = 3
MIN_DELTA = 1e-3


train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
validation_df = pd.read_csv(PROCESSED_DATA_DIR / "validation.csv")


vocab = Vocabulary(
    min_freq=2,
    max_size=10_000,
)

train_loader , validation_loader = run_pipeline(
    train_df=train_df,
    validation_df=validation_df,
    vocab=vocab,
    seq_length=SEQUENCE_LENGTH,
    batch_size=BATCH_SIZE,
    num_workers=NUM_WORKERS,
    route_to_id=ROUTE_TO_ID
)

vocab.build_vocab(train_df["text"])
print(f"Vocab size: {len(vocab.stoi)}")


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
optimizer = torch.optim.AdamW(
    params=model.parameters(),
    lr=1e-3,
    weight_decay=1e-4
)
accuracy_fn = Accuracy(
    task="multiclass",
    num_classes=len(ROUTE_TO_ID)
)
f1 = MulticlassF1Score(
    num_classes=len(ROUTE_TO_ID),
    average="macro"
)


# Create Write for ploting
run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

writer = SummaryWriter(
    log_dir=Path("runs") / run_name
)

best_validation_loss = float("inf")
epochs_without_improvement = 0

# Training Loop
for epoch in tqdm(range(EPOCHS)):
    # Train
    model.train()
    train_loss = 0
    train_examples = 0
    accuracy_fn.reset()
    f1.reset()

    for inputs,lengths,labels in train_loader:
        y_logits = model(inputs , lengths)

        loss = loss_fn(y_logits , labels)

        batch_size = labels.size(0)
        train_loss += loss.item() * batch_size
        train_examples += batch_size

        accuracy_fn.update(y_logits.argmax(dim=1) , labels)
        f1.update(y_logits.argmax(dim=1) , labels)


        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    train_loss /= train_examples
    train_acc = accuracy_fn.compute().item()
    train_f1 = f1.compute().item()


    # Eval
    model.eval()
    validation_loss = 0
    validation_examples = 0
    accuracy_fn.reset()
    f1.reset()
    
    with torch.inference_mode():
        for inputs, lengths, labels in validation_loader:
            y_logits = model(inputs , lengths)

            loss = loss_fn(y_logits , labels)

            batch_size = labels.size(0)
            validation_loss += loss.item() * batch_size
            validation_examples += batch_size

            accuracy_fn.update(y_logits.argmax(dim=1) , labels)
            f1.update(y_logits.argmax(dim=1) , labels)

        validation_loss /= validation_examples
        validation_acc = accuracy_fn.compute().item()
        validation_f1 = f1.compute().item()

    improved = validation_loss < best_validation_loss - MIN_DELTA

    if improved:
        best_validation_loss = validation_loss
        epochs_without_improvement = 0

        torch.save({
            "epoch": epoch + 1,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "validation_loss": validation_loss,
            "vocab_stoi": vocab.stoi,
            "vocab_itos": vocab.itos,
            "route_to_id": ROUTE_TO_ID,
            "batch_size": BATCH_SIZE,
            "num_workers": NUM_WORKERS,
            "seq_len": SEQUENCE_LENGTH,
            "model_config": {
                "vocab_size": len(vocab.stoi),
                "embed_dim": EMBED_DIM,
                "hidden_dim": HIDDEN_DIM,
                "num_classes": len(ROUTE_TO_ID),
                "n_layers": N_LAYERS,
            },
        } , CHECKPOINT_DIR / "best_model_oos.pt")
        print("Best Model Saved")
    else:
        epochs_without_improvement += 1

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
    writer.add_scalar(
        "F1/train",
        train_f1,
        epoch + 1
    )
    writer.add_scalar(
        "F1/validation",
        validation_f1,
        epoch + 1
    )
    if epochs_without_improvement >= PATIENCE:
        print(f"Early stopping at epoch {epoch + 1}. ")
        print(f"Best validation loss: {best_validation_loss:.4f}")
        break
    
    

    print(
        f"Epoch {epoch + 1}/{EPOCHS} | "
        f"train loss: {train_loss:.4f} | "
        f"train accuracy: {train_acc:.4f} | "
        f"train f1: {train_f1:.4f} | "
        f"validation loss: {validation_loss:.4f} | "
        f"validation accuracy: {validation_acc:.4f} |"
        f"validation f1: {validation_f1:.4f} | "
    )

# Evaluate using validation set , plot confusion matrix

# AI
checkpoint = torch.load(
    CHECKPOINT_DIR / "best_model_oos.pt"
)


model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

print(
    f"Restored model from epoch {checkpoint['epoch']} "
    f"with validation loss {checkpoint['validation_loss']:.4f}"
)
#

# Collect validation predictions
all_predictions = []
all_labels = []

with torch.inference_mode():
    for inputs, lengths, labels in validation_loader:

        logits = model(inputs, lengths)
        predictions = logits.argmax(dim=1)

        all_predictions.append(predictions)
        all_labels.append(labels)

all_predictions = torch.cat(all_predictions)
all_labels = torch.cat(all_labels)

class_names = [
    ID_TO_ROUTE[class_id]
    for class_id in range(len(ID_TO_ROUTE))
]

confmat = ConfusionMatrix(task="multiclass" , num_classes=len(class_names))
confmat_tensor = confmat(preds=all_predictions,
                         target=all_labels)

fig , ax = plot_confusion_matrix(
    conf_mat=confmat_tensor.numpy(),
    class_names=class_names,
    figsize=(10 , 7)
)

ax.set_title("Validation Confusion Matrix")

PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

plot_path = PLOTS_DIR / "validation_confusion_matrix.png"

fig.savefig(
    plot_path,
    dpi=300,
    bbox_inches="tight",
)

print(f"Confusion matrix saved to: {plot_path}")

writer.add_figure(
    "ConfusionMatrix/validation",
    fig,
    global_step=checkpoint["epoch"],
)

writer.close()
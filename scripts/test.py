from pathlib import Path
from tqdm.auto import tqdm
from torch import nn
from torchmetrics import Accuracy , ConfusionMatrix
from torchmetrics.classification import MulticlassF1Score
from datetime import datetime
from mlxtend.plotting import plot_confusion_matrix
import torch
import pandas as pd

from src.data.vocabulary import Vocabulary
from src.data.dataset import RoutingDataset
from src.data.dataloader import create_loader
from src.data.mapping import ROUTE_TO_ID , ID_TO_ROUTE
from src.models.model import IntentClassifier


PROCESSED_DATA_DIR = Path("data/processed")
CHECKPOINT_DIR = Path("models/checkpoints")


RANDOM_SEED = 42


checkpoint = torch.load(
    CHECKPOINT_DIR / "best_model_oos.pt",
    weights_only=True
)

class_names = [
    ID_TO_ROUTE[class_id]
    for class_id in range(len(ID_TO_ROUTE))
]

vocab = Vocabulary(
    min_freq=2,
    max_size=10_000,
)

vocab.stoi = checkpoint["vocab_stoi"]
vocab.itos = checkpoint["vocab_itos"]

test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")
test_data = RoutingDataset(
    dataframe=test_df,
    vocabulary=vocab,
    max_seq=checkpoint["seq_len"],
    route_to_id=ROUTE_TO_ID
)
test_loader = create_loader(
    dataset=test_data,
    batch_size=checkpoint["batch_size"],
    num_workers=checkpoint["num_workers"],
    shuffle=False
)

model = IntentClassifier(
    **checkpoint["model_config"],
    pretrained_embeddings=None
)

model.load_state_dict(checkpoint["model_state_dict"])

loss_fn = nn.CrossEntropyLoss()
accuracy_fn = Accuracy(task="multiclass",
                       num_classes=len(class_names))
f1 = MulticlassF1Score(num_classes=len(class_names),
                       average="macro")

model.eval()

total_loss = 0.0
total_examples = 0
all_predictions = []
all_labels = []

with torch.inference_mode():
    for inputs , lengths , labels in tqdm(test_loader 
                                          , desc="Testing the model.."):

        logits = model(inputs , lengths)
        loss = loss_fn(logits , labels)

        predictions = logits.argmax(dim=1)

        batch_size = labels.size(0)
        total_loss += loss.item() * batch_size
        total_examples += batch_size

        all_predictions.append(predictions)
        all_labels.append(labels)

    predictions = torch.cat(all_predictions)
    labels = torch.cat(all_labels)

    test_loss = total_loss / total_examples
    test_acc = accuracy_fn(predictions , labels)
    test_f1 = f1(predictions , labels)

    print(f"Test examples: {total_examples}")
    print(f"Test loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_acc.item():.4f}")
    print(f"Test macro F1: {test_f1.item():.4f}")

    confmat = ConfusionMatrix(task="multiclass" , num_classes=len(class_names))
    confmat_tensor = confmat(preds=predictions,
                            target=labels)

    fig , ax = plot_confusion_matrix(
        conf_mat=confmat_tensor.numpy(),
        class_names=class_names,
        figsize=(10 , 7)
    )

    ax.set_title("Test Confusion Matrix")

    PLOTS_DIR = Path("plots")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    plot_path = PLOTS_DIR / "test_confusion_matrix.png"

    fig.savefig(
        plot_path,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Confusion matrix saved to: {plot_path}")






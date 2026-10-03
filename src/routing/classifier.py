from dataclasses import dataclass
from pathlib import Path

import torch

from src.data.dataset import pad_or_truncate
from src.data.vocabulary import Vocabulary
from src.models.model import IntentClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHECKPOINT_PATH = (
    PROJECT_ROOT / "models" / "checkpoints" / "best_model_oos.pt"
)


@dataclass(frozen=True)
class RoutingPrediction:
    route: str
    confidence: float


class ClassifierRouter:
    def __init__(
        self,
        checkpoint_path: str | Path = DEFAULT_CHECKPOINT_PATH,
        device: torch.device = "cpu",
    ) -> None:
        self.device = torch.device(device)
        self.checkpoint_path = Path(checkpoint_path)

        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Router checkpoint was not found: {self.checkpoint_path}"
            )

        checkpoint = torch.load(
            self.checkpoint_path,
            map_location=self.device,
            weights_only=True,
        )

        required_keys = {
            "model_state_dict",
            "model_config",
            "vocab_stoi",
            "vocab_itos",
            "route_to_id",
            "seq_len",
        }
        # AI
        missing_keys = required_keys.difference(checkpoint)
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"Checkpoint is missing required fields: {missing}")
        # AI

        self.vocabulary = Vocabulary()
        self.vocabulary.stoi = checkpoint["vocab_stoi"]
        self.vocabulary.itos = checkpoint["vocab_itos"]

        self.sequence_length = checkpoint["seq_len"]
        self.id_to_route = {
            route_id: route
            for route, route_id in checkpoint["route_to_id"].items()
        }

        self.model = IntentClassifier(**checkpoint["model_config"])
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

    def predict(self, message: str) -> str:
        return self.predict_with_confidence(message).route

    def predict_with_confidence(self, message: str) -> RoutingPrediction:
        if not isinstance(message, str):
            raise TypeError("message must be a string")
        if not message.strip():
            raise ValueError("message cannot be empty")

        token_ids = self.vocabulary.numericalize(message)
        token_ids, length = pad_or_truncate(
            token_ids=token_ids,
            pad_id=self.vocabulary.stoi[self.vocabulary.pad_token],
            max_length=self.sequence_length,
        )

        inputs = torch.tensor(
            [token_ids],
            dtype=torch.long,
            device=self.device,
        )
        lengths = torch.tensor([length], dtype=torch.long)

        with torch.inference_mode():
            logits = self.model(inputs, lengths)
            probabilities = torch.softmax(logits, dim=1)
            confidence, route_id = probabilities.max(dim=1)
            route_id = route_id.item()

        try:
            route = self.id_to_route[route_id]
        except KeyError as error:
            raise ValueError(
                f"Model predicted unknown route ID: {route_id}"
            ) from error

        return RoutingPrediction(
            route=route,
            confidence=confidence.item(),
        )


if __name__ == "__main__":
    router = ClassifierRouter()
    print(router.predict("How do i activate my card"))

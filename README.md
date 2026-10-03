# Synthetic Bank Multi-Agent Support Chatbot

This project is a Streamlit banking-support chatbot that combines:

- A trained PyTorch intent classifier for routing requests.
- Specialized LangChain agents and banking tools.
- Retrieval-augmented generation (RAG) using Chroma and local Markdown documents.
- A bounded conversation memory containing the latest five turns.
- A Streamlit chat interface showing the selected route and confidence score.

The application uses the **Groq free API tier** through `langchain-groq`. The configured LLM is `openai/gpt-oss-20b`.

## Setup

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Copy the environment template and add your Groq API key:

```bash
cp .env.example .env
```

Never commit the populated `.env` file or a real API key.

## Prepare the RAG index

The source documents are stored in `data/knowledge_base/`. Build the local Chroma index before starting the application:

```bash
python -m src.rag.vector_store
```

The embedding model is `sentence-transformers/all-MiniLM-L6-v2`. Its files are downloaded on first use and then cached locally.

## Run the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` if Streamlit does not open the browser automatically.

## Classifier data, training, and evaluation

The submitted processed splits are in `data/processed/`, and the runtime classifier checkpoint is:

```text
models/checkpoints/best_model_oos.pt
```

To regenerate the processed train, validation, and test splits from the raw datasets:

```bash
python -m src.data.prepare_data
```

To train a new classifier:

```bash
python scripts/train.py
```

Training writes a new checkpoint to `models/checkpoints/best_model_oos_64_256.pt`. To use that checkpoint in the application, either replace `best_model_oos.pt` with it or pass its path to `ClassifierRouter`.

Evaluate the included runtime checkpoint with:

```bash
python scripts/test.py
```

View training metrics in TensorBoard with:

```bash
tensorboard --logdir runs --port 6006
```

Then open `http://localhost:6006`.

## Notes

- The application uses synthetic banking records from `data/synthetic/bank.db` and defaults to customer `cus_001`.
- The knowledge base describes a fictional company named Synthetic Bank.
- `.env` is ignored by Git; `.env.example` contains placeholders only.
- The generated `data/vector_store/` index can be rebuilt from the included RAG source documents.

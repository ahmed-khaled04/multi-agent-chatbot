from collections import Counter

from .text_processing import tokenize

class Vocabulary:
    def __init__(self ,
                 min_freq=1,
                 max_size=10_000,
                 pad_token="<pad>",
                 unk_token="<unk>"
                 ):
        self.min_freq = min_freq
        self.max_size = max_size
        self.pad_token = pad_token
        self.unk_token = unk_token
        self.specials = [pad_token , unk_token]

        # Maps string to index and index to string
        self.itos = list(self.specials)
        self.stoi = {token: idx for idx , token in enumerate(self.itos)}

    def build_vocab(self , text_iterator):
        counter = Counter()
        for text in text_iterator:
            tokens = self._tokenize(text)
            counter.update(tokens)
        sorted_tokens = sorted(
            counter.items(), # [token , count]
            key=lambda item: (-item[1] , item[0]), # Sort alphabetically if count is equal
        )
        most_frequent_tokens = sorted_tokens[:self.max_size]
        for token, freq in most_frequent_tokens:
            if freq >= self.min_freq and token not in self.stoi:
                self.stoi[token] = len(self.itos)
                self.itos.append(token)

    def _tokenize(self , text):
        return tokenize(text)

    def numericalize(self , text):
        tokens = self._tokenize(text)
        return [self.stoi.get(token , self.stoi[self.unk_token]) for token in tokens]

if __name__ == "__main__":
        
    # AI
    # Example Usage:
    corpus = [
        "Hello world! Welcome to PyTorch.",
        "PyTorch makes deep learning easy and modular."
    ]

    vocab = Vocabulary(min_freq=1 , unk_token="<UNK>")
    vocab.build_vocab(corpus)

    print(vocab.stoi)
    print(f"Encoded line: {vocab.numericalize('Hello PyTorch and hi i Then No They')}")
    # AI Example to test the class
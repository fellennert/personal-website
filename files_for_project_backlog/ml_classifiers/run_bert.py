#!/usr/bin/env python3
"""
Train and evaluate BERT on IMDb sentiment (500 train samples).
Uses conda env bert-env. Writes metrics and runtime to bert_results.json.
"""
import json
import time
from pathlib import Path

import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Paths: same directory as this script
BASE = Path(__file__).resolve().parent
TRAIN_CSV = BASE / "train_split.csv"
TEST_CSV = BASE / "test_split.csv"
OUT_JSON = BASE / "bert_results.json"


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class SentenceDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer.encode_plus(
            text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "label": torch.tensor(label, dtype=torch.long),
        }


class BertClassifier(nn.Module):
    def __init__(self, dropout=0.1):
        super().__init__()
        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(768, 2)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        return self.classifier(pooled_output)


def train_model(model, train_loader, val_loader, device, epochs=3, lr=2e-5):
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["label"].to(device)
                outputs = model(input_ids, attention_mask)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
    return model


def predict_batch(model, loader, device):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs = model(input_ids, attention_mask)
            _, predicted = torch.max(outputs, 1)
            preds.extend(predicted.cpu().tolist())
            labels.extend(batch["label"].tolist())
    return preds, labels


def main():
    device = get_device()
    label_map = {"negative": 0, "positive": 1}

    train_df = pd.read_csv(TRAIN_CSV)
    test_df = pd.read_csv(TEST_CSV)
    if "review" in train_df.columns and "text" not in train_df.columns:
        train_df = train_df.rename(columns={"review": "text"})
    if "review" in test_df.columns and "text" not in test_df.columns:
        test_df = test_df.rename(columns={"review": "text"})

    X_train = train_df["text"].tolist()
    y_train = [label_map[str(s).strip().lower()] for s in train_df["sentiment"]]
    X_test = test_df["text"].tolist()
    y_test = [label_map[str(s).strip().lower()] for s in test_df["sentiment"]]

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    train_dataset = SentenceDataset(X_train, y_train, tokenizer)
    test_dataset = SentenceDataset(X_test, y_test, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16)

    model = BertClassifier()
    t0 = time.perf_counter()
    train_model(model, train_loader, train_loader, device, epochs=3)
    preds, labels = predict_batch(model, test_loader, device)
    elapsed = time.perf_counter() - t0

    results = {
        "accuracy": float(accuracy_score(labels, preds)),
        "precision": float(precision_score(labels, preds, average="weighted", zero_division=0)),
        "recall": float(recall_score(labels, preds, average="weighted", zero_division=0)),
        "f1": float(f1_score(labels, preds, average="weighted", zero_division=0)),
        "runtime_seconds": round(elapsed, 2),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print("BERT results:", results)


if __name__ == "__main__":
    main()

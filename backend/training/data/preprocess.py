"""
Preprocessing for the credibility classifier training data.

Source: Kaggle "TruthLens - Fake News Detection" competition train.csv
Confirmed label convention (checked manually against actual article text,
not assumed from column naming): type=0 -> Real, type=1 -> Fake.

IMPORTANT - dateline leakage:
Real rows in this dataset are mostly Reuters wire copy and literally start
with a "CITY (Reuters) -" prefix. Left in, the model can hit high accuracy
by detecting that formatting pattern alone instead of learning anything
about actual misinformation content. That number would be real but useless
for any input that isn't wire-service copy (i.e. basically everything a
real user submits). This script strips that prefix before training.
"""
import re

import pandas as pd
from sklearn.model_selection import train_test_split

RAW_PATH = "train.csv"
OUTPUT_DIR = "data/processed"
TARGET_ROWS_PER_CLASS = 3500  # ~7000 total rows, sane training time on Colab GPU
RANDOM_SEED = 42

# Matches things like "WASHINGTON (Reuters) - " or "NEW YORK/LONDON (Reuters) - "
DATELINE_PATTERN = re.compile(r"^[A-Z][A-Za-z/,\.\s]*\(Reuters\)\s*-\s*")


def strip_dateline(text: str) -> str:
    return DATELINE_PATTERN.sub("", text, count=1)


def clean_text(text: str) -> str:
    text = str(text).strip()
    text = strip_dateline(text)
    text = re.sub(r"<[^>]+>", " ", text)  # strip leftover HTML tags from scraping
    text = re.sub(r"\s+", " ", text)  # collapse repeated whitespace/newlines
    return text.strip()


def main() -> None:
    df = pd.read_csv(RAW_PATH)
    print(f"Loaded {len(df)} rows")

    before = len(df)
    df = df.dropna(subset=["title", "text"])
    print(f"Dropped {before - len(df)} rows with missing title/text")

    df["text_cleaned"] = df["text"].astype(str).apply(strip_dateline)
    df["input_text"] = (df["title"].astype(str) + ". " + df["text_cleaned"]).apply(clean_text)

    before = len(df)
    df = df[df["input_text"].str.len() >= 20]
    print(f"Dropped {before - len(df)} rows that were too short after cleaning")

    # Drop exact duplicate articles BEFORE splitting - otherwise the same
    # article can land in both train and test, letting the model "cheat"
    # by memorizing rows instead of generalizing. Also catch near-duplicates
    # (reposts with minor edits) using a first-200-char fingerprint.
    before = len(df)
    df = df.drop_duplicates(subset=["input_text"])
    print(f"Dropped {before - len(df)} exact duplicate rows")

    before = len(df)
    df["_fingerprint"] = df["input_text"].str[:200]
    df = df.drop_duplicates(subset=["_fingerprint"])
    df = df.drop(columns=["_fingerprint"])
    print(f"Dropped {before - len(df)} near-duplicate rows (matching first 200 chars)")

    df["label"] = df["type"]

    print("\nClass balance after cleaning:")
    print(df["label"].value_counts())

    class_0 = df[df["label"] == 0]
    class_1 = df[df["label"] == 1]
    n_per_class = min(len(class_0), len(class_1), TARGET_ROWS_PER_CLASS)

    class_0_sample = class_0.sample(n=n_per_class, random_state=RANDOM_SEED)
    class_1_sample = class_1.sample(n=n_per_class, random_state=RANDOM_SEED)

    balanced = pd.concat([class_0_sample, class_1_sample]).sample(
        frac=1, random_state=RANDOM_SEED
    ).reset_index(drop=True)

    print(f"\nBalanced dataset: {len(balanced)} rows ({n_per_class} per class)")

    train_df, temp_df = train_test_split(
        balanced, test_size=0.2, stratify=balanced["label"], random_state=RANDOM_SEED
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["label"], random_state=RANDOM_SEED
    )

    print(f"\nSplit sizes: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
    print("\nTrain label balance:")
    print(train_df["label"].value_counts())

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    train_df[["input_text", "label"]].to_csv(f"{OUTPUT_DIR}/train.csv", index=False)
    val_df[["input_text", "label"]].to_csv(f"{OUTPUT_DIR}/val.csv", index=False)
    test_df[["input_text", "label"]].to_csv(f"{OUTPUT_DIR}/test.csv", index=False)

    print(f"\nSaved train/val/test CSVs to {OUTPUT_DIR}/")

    print("\n--- Sanity check: cleaned label=0 (Real) example ---")
    print(balanced[balanced["label"] == 0]["input_text"].iloc[0][:300])
    print("\n--- Sanity check: cleaned label=1 (Fake) example ---")
    print(balanced[balanced["label"] == 1]["input_text"].iloc[0][:300])


if __name__ == "__main__":
    main()
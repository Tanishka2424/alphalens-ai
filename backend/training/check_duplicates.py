"""
Diagnostic: check for exact or near-duplicate rows leaking across the
train/val/test splits. If the same (or a near-identical) article appears
in both train and test, the model could partly be memorizing rather than
generalizing - which would inflate test accuracy without meaning much.
"""
import pandas as pd

train_df = pd.read_csv("data/data/processed/train.csv")
val_df   = pd.read_csv("data/data/processed/val.csv")
test_df  = pd.read_csv("data/data/processed/test.csv")

train_texts = set(train_df["input_text"])
val_texts = set(val_df["input_text"])
test_texts = set(test_df["input_text"])

train_test_overlap = train_texts & test_texts
train_val_overlap = train_texts & val_texts

print(f"Exact duplicate rows between train and test: {len(train_test_overlap)}")
print(f"Exact duplicate rows between train and val:  {len(train_val_overlap)}")

train_prefixes = set(train_df["input_text"].str[:100])
test_prefixes = test_df["input_text"].str[:100]
near_dupe_count = test_prefixes.isin(train_prefixes).sum()

print(f"\nTest rows whose first 100 characters also appear in train: {near_dupe_count} / {len(test_df)}")

if len(train_test_overlap) > 0 or near_dupe_count > 5:
    print("\n=> Likely leakage between splits - test accuracy is probably inflated.")
else:
    print("\n=> No meaningful overlap detected - splits look clean.")
import logging
import os
import random
import re
import sys
import time
from pathlib import Path

import datasets
import evaluate
import numpy as np
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EvalPrediction,
    Trainer,
    TrainingArguments,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

DATA_DIR = Path("/home/workspace/notion-auto-archive") / "data"

pretrained_model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

train_dataset = datasets.load_from_disk(DATA_DIR / "train/jp-engineer-articles-dataset")
test_dataset = datasets.load_from_disk(DATA_DIR / "test/jp-engineer-articles-dataset")

training_args = TrainingArguments(
    output_dir=DATA_DIR / "results",  # output directory
    num_train_epochs=2,  # total number of training epochs
    learning_rate=2e-05,
    per_device_train_batch_size=2,  # batch size per device during training
    per_device_eval_batch_size=2,  # batch size for evaluation
    warmup_ratio=0.1,  # number of warmup steps for learning rate scheduler
    weight_decay=0.06,  # strength of weight decay
)

model = AutoModelForSequenceClassification.from_pretrained(
    pretrained_model, num_labels=3
)
tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
config = AutoConfig.from_pretrained(pretrained_model, num_labels=3)


def preprocess_function(examples):
    # Tokenize the texts
    return tokenizer(
        examples["premise"],
        examples["hypothesis"],
        padding="max_length",
        max_length=2048,
        truncation=True,
    )


with training_args.main_process_first(desc="train dataset map pre-processing"):
    train_dataset = train_dataset.map(
        preprocess_function,
        batched=True,
        load_from_cache_file=True,
        desc="Running tokenizer on train dataset",
    )
# Log a few random samples from the training set:
for index in random.sample(range(len(train_dataset)), 3):
    logger.info(f"Sample {index} of the training set: {train_dataset[index]}.")

with training_args.main_process_first(desc="prediction dataset map pre-processing"):
    predict_dataset = test_dataset.map(
        preprocess_function,
        batched=True,
        load_from_cache_file=True,
        desc="Running tokenizer on prediction dataset",
    )

metric = evaluate.load("xnli")


def compute_metrics(p: EvalPrediction):
    preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
    preds = np.argmax(preds, axis=1)
    return metric.compute(predictions=preds, references=p.label_ids)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=None,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
    data_collator=None,
)


checkpoint = None
train_result = trainer.train(resume_from_checkpoint=checkpoint)
metrics = train_result.metrics
max_train_samples = len(train_dataset)
metrics["train_samples"] = min(max_train_samples, len(train_dataset))

trainer.save_model()  # Saves the tokenizer too for easy upload

trainer.log_metrics("train", metrics)
trainer.save_metrics("train", metrics)
trainer.save_state()

logger.info("*** Predict ***")
label_list = ["entailment", "neutral", "contradiction"]
predictions, labels, metrics = trainer.predict(
    predict_dataset, metric_key_prefix="predict"
)

max_predict_samples = len(predict_dataset)
metrics["predict_samples"] = min(max_predict_samples, len(predict_dataset))

trainer.log_metrics("predict", metrics)
trainer.save_metrics("predict", metrics)

predictions = np.argmax(predictions, axis=1)
output_predict_file = os.path.join(training_args.output_dir, "predictions.txt")
if trainer.is_world_process_zero():
    with open(output_predict_file, "w") as writer:
        writer.write("index\tprediction\n")
        for index, item in enumerate(predictions):
            item = label_list[item]
            writer.write(f"{index}\t{item}\n")

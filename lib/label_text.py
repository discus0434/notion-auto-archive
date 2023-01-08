import warnings

import pandas as pd
from transformers import pipeline

# Suppress the warning of transformers
warnings.simplefilter("ignore", UserWarning)


def label_text(
    text: str,
    candidate_labels: list[str],
    threshold: float = 0.9,
) -> list[str]:
    """Label the text with the candidate labels, using the zero-shot-classification model.

    Parameters
    ----------
    text : str
        text to be labeled
    candidate_labels : list[str]
        candidate labels, which is given at 'config/config.py'
    threshold : float, optional
        threshold to filter the labels whether the score is higher
        than the threshold or not, by default 0.9
    Returns
    -------
    list[str]
        list of labels
    """

    res = classify_text(text, candidate_labels)

    res = pd.DataFrame({"labels": res["labels"], "scores": res["scores"]})
    labels = res[res["scores"] > threshold].sort_values(by="scores", ascending=False)

    while len(labels) == 0:
        threshold -= 0.05
        labels = res[res["scores"] > threshold].sort_values(
            by="scores", ascending=False
        )

    if len(labels) > 5:
        labels = labels[:5]

    return labels["labels"].tolist()


def classify_text(text: str, candidate_labels: list[str]) -> dict:
    classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    )

    result = classifier(
        text,
        candidate_labels,
        multi_label=True,
        hypothesis_template="This text is about {}.",
    )
    
    return result

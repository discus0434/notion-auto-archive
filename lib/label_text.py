import warnings

from transformers import pipeline

# Suppress the warning of transformers
warnings.simplefilter("ignore", UserWarning)


def label_text(
    text: str, candidate_labels: list[str], threshold: float = 0.45
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
        than the threshold or not, by default 0.45
    Returns
    -------
    list[str]
        list of labels
    """

    result = classify_text(text, candidate_labels)

    result["labels"] = [
        label
        for label, score in zip(result["labels"], result["scores"])
        if score > threshold
    ]

    # if the tags are too many or too few, adjust the threshold
    counter = 0
    while len(result["labels"]) == 0 or len(result["labels"]) >= 4:
        if len(result["labels"]) >= 4:
            threshold += 0.05
            result["labels"] = [
                label
                for label, score in zip(result["labels"], result["scores"])
                if score > threshold
            ]
        else:
            threshold -= 0.05
            result["labels"] = [
                label
                for label, score in zip(result["labels"], result["scores"])
                if score > threshold
            ]

        counter += 1
        if counter > 10:
            break

    return result["labels"]


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

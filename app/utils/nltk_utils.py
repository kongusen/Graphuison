import nltk
from nltk.data import find

def download_if_needed(package):
    """
    若指定的NLTK包未下载，则下载该包。
    """
    try:
        find(f"corpora/{package}")
    except LookupError:
        nltk.download(package)
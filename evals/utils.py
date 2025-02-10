import difflib

def compare_strings(a: str, b: str) -> float:
    """
    Compare two strings and return a similarity ratio.
    This function uses difflib.SequenceMatcher to calculate the similarity between two strings.
    """
    return difflib.SequenceMatcher(None, a, b).ratio() 
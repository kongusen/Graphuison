from fuzzywuzzy import fuzz

def filter_abstracts_by_term(term, abstracts, threshold=70):
    """
    根据术语过滤摘要文本，返回符合条件的摘要列表。
    """
    filtered_abstracts = []
    for abstract in abstracts:
        if isinstance(abstract, str):
            if fuzz.partial_ratio(term.lower(), abstract.lower()) >= threshold:
                filtered_abstracts.append(abstract)
    return filtered_abstracts
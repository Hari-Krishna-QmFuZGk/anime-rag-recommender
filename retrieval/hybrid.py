import math
from typing import List


def bm25_score(query: str, documents: List[str]) -> List[float]:
    query_terms = set(query.lower().split())
    scores = []

    for doc in documents:
        doc_terms = doc.lower().split()
        score = 0.0
        for term in query_terms:
            tf = doc_terms.count(term)
            if tf > 0:
                score += 1 + math.log(tf)
        scores.append(score)

    return scores

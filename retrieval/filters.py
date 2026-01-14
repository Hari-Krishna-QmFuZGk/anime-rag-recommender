from typing import Any, Dict, List, Optional


def build_where(min_year=None, max_year=None, min_score=None, studios=None, **kwargs):
    clauses = []

    if min_year is not None:
        clauses.append({"year": {"$gte": min_year}})
    if max_year is not None:
        clauses.append({"year": {"$lte": max_year}})
    if min_score is not None:
        clauses.append({"score": {"$gte": min_score}})
    if studios:
        clauses.append({"studio": {"$in": studios}})

    return {"$and": clauses} if clauses else {}

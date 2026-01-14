from typing import List, Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class RankedAnime(BaseModel):
    titles: List[str] = Field(description="List of anime titles sorted by rank")


def rerank(query: str, candidates: List[Dict]) -> List[Dict]:
    if not candidates:
        return []

    # Prepare prompt
    prompt = f"User wants anime recommendations for: {query}\n\nRank these anime:\n"
    for i, c in enumerate(candidates):
        prompt += f"{i+1}. {c['title']}\n"
    prompt += "\nReturn the best ones in order."

    # Use LLM for ranking
    llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(RankedAnime)
    response = llm.invoke(prompt)

    # Map titles back to original candidate objects efficiently
    candidates_map = {c["title"]: c for c in candidates}
    ranked = []

    for title in response.titles:
        if title in candidates_map:
            ranked.append(candidates_map[title])

    # Fallback to original candidates if ranking fails to return matches
    return ranked if ranked else candidates

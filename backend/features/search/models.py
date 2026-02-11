from datetime import datetime

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    document: Document
    score: float = Field(..., ge=0)
    reason: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)


class SearchEntry(BaseModel):
    query: str = Field(..., min_length=1)
    timestamp: datetime


class CypherQuery(BaseModel):
    """Fields that can be converted to a Cypher Query in natural language."""

    # TODO
    match_clause: str = Field(..., description="MATCH clause for the Cypher query")
    where_clause: str | None = Field(None, description="Optional WHERE clause for filtering")
    return_clause: str = Field(..., description="RETURN clause specifying what to return")
    limit: int = Field(10, ge=1, description="LIMIT clause for number of results")


    def __str__(self) -> str:
        """TODO"""
        parts = [f"{self.match_clause}"]
        
        if self.where_clause:
            parts.append(f"{self.where_clause}")
        parts.append(f"{self.return_clause}")
        parts.append(f"LIMIT {self.limit}")
        return "\n".join(parts)

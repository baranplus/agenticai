from pydantic import BaseModel, Field

class ValidateQuery(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

def safe_parse_grade(response_text: str) -> ValidateQuery:
    try:
        
        return ValidateQuery.model_validate_json(response_text)
    except Exception:
        
        if "yes" in response_text.lower():
            return ValidateQuery(binary_score="yes")
        return ValidateQuery(binary_score="no")
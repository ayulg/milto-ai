"""
Input validation using Pydantic
"""
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        cleaned = v.replace(".", "").replace("_", "").replace("-", "").replace(" ", "")
        if not cleaned.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=200)


class CoachRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class AssessmentRequest(BaseModel):
    answers: dict = Field(default_factory=dict)


class CareerChangeRequest(BaseModel):
    current: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=100)


class DevelopmentRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=100)


def validate_request(model, data):
    """Validate request and return (validated_data, error)"""
    try:
        return model(**data), None
    except ValidationError as e:
        errors = []
        for err in e.errors():
            field = ".".join(str(x) for x in err["loc"])
            errors.append(f"{field}: {err['msg']}")
        return None, "; ".join(errors)

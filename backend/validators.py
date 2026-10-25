"""
Input validation using Pydantic
"""
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email address")
        return v


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=120)
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

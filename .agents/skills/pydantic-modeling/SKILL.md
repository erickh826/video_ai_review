---
name: pydantic-modeling
description: Create and refactor Pydantic models for FastAPI and backend systems. Use for data validation, schema design, request/response modeling, and serialization logic. Keywords: pydantic, BaseModel, validation, schema, fastapi, data modeling, DTO
---

# Pydantic Modeling Skill

## Purpose

This skill helps design clean, production-ready Pydantic models for:
- FastAPI request/response schemas
- Internal DTOs
- Validation logic
- Settings/config models
- ORM integration

Use this skill whenever:
- Creating API schemas
- Refactoring models
- Adding validation
- Designing nested data structures
- Converting DB models to response models

---

## Conventions

### ✅ Use Pydantic v2 syntax unless specified
- Prefer `BaseModel`
- Use `model_config = ConfigDict(...)`
- Use `field_validator` instead of `validator`
- Use `model_validate()` instead of `parse_obj()`

---

## Base Example

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
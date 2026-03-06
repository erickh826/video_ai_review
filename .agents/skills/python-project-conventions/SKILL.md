---
name: python-project-conventions
description: Enforce consistent Python project structure, naming conventions, and clean architecture. Use for refactoring, organizing files, and improving maintainability.
---

# Python Project Conventions

## Folder Structure

Recommended structure:
app/
api/
core/
models/
schemas/
services/
repositories/
db/
tests/

---

## Naming Conventions

- snake_case → variables, functions, files
- PascalCase → classes
- UPPER_CASE → constants
- verbs → function names
- nouns → class names

---

## Import Rules

- Standard library first
- Third-party second
- Local imports last
- Avoid wildcard imports

Example:

```python
import os
from datetime import datetime

from fastapi import APIRouter

from app.schemas.user import UserCreate
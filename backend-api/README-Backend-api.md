# Backend API - Vertical Slice + CQRS

FastAPI backend service with modern architecture patterns.

## Architecture

### Vertical Slice
Each feature is self-contained:
- Commands (write operations)
- Queries (read operations)
- Models (database)
- Schemas (validation)
- Router (HTTP endpoints)

### CQRS
- **Commands:** POST, PUT, DELETE (modify state)
- **Queries:** GET (read-only)

## Structure
```
app/
├── core/              # Configuration
├── common/            # Shared utilities
└── features/          # VERTICAL SLICES
    └── appointments/
        ├── commands/  # CreateAppointment, UpdateAppointment
        ├── queries/   # GetAppointment, ListAppointments
        ├── models/    # Appointment (SQLAlchemy)
        ├── schemas/   # Appointment (Pydantic)
        └── router.py  # FastAPI endpoints
```

## Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/features/appointments/ -v
```

## Code Quality
```bash
# Format
black app/
isort app/

# Lint
flake8 app/
pylint app/

# Type check
mypy app/
```
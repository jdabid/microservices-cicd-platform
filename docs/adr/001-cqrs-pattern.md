# ADR-001: CQRS Pattern for Feature Architecture

## Status
Accepted

## Date
2026-03-10

## Context
As the medical appointments platform grows, endpoint handlers tend to accumulate both read and write logic in a single service layer. This leads to several problems:

- **Mixed concerns**: A single service file handles creation, validation, querying, and filtering, making it difficult to reason about side effects.
- **Testing complexity**: Unit tests must mock both read and write dependencies even when testing only one path.
- **Scalability constraints**: Read-heavy and write-heavy workloads cannot be optimized or scaled independently.
- **Team collaboration**: Multiple developers editing the same service file increases merge conflicts.

The project follows a Vertical Slice Architecture where each feature (appointments, patients, auth) is a self-contained module. A complementary pattern was needed to organize the internal logic of each slice.

## Decision
Implement Command Query Responsibility Segregation (CQRS) within each vertical slice by separating write operations (commands) from read operations (queries) into dedicated directories.

Each feature follows this structure:

```
features/<feature>/
  commands/       # Write operations: create, update, delete, cancel
  queries/        # Read operations: get_by_id, list, search, filter
  models/         # SQLAlchemy ORM models
  schemas/        # Pydantic v2 request/response schemas
  router.py       # FastAPI router wiring commands and queries
```

Key rules:
- Commands perform mutations and return the created/updated resource.
- Queries are read-only and never modify state.
- Commands and queries each have their own module files (e.g., `create_appointment.py`, `get_appointments.py`).
- The router imports from both directories and delegates accordingly.
- Cross-feature communication goes through dependency injection, never direct imports between features.

## Consequences

### Positive
- **Clear separation of concerns**: Developers immediately know where to find read vs. write logic.
- **Easier testing**: Command tests focus on mutations and side effects; query tests focus on filtering and response shapes. Mocking is simpler because each unit has a narrow scope.
- **Independent optimization**: Queries can use read replicas, caching (Redis), or denormalized views without affecting command logic.
- **Scalability path**: In the future, commands could publish domain events while queries subscribe to projections, enabling eventual consistency if needed.
- **Onboarding clarity**: New contributors can follow a consistent, predictable file layout across all features.

### Negative
- **More files per feature**: Each feature has at minimum 5-6 directories, which can feel heavyweight for simple CRUD operations.
- **Potential duplication**: Some validation or model-loading logic may appear in both commands and queries, requiring shared utilities in `common/`.
- **Overhead for simple features**: A feature with only one read and one write endpoint still requires the full directory structure.

### Risks
- **Over-engineering for current scale**: The platform currently has three features. Full CQRS adds structure that may not pay off until the service count grows.
- **Drift from pattern**: Without code review enforcement, developers might add write logic inside query modules or vice versa.

## Alternatives Considered

### Traditional Service Layer
A single `service.py` per feature containing all business logic.
- **Rejected because**: Leads to large files with mixed read/write concerns. Harder to test individual operations in isolation. Does not provide a natural scaling boundary.

### Repository Pattern Alone
Use repositories for data access with services on top, without separating reads from writes.
- **Rejected because**: Repositories handle data access but do not enforce separation of intent. The same service method could still mix queries with mutations. CQRS provides a higher-level organizational boundary that complements repositories.

### Event Sourcing + CQRS
Full event sourcing where commands emit events and queries rebuild state from event streams.
- **Rejected because**: Adds significant complexity (event store, projections, eventual consistency) that is not justified for a portfolio-scale application. The current approach uses CQRS at the application layer without event sourcing, keeping the benefits of separation without the infrastructure overhead.

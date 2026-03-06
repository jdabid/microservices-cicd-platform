You are implementing a user story from the project backlog.

The user will specify which story to implement (e.g., "US-04", "US-14", or a description).

Steps:
1. Read docs/evaluations/cronograma-scrum.md to find the exact user story, its acceptance criteria, and its sprint context.
2. Read CLAUDE.md to understand coding conventions.
3. Analyze the current codebase to understand existing patterns (read relevant existing files first).
4. Implement the story following these rules:
   - Follow the EXACT same patterns already used in the codebase (look at appointments/ as reference for new features)
   - Follow CQRS: commands/ for writes, queries/ for reads
   - Add type hints on everything
   - Use Pydantic v2 validators
   - Use async/await properly
   - Write tests for all new code (unit tests at minimum)
   - Never leave files empty
5. After implementation, run the tests to verify everything passes.
6. Show a summary of what was implemented and what files were created/modified.

IMPORTANT: Do NOT create placeholder or stub implementations. Every file must have real, working code.

Story to implement: $ARGUMENTS

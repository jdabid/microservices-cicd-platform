Run the test suite and analyze results.

Steps:
1. Check if virtual environment exists at backend-api/venv/
2. Run tests with coverage:
   ```
   cd backend-api && source venv/bin/activate && python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing 2>&1
   ```
3. Analyze the output and suggest fixes for failures.

If $ARGUMENTS is provided, run only those specific tests.

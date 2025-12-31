# WordVoyage Frontend End-to-End Tests

Comprehensive browser-based end-to-end tests for the WordVoyage frontend application.

## Architecture

- **Double Container Setup**: Browserless Chromium + Test Runner
- **Framework**: Playwright (Python)
- **Screenshot Management**: Organized by test run and test case
- **Client Abstraction**: PlaywrightClient encapsulates browser operations

## Prerequisites

- Podman (or Docker)
- Backend service running on port 8080
- set envs
    * SERVICE_OPENAI_BASE_URL
    * SERVICE_OPENAI_API_KEY
    * SERVICE_OPENAI_MODEL

## Usage

### Run All Tests (with auto-start frontend)

```bash
frontend/end-to-end/test.sh
```

This will:
1. Start Frontend service (via deploy.sh)
2. Start Browserless Chromium
3. Run all test cases
4. Clean up all services and containers

### View Screenshots

Screenshots are organized by test run timestamp:

```
build/screenshots/
└── 2025-12-30_14-30-25/
    ├── test_game_initialization/
    │   ├── 01_page_load_start.png
    │   ├── 02_page_ready.png
    │   └── 03_final_state.png
    ├── test_single_user_input/
    │   ├── 01_initial_state.png
    │   ├── 02_input_submitted.png
    │   └── 03_event_received.png
    └── ...
```

## Development

### Adding New Tests

1. Create test file in `src/case/`
2. Import test functions in `src/run_tests.py`
3. Add test invocations in `run_all_tests()`

### PlaywrightClient Methods

- `navigate_to_game()`: Navigate to game page
- `wait_for_game_ready()`: Wait for page initialization
- `get_current_event_text()`: Get current event description
- `get_context_state()`: Get game state dictionary
- `get_history_count()`: Get number of history entries
- `submit_user_input(text)`: Submit user input
- `wait_for_new_event(previous_text)`: Wait for event change
- `check_error_message()`: Check for error messages
- `capture_screenshot(name)`: Take screenshot

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

## Usage

### Run All Tests (with auto-start frontend)

```bash
cd frontend/end-to-end
./test.sh
```

This will:
1. Start Frontend service (via deploy.sh)
2. Start Browserless Chromium
3. Run all test cases
4. Clean up all services and containers

### Options

```bash
# Skip building frontend image (use existing)
./test.sh --skip-build

# Only cleanup containers (without running tests)
./test.sh --cleanup-only

# Show help
./test.sh --help
```

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

## Test Cases

### 1. test_game_initialization
- Page loads successfully
- Event description appears
- Context state is displayed
- Input form is accessible
- No error messages

### 2. test_single_user_input
- User input submission works
- New event appears after input
- History count increases

### 3. test_multiple_sequential_inputs
- Multiple inputs processed sequentially
- State updates for each input
- History grows correctly

### 4. test_context_update_after_input
- Context state updates after actions
- State values are valid

### 5. test_history_list_updates
- History list grows with each action
- Count matches expected

### 6. test_event_display_updates
- Event text updates properly
- Events are different (not identical)

### 7. test_context_display_structure
- Context has proper structure
- All fields are valid types

## Configuration

Environment variables (set in test.sh or override):

- `FRONTEND_URL`: Frontend service URL (default: http://localhost:3000)
- `BROWSER_WS_URL`: Browserless WebSocket URL (default: ws://localhost:3003/...)
- `SCREENSHOT_DIR`: Screenshot output directory (default: /app/screenshots)
- `TEST_TIMEOUT`: Test timeout in seconds (default: 30)
- `PAGE_LOAD_TIMEOUT`: Page load timeout in seconds (default: 15)

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

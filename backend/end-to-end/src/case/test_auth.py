"""Authentication tests"""

import time
import random
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def _generate_test_email(prefix: str = "test") -> str:
    """Generate unique test email with timestamp and random suffix"""
    return f"{prefix}_{int(time.time())}_{random.randint(1000, 9999)}@example.com"


def test_anonymous_to_registered(client: BackendGameClient, result: TestResult):
    """Test anonymous user registration preserves session"""
    test_name = "Anonymous to Registered User"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        response = test_client.start_game()
        session_id_before = response.get('sessionId')
        print(f"  Session ID before registration: {session_id_before}")

        test_client.process_step("look around")
        test_client.process_step("check inventory")

        history_before = test_client.get_history()
        steps_count_before = len(history_before.get('steps', []))
        print(f"  Steps before registration: {steps_count_before}")

        email = _generate_test_email()
        password = "TestPassword123!"
        register_response = test_client.register_user(email, password)

        assert 'user' in register_response
        assert 'accessToken' in register_response
        assert 'refreshToken' in register_response
        assert register_response['user']['email'] == email
        print(f"  Registered user: {email}")

        session_id_after = test_client.get_session_id()
        assert session_id_before == session_id_after, "Session ID changed after registration"
        print(f"  ✓ Session ID preserved")

        history_after = test_client.get_history()
        steps_count_after = len(history_after.get('steps', []))
        assert steps_count_after == steps_count_before, "History lost after registration"
        print(f"  ✓ History preserved ({steps_count_after} steps)")

        test_client.process_step("continue")
        print(f"  ✓ Game continues seamlessly")

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_user_login(client: BackendGameClient, result: TestResult):
    """Test registered user login and session access"""
    test_name = "User Login"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()
        password = "TestPassword123!"
        test_client.register_user(email, password)

        test_client.process_step("explore")
        session_id = test_client.get_session_id()
        print(f"  Created session: {session_id}")

        new_client = BackendGameClient(client.service_url)
        login_response = new_client.login_user(email, password)

        assert 'user' in login_response
        assert 'accessToken' in login_response
        assert 'refreshToken' in login_response
        assert login_response['user']['email'] == email
        print(f"  ✓ Login successful")

        new_client.set_jwt_header(login_response['accessToken'])
        context_response = new_client.get_context_by_id(session_id)
        assert context_response.status_code == 200
        print(f"  ✓ Can access session with JWT")

        test_client.close()
        new_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_logout(client: BackendGameClient, result: TestResult):
    """Test logout revokes refresh token"""
    test_name = "Logout"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()
        password = "TestPassword123!"
        register_response = test_client.register_user(email, password)
        refresh_token = register_response['refreshToken']

        logout_response = test_client.logout(refresh_token)
        assert 'message' in logout_response or 'error' not in logout_response
        print(f"  ✓ Logout successful")

        try:
            test_client.refresh_token(refresh_token)
            raise AssertionError("Refresh token should be revoked")
        except Exception as e:
            if "401" in str(e) or "Invalid" in str(e):
                print(f"  ✓ Refresh token revoked")
            else:
                raise

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_token_refresh(client: BackendGameClient, result: TestResult):
    """Test token refresh endpoint"""
    test_name = "Token Refresh"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()
        password = "TestPassword123!"
        register_response = test_client.register_user(email, password)
        refresh_token = register_response['refreshToken']

        refresh_response = test_client.refresh_token(refresh_token)
        assert 'accessToken' in refresh_response
        assert 'refreshToken' in refresh_response
        print(f"  ✓ New tokens obtained")

        test_client.set_jwt_header(refresh_response['accessToken'])
        session_id = test_client.get_session_id()
        context_response = test_client.get_context_by_id(session_id)
        assert context_response.status_code == 200
        print(f"  ✓ New access token works")

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_cross_user_session_access(client: BackendGameClient, result: TestResult):
    """Test users cannot access other users' sessions"""
    test_name = "Cross-User Session Access Prevention"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        client_a = BackendGameClient(client.service_url)
        client_a.start_game()
        email_a = _generate_test_email("test_a")
        client_a.register_user(email_a, "Password123!")
        session_a = client_a.get_session_id()
        print(f"  User A session: {session_a}")

        client_b = BackendGameClient(client.service_url)
        client_b.start_game()
        email_b = _generate_test_email("test_b")
        tokens_b = client_b.register_user(email_b, "Password123!")
        client_b.set_jwt_header(tokens_b['accessToken'])
        print(f"  User B registered")

        context_response = client_b.get_context_by_id(session_a)
        assert context_response.status_code in [403, 404], f"Expected 403/404, got {context_response.status_code}"
        print(f"  ✓ Context access denied ({context_response.status_code})")

        history_response = client_b.get_history_by_id(session_a)
        assert history_response.status_code in [403, 404], f"Expected 403/404, got {history_response.status_code}"
        print(f"  ✓ History access denied ({history_response.status_code})")

        client_a.close()
        client_b.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_anonymous_session_isolation(client: BackendGameClient, result: TestResult):
    """Test multiple anonymous users have isolated sessions"""
    test_name = "Anonymous Session Isolation"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        client_a = BackendGameClient(client.service_url)
        response_a = client_a.start_game()
        session_a = response_a.get('sessionId')
        client_a.process_step("go north")
        print(f"  Anonymous user A session: {session_a}")

        client_b = BackendGameClient(client.service_url)
        response_b = client_b.start_game()
        session_b = response_b.get('sessionId')
        client_b.process_step("go south")
        print(f"  Anonymous user B session: {session_b}")

        assert session_a != session_b, "Sessions should be different"
        print(f"  ✓ Different session IDs")

        history_a = client_a.get_history()
        history_b = client_b.get_history()
        steps_a = history_a.get('steps', [])
        steps_b = history_b.get('steps', [])

        assert len(steps_a) > 0 and len(steps_b) > 0
        last_input_a = steps_a[-1].get('userInput', '')
        last_input_b = steps_b[-1].get('userInput', '')
        assert last_input_a != last_input_b, "Histories should be independent"
        print(f"  ✓ Independent histories")

        client_a.close()
        client_b.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_register_preserves_ownership(client: BackendGameClient, result: TestResult):
    """Test registration transfers session ownership correctly"""
    test_name = "Register Preserves Session Ownership"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        client_a = BackendGameClient(client.service_url)
        client_a.start_game()
        email_a = _generate_test_email("test_a")
        tokens_a = client_a.register_user(email_a, "Password123!")
        session_a = client_a.get_session_id()
        print(f"  User A registered, session: {session_a}")

        new_client_a = BackendGameClient(client.service_url)
        new_client_a.login_user(email_a, "Password123!")
        new_client_a.set_jwt_header(tokens_a['accessToken'])
        context_response = new_client_a.get_context_by_id(session_a)
        assert context_response.status_code == 200
        print(f"  ✓ User A can access own session")

        client_b = BackendGameClient(client.service_url)
        client_b.start_game()
        email_b = _generate_test_email("test_b")
        tokens_b = client_b.register_user(email_b, "Password123!")
        client_b.set_jwt_header(tokens_b['accessToken'])

        context_response_b = client_b.get_context_by_id(session_a)
        assert context_response_b.status_code in [403, 404], f"Expected 403/404, got {context_response_b.status_code}"
        print(f"  ✓ User B cannot access User A's session")

        client_a.close()
        new_client_a.close()
        client_b.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_invalid_credentials(client: BackendGameClient, result: TestResult):
    """Test login fails with invalid credentials"""
    test_name = "Invalid Credentials"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()
        password = "TestPassword123!"
        test_client.register_user(email, password)

        try:
            test_client.login_user(email, "WrongPassword")
            raise AssertionError("Login should fail with wrong password")
        except Exception as e:
            if "401" in str(e):
                print(f"  ✓ Wrong password rejected (401)")
            else:
                raise

        try:
            test_client.login_user("nonexistent@example.com", password)
            raise AssertionError("Login should fail with non-existent email")
        except Exception as e:
            if "401" in str(e):
                print(f"  ✓ Non-existent email rejected (401)")
            else:
                raise

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_duplicate_email(client: BackendGameClient, result: TestResult):
    """Test registration fails for duplicate email"""
    test_name = "Duplicate Email Registration"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()
        password = "TestPassword123!"
        test_client.register_user(email, password)
        print(f"  First registration: {email}")

        client_b = BackendGameClient(client.service_url)
        client_b.start_game()

        try:
            client_b.register_user(email, "DifferentPassword123!")
            raise AssertionError("Registration should fail for duplicate email")
        except Exception as e:
            if "400" in str(e):
                print(f"  ✓ Duplicate email rejected (400)")
            else:
                raise

        test_client.close()
        client_b.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_empty_password(client: BackendGameClient, result: TestResult):
    """Test registration validates password requirements"""
    test_name = "Empty Password Validation"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        email = _generate_test_email()

        try:
            test_client.register_user(email, "")
            raise AssertionError("Registration should fail with empty password")
        except Exception as e:
            if "400" in str(e):
                print(f"  ✓ Empty password rejected (400)")
            else:
                raise

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_malformed_email(client: BackendGameClient, result: TestResult):
    """Test registration validates email format"""
    test_name = "Malformed Email Validation"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        test_client = BackendGameClient(client.service_url)
        test_client.start_game()
        password = "TestPassword123!"

        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com"
        ]

        for invalid_email in invalid_emails:
            try:
                test_client.register_user(invalid_email, password)
                raise AssertionError(f"Registration should fail for: {invalid_email}")
            except Exception as e:
                if "400" in str(e):
                    print(f"  ✓ Invalid email rejected: {invalid_email}")
                else:
                    raise

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise

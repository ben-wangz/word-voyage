"""i18n (Internationalization) tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


# Expected translations for initial game content
EXPECTED_TRANSLATIONS = {
    "en": {
        "location": "Crashed Spaceship",
        "health_desc": "Health points",
        "hunger_desc": "Hunger level",
        "thirst_desc": "Thirst level",
        "energy_desc": "Energy level",
        "location_desc": "Current location",
        "event_keyword": "spacecraft",  # Keyword from event description (@file:)
    },
    "zh": {
        "location": "坠毁的飞船",
        "health_desc": "生命值",
        "hunger_desc": "饥饿度",
        "thirst_desc": "口渴度",
        "energy_desc": "精力值",
        "location_desc": "当前位置",
        "event_keyword": "飞船",  # Keyword from Chinese event description (@file:)
    }
}


def test_game_init_i18n(client: BackendGameClient, result: TestResult):
    """Test that game initial content is correctly translated based on language parameter"""
    test_name = "i18n Game Initialization"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        # Test English version
        print(f"\n--- Testing English (lang=en) ---")
        en_response = client.start_game(lang="en")

        assert 'step' in en_response, "Expected step in English response"
        en_step = en_response.get('step')
        en_context = en_step.get('context', {})
        en_state = en_context.get('state', {})

        # Verify English location
        en_location_value = en_state.get('location', {}).get('value', '')
        en_location_desc = en_state.get('location', {}).get('description', '')
        print(f"  Location value: {en_location_value}")
        print(f"  Location desc: {en_location_desc}")

        assert en_location_value == EXPECTED_TRANSLATIONS["en"]["location"], \
            f"Expected English location '{EXPECTED_TRANSLATIONS['en']['location']}', got '{en_location_value}'"
        assert en_location_desc == EXPECTED_TRANSLATIONS["en"]["location_desc"], \
            f"Expected English location desc '{EXPECTED_TRANSLATIONS['en']['location_desc']}', got '{en_location_desc}'"

        # Verify English state field descriptions
        en_health_desc = en_state.get('health', {}).get('description', '')
        print(f"  Health desc: {en_health_desc}")
        assert en_health_desc == EXPECTED_TRANSLATIONS["en"]["health_desc"], \
            f"Expected English health desc '{EXPECTED_TRANSLATIONS['en']['health_desc']}', got '{en_health_desc}'"

        en_hunger_desc = en_state.get('hunger', {}).get('description', '')
        assert en_hunger_desc == EXPECTED_TRANSLATIONS["en"]["hunger_desc"], \
            f"Expected English hunger desc '{EXPECTED_TRANSLATIONS['en']['hunger_desc']}', got '{en_hunger_desc}'"

        # Verify English event description (loaded via @file:)
        en_event_desc = en_step.get('event', {}).get('description', '')
        print(f"  Event desc keyword: {EXPECTED_TRANSLATIONS['en']['event_keyword']}")
        assert EXPECTED_TRANSLATIONS["en"]["event_keyword"] in en_event_desc, \
            f"Expected keyword '{EXPECTED_TRANSLATIONS['en']['event_keyword']}' in event description, got '{en_event_desc[:100]}'"

        print(f"  ✓ English translations verified (including @file: content)")

        # Test Chinese version
        print(f"\n--- Testing Chinese (lang=zh) ---")
        zh_response = client.start_game(lang="zh")

        assert 'step' in zh_response, "Expected step in Chinese response"
        zh_step = zh_response.get('step')
        zh_context = zh_step.get('context', {})
        zh_state = zh_context.get('state', {})

        # Verify Chinese location
        zh_location_value = zh_state.get('location', {}).get('value', '')
        zh_location_desc = zh_state.get('location', {}).get('description', '')
        print(f"  Location value: {zh_location_value}")
        print(f"  Location desc: {zh_location_desc}")

        assert zh_location_value == EXPECTED_TRANSLATIONS["zh"]["location"], \
            f"Expected Chinese location '{EXPECTED_TRANSLATIONS['zh']['location']}', got '{zh_location_value}'"
        assert zh_location_desc == EXPECTED_TRANSLATIONS["zh"]["location_desc"], \
            f"Expected Chinese location desc '{EXPECTED_TRANSLATIONS['zh']['location_desc']}', got '{zh_location_desc}'"

        # Verify Chinese state field descriptions
        zh_health_desc = zh_state.get('health', {}).get('description', '')
        print(f"  Health desc: {zh_health_desc}")
        assert zh_health_desc == EXPECTED_TRANSLATIONS["zh"]["health_desc"], \
            f"Expected Chinese health desc '{EXPECTED_TRANSLATIONS['zh']['health_desc']}', got '{zh_health_desc}'"

        zh_hunger_desc = zh_state.get('hunger', {}).get('description', '')
        assert zh_hunger_desc == EXPECTED_TRANSLATIONS["zh"]["hunger_desc"], \
            f"Expected Chinese hunger desc '{EXPECTED_TRANSLATIONS['zh']['hunger_desc']}', got '{zh_hunger_desc}'"

        # Verify Chinese event description (loaded via @file:)
        zh_event_desc = zh_step.get('event', {}).get('description', '')
        print(f"  Event desc keyword: {EXPECTED_TRANSLATIONS['zh']['event_keyword']}")
        assert EXPECTED_TRANSLATIONS["zh"]["event_keyword"] in zh_event_desc, \
            f"Expected keyword '{EXPECTED_TRANSLATIONS['zh']['event_keyword']}' in event description, got '{zh_event_desc[:100]}'"

        print(f"  ✓ Chinese translations verified (including @file: content)")

        # Verify that English and Chinese are different
        print(f"\n--- Verifying English != Chinese ---")
        assert en_location_value != zh_location_value, \
            "English and Chinese location values should be different"
        assert en_health_desc != zh_health_desc, \
            "English and Chinese health descriptions should be different"
        assert en_event_desc != zh_event_desc, \
            "English and Chinese event descriptions should be different"

        print(f"  ✓ English and Chinese content are different")
        print(f"  ✓ @file: references are correctly loaded and translated")
        print(f"\n  ✓ i18n capability verified successfully")

        result.add(test_name, "success", time.time() - start_time)

    except AssertionError as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise

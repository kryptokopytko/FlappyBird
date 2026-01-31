#!/usr/bin/env python3
"""Test effect stacking/extending mechanism."""

import sys
sys.path.insert(0, "src")

from effects import EffectManager, ShieldEffect, SlowMotionEffect, SpeedUpEffect


class MockGame:
    """Mock game object for testing."""
    def __init__(self):
        self.scroll_speed = 2.0
        self.bird = MockBird()


class MockBird:
    """Mock bird object for testing."""
    def __init__(self):
        self.has_shield = False


def test_effect_extending():
    """Test that collecting same effect extends duration."""
    print("=" * 60)
    print("Test 1: Effect Duration Extending")
    print("=" * 60)

    game = MockGame()
    manager = EffectManager(game)

    # Add first shield (10s)
    manager.add_effect("shield")
    assert len(manager.active_effects) == 1
    shield = manager.active_effects[0]
    print(f"✓ Added first shield: duration={shield.duration}s")

    # Simulate 3 seconds passing
    manager.update(3.0)
    remaining = shield.get_remaining_time()
    print(f"✓ After 3s: remaining={remaining:.1f}s")
    assert abs(remaining - 7.0) < 0.1

    # Add second shield (should extend by 10s more)
    manager.add_effect("shield")
    assert len(manager.active_effects) == 1  # Still one effect
    shield = manager.active_effects[0]
    remaining = shield.get_remaining_time()
    print(f"✓ Added second shield: total duration={shield.duration}s, remaining={remaining:.1f}s")
    assert abs(remaining - 17.0) < 0.1  # 7s + 10s = 17s

    print("✓ Test 1 PASSED: Effects extend duration!\n")


def test_speed_effects_no_bug():
    """Test that speed effects don't have the original_speed bug."""
    print("=" * 60)
    print("Test 2: Speed Effects Bug Fix")
    print("=" * 60)

    game = MockGame()
    manager = EffectManager(game)

    base_speed = game.scroll_speed
    print(f"Base speed: {base_speed}")

    # Add slow motion
    manager.add_effect("slow_motion")
    print(f"✓ Added slow_motion: speed={game.scroll_speed}")
    assert abs(game.scroll_speed - base_speed * 0.5) < 0.01

    # Add another slow motion (should extend, not reapply)
    manager.add_effect("slow_motion")
    print(f"✓ Added second slow_motion: speed={game.scroll_speed} (should be same)")
    assert abs(game.scroll_speed - base_speed * 0.5) < 0.01  # Should still be 0.5x

    # Remove all effects
    manager.clear_all()
    print(f"✓ Cleared all effects: speed={game.scroll_speed}")
    assert abs(game.scroll_speed - base_speed) < 0.01  # Should be back to base

    print("✓ Test 2 PASSED: No speed bug!\n")


def test_multiple_different_effects():
    """Test multiple different effects active at once."""
    print("=" * 60)
    print("Test 3: Multiple Different Effects")
    print("=" * 60)

    game = MockGame()
    manager = EffectManager(game)

    base_speed = game.scroll_speed

    # Add shield and slow_motion
    manager.add_effect("shield")
    manager.add_effect("slow_motion")

    assert len(manager.active_effects) == 2
    assert game.bird.has_shield == True
    assert abs(game.scroll_speed - base_speed * 0.5) < 0.01
    print(f"✓ Added shield + slow_motion: {len(manager.active_effects)} effects active")

    # Add speed_up (should work alongside slow_motion)
    manager.add_effect("speed_up")
    assert len(manager.active_effects) == 3
    expected_speed = base_speed * 0.5 * 1.5  # slow * speed_up
    print(f"✓ Added speed_up: speed={game.scroll_speed}, expected={expected_speed}")
    assert abs(game.scroll_speed - expected_speed) < 0.01

    # Remove slow_motion
    manager.remove_effect_by_type("slow_motion")
    expected_speed = base_speed * 1.5  # only speed_up
    print(f"✓ Removed slow_motion: speed={game.scroll_speed}, expected={expected_speed}")
    assert abs(game.scroll_speed - expected_speed) < 0.01

    # Remove speed_up
    manager.remove_effect_by_type("speed_up")
    print(f"✓ Removed speed_up: speed={game.scroll_speed}, expected={base_speed}")
    assert abs(game.scroll_speed - base_speed) < 0.01

    print("✓ Test 3 PASSED: Multiple effects work correctly!\n")


def test_stacking_same_effect_multiple_times():
    """Test collecting same effect many times."""
    print("=" * 60)
    print("Test 4: Stacking Same Effect Multiple Times")
    print("=" * 60)

    game = MockGame()
    manager = EffectManager(game)

    # Add shield 5 times
    for i in range(5):
        manager.add_effect("shield")
        shield = manager.active_effects[0]
        expected_duration = 10.0 * (i + 1)
        print(f"  Shield #{i+1}: total_duration={shield.duration}s")
        assert abs(shield.duration - expected_duration) < 0.1

    assert len(manager.active_effects) == 1
    shield = manager.active_effects[0]
    print(f"✓ After 5 shields: duration={shield.duration}s (expected 50s)")
    assert abs(shield.duration - 50.0) < 0.1

    print("✓ Test 4 PASSED: Can stack effects many times!\n")


if __name__ == "__main__":
    try:
        test_effect_extending()
        test_speed_effects_no_bug()
        test_multiple_different_effects()
        test_stacking_same_effect_multiple_times()

        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nSummary:")
        print("• Effects extend duration when collected multiple times")
        print("• Speed effects don't have original_speed bug")
        print("• Multiple different effects can be active simultaneously")
        print("• Effects stack correctly even when collected many times")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

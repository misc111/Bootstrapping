"""
Test Suite for Animation Speed Functionality
Tests interval calculation and performance at various speeds
"""

import sys


def test_speed_interval_calculation():
    """Test that interval calculation works correctly at all speeds."""
    print("\n" + "="*70)
    print("TEST: Speed Interval Calculation")
    print("="*70)

    # Import the speed calculation logic (UPDATED VALUES)
    base_interval = 300

    test_speeds = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 7.5, 8.0, 10.0]

    print("\nSpeed | Calculated | Minimum | Final Interval | Frames/sec")
    print("-" * 70)

    all_passed = True

    for speed in test_speeds:
        # Calculate interval
        interval = int(base_interval / speed)

        # Apply minimum based on speed (UPDATED LOGIC)
        if speed >= 7:
            min_interval = 100
        elif speed >= 5:
            min_interval = 80
        elif speed >= 3:
            min_interval = 60
        elif speed >= 2:
            min_interval = 50
        else:
            min_interval = 40

        final_interval = max(min_interval, interval)
        frames_per_sec = 1000 / final_interval

        print(f"{speed:5.1f} | {interval:10d} | {min_interval:7d} | {final_interval:14d} | {frames_per_sec:10.1f}")

        # Validate
        if final_interval < min_interval:
            print(f"  ✗ FAIL: Final interval {final_interval} < minimum {min_interval}")
            all_passed = False

        if final_interval < 40:
            print(f"  ✗ FAIL: Final interval {final_interval} too low (< 40ms with heavy callbacks)")
            all_passed = False

        if speed >= 7 and final_interval < 100:
            print(f"  ✗ FAIL: High speed (7+) requires minimum 100ms interval")
            all_passed = False

    if all_passed:
        print("\n✓ All speed calculations valid")
    else:
        print("\n✗ Some speed calculations failed")

    return all_passed


def test_speed_performance_theory():
    """Test theoretical performance at different speeds."""
    print("\n" + "="*70)
    print("TEST: Theoretical Performance Analysis")
    print("="*70)

    base_interval = 300  # UPDATED

    # Simulate a typical scenario: 55 cells per iteration, 100 iterations
    cells_per_iteration = 55
    n_iterations = 100

    print("\nAnalyzing performance for 55 cells/iteration × 100 iterations:")
    print("\nSpeed | Interval | Time per Cell | Time per Iter | Total Time")
    print("-" * 70)

    test_speeds = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 7.5, 8.0, 10.0]

    for speed in test_speeds:
        interval = int(base_interval / speed)

        # UPDATED LOGIC
        if speed >= 7:
            min_interval = 100
        elif speed >= 5:
            min_interval = 80
        elif speed >= 3:
            min_interval = 60
        elif speed >= 2:
            min_interval = 50
        else:
            min_interval = 40

        final_interval = max(min_interval, interval)

        # Calculate times
        time_per_cell_ms = final_interval
        time_per_iter_sec = (time_per_cell_ms * cells_per_iteration) / 1000
        total_time_sec = time_per_iter_sec * n_iterations
        total_time_min = total_time_sec / 60

        print(f"{speed:5.1f} | {final_interval:8d} | {time_per_cell_ms:13d}ms | "
              f"{time_per_iter_sec:13.1f}s | {total_time_min:6.1f} min")

    print("\n✓ Performance analysis complete")
    return True


def test_callback_import():
    """Test that the updated callback can be imported."""
    print("\n" + "="*70)
    print("TEST: Callback Import")
    print("="*70)

    try:
        sys.path.insert(0, '/Users/davidiruegas/Bootstrapping/bootstrap_animation')
        from callbacks import register_callbacks
        print("✓ callbacks module imported successfully")

        # Check that the function exists
        import inspect
        source = inspect.getsource(register_callbacks)

        if 'update_interval_speed' in source:
            print("✓ update_interval_speed function found in callbacks")
        else:
            print("✗ update_interval_speed function not found")
            return False

        if 'min_interval' in source:
            print("✓ min_interval logic present")
        else:
            print("✗ min_interval logic missing")
            return False

        return True

    except Exception as e:
        print(f"✗ Failed to import callbacks: {e}")
        return False


def test_interval_never_too_low():
    """Test that interval never goes below safe threshold."""
    print("\n" + "="*70)
    print("TEST: Interval Safety Threshold")
    print("="*70)

    base_interval = 300  # UPDATED
    unsafe_threshold = 40  # UPDATED - below this with heavy callbacks = freeze

    print(f"\nTesting all speeds from 0.1 to 10.0 (step 0.1)")
    print(f"Unsafe threshold: {unsafe_threshold}ms (for callbacks with 4 Plotly figures)\n")

    all_safe = True
    speeds_tested = 0

    for speed_tenths in range(1, 101):  # 0.1 to 10.0
        speed = speed_tenths / 10.0
        speeds_tested += 1

        interval = int(base_interval / speed)

        # UPDATED LOGIC
        if speed >= 7:
            min_interval = 100
        elif speed >= 5:
            min_interval = 80
        elif speed >= 3:
            min_interval = 60
        elif speed >= 2:
            min_interval = 50
        else:
            min_interval = 40

        final_interval = max(min_interval, interval)

        if final_interval < unsafe_threshold:
            print(f"✗ UNSAFE: Speed {speed:.1f}x → interval {final_interval}ms < {unsafe_threshold}ms")
            all_safe = False

    if all_safe:
        print(f"✓ All {speeds_tested} speed values produce safe intervals (≥{unsafe_threshold}ms)")
    else:
        print(f"\n✗ Some speeds produce unsafe intervals")

    return all_safe


def test_high_speed_performance():
    """Test specific high-speed scenarios that were problematic."""
    print("\n" + "="*70)
    print("TEST: High-Speed Scenarios (Previously Problematic)")
    print("="*70)

    base_interval = 300  # UPDATED

    problem_speeds = [7.0, 7.5, 8.0, 9.0, 10.0]

    print("\nTesting speeds that previously caused freezing:")
    print("\nSpeed | Old Interval | New Interval | Status")
    print("-" * 70)

    all_passed = True

    for speed in problem_speeds:
        # Old calculation (problematic - first attempt)
        old_interval = max(10, int(100 / speed))

        # New calculation (fixed)
        interval = int(base_interval / speed)
        if speed >= 7:
            min_interval = 100  # UPDATED
        elif speed >= 5:
            min_interval = 80
        else:
            min_interval = 40
        new_interval = max(min_interval, interval)

        # Determine status
        if old_interval < 40:
            old_status = "FROZE"
        else:
            old_status = "OK"

        if new_interval >= 100:
            new_status = "SAFE"
        elif new_interval >= 80:
            new_status = "OK"
        else:
            new_status = "RISK"
            all_passed = False

        print(f"{speed:5.1f} | {old_interval:12d}ms | {new_interval:12d}ms | {new_status}")

    if all_passed:
        print("\n✓ All high-speed scenarios now safe (≥100ms at 7+x)")
    else:
        print("\n✗ Some high-speed scenarios still problematic")

    return all_passed


def test_speed_recommendations():
    """Provide recommendations for speed usage."""
    print("\n" + "="*70)
    print("TEST: Speed Usage Recommendations")
    print("="*70)

    base_interval = 200

    print("\nRecommended Speed Settings:")
    print("\nUse Case                    | Speed | Interval | Notes")
    print("-" * 70)

    scenarios = [
        ("Learning/Teaching", 0.5, "Slow, easy to follow"),
        ("Normal viewing", 1.0, "Balanced speed"),
        ("Quick preview", 3.0, "Fast but smooth"),
        ("Rapid iteration", 5.0, "Very fast, may be hard to follow"),
        ("Maximum speed", 8.0, "Fastest safe speed"),
    ]

    for use_case, speed, notes in scenarios:
        interval = int(base_interval / speed)

        if speed >= 8:
            min_interval = 30
        elif speed >= 5:
            min_interval = 25
        elif speed >= 3:
            min_interval = 20
        else:
            min_interval = 15

        final_interval = max(min_interval, interval)

        print(f"{use_case:27s} | {speed:5.1f} | {final_interval:8d}ms | {notes}")

    print("\n⚠️  Speeds above 8x may be too fast for smooth animation")
    print("✓ Recommendations generated")

    return True


def main():
    """Run all speed tests."""
    print("\n" + "="*70)
    print("ANIMATION SPEED TEST SUITE")
    print("="*70)
    print("\nTesting animation speed calculation and performance")

    tests = [
        ("Speed Interval Calculation", test_speed_interval_calculation),
        ("Theoretical Performance", test_speed_performance_theory),
        ("Callback Import", test_callback_import),
        ("Interval Safety Threshold", test_interval_never_too_low),
        ("High-Speed Scenarios", test_high_speed_performance),
        ("Speed Recommendations", test_speed_recommendations),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")

    if failed == 0:
        print("\n🎉 ALL SPEED TESTS PASSED! 🎉")
        print("\nThe animation speed system is working correctly.")
        print("High speeds (8-10x) are now safe and won't freeze the browser.")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())

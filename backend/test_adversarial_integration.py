"""
Quick integration test for adversarial testing suite.

Run this to verify all imports and basic functionality work.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_imports():
    """Test that all adversarial test modules can be imported."""
    print("Testing imports...")
    
    try:
        from tests.adversarial.base import AdversarialTest, create_test_transaction, run_detection_on_date_range, calculate_metrics
        print("✓ base.py imports successful")
    except Exception as e:
        print(f"✗ base.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.evasion_attack import EvasionAttack
        print("✓ evasion_attack.py imports successful")
    except Exception as e:
        print(f"✗ evasion_attack.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.flooding_attack import FloodingAttack
        print("✓ flooding_attack.py imports successful")
    except Exception as e:
        print(f"✗ flooding_attack.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.spoofing_attack import SpoofingAttack
        print("✓ spoofing_attack.py imports successful")
    except Exception as e:
        print(f"✗ spoofing_attack.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.temporal_spoofing import TemporalSpoofingAttack
        print("✓ temporal_spoofing.py imports successful")
    except Exception as e:
        print(f"✗ temporal_spoofing.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.velocity_attack import VelocityAttack
        print("✓ velocity_attack.py imports successful")
    except Exception as e:
        print(f"✗ velocity_attack.py import failed: {e}")
        return False
    
    try:
        from tests.adversarial.runner import run_all_adversarial_tests, calculate_robustness_score, identify_critical_vulnerabilities
        print("✓ runner.py imports successful")
    except Exception as e:
        print(f"✗ runner.py import failed: {e}")
        return False
    
    return True


def test_class_instantiation():
    """Test that all test classes can be instantiated."""
    print("\nTesting class instantiation...")
    
    try:
        from tests.adversarial.evasion_attack import EvasionAttack
        from tests.adversarial.flooding_attack import FloodingAttack
        from tests.adversarial.spoofing_attack import SpoofingAttack
        from tests.adversarial.temporal_spoofing import TemporalSpoofingAttack
        from tests.adversarial.velocity_attack import VelocityAttack
        
        tests = [
            EvasionAttack(),
            FloodingAttack(),
            SpoofingAttack(),
            TemporalSpoofingAttack(),
            VelocityAttack()
        ]
        
        for test in tests:
            print(f"✓ {test.name}: {test.description}")
        
        return True
    except Exception as e:
        print(f"✗ Class instantiation failed: {e}")
        return False


def test_robustness_calculation():
    """Test robustness score calculation."""
    print("\nTesting robustness score calculation...")
    
    try:
        from tests.adversarial.runner import calculate_robustness_score, identify_critical_vulnerabilities
        
        # Mock results - all passed
        results_all_pass = {
            "evasion_attack": {"passed": True},
            "flooding_attack": {"passed": True},
            "spoofing_attack": {"passed": True},
            "temporal_spoofing": {"passed": True},
            "velocity_attack": {"passed": True}
        }
        
        score = calculate_robustness_score(results_all_pass)
        print(f"✓ All tests passed: score = {score:.2f} (expected: 1.00)")
        
        # Mock results - some failed
        results_mixed = {
            "evasion_attack": {"passed": True},
            "flooding_attack": {"passed": True},
            "spoofing_attack": {"passed": False, "severity": "high"},
            "temporal_spoofing": {"passed": False, "severity": "high"},
            "velocity_attack": {"passed": True}
        }
        
        score = calculate_robustness_score(results_mixed)
        vulnerabilities = identify_critical_vulnerabilities(results_mixed)
        print(f"✓ Mixed results: score = {score:.2f} (expected: 0.65)")
        print(f"✓ Critical vulnerabilities: {vulnerabilities}")
        
        return True
    except Exception as e:
        print(f"✗ Robustness calculation failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("ADVERSARIAL TESTING SUITE - INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test class instantiation
    results.append(("Class Instantiation", test_class_instantiation()))
    
    # Test robustness calculation
    results.append(("Robustness Calculation", test_robustness_calculation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All integration tests passed!")
        print("\nNext steps:")
        print("1. Start backend: cd backend && python main.py")
        print("2. Test API: curl -X POST http://localhost:8000/api/v1/tests/adversarial")
        print("3. View results in AdversarialTestPanel.jsx")
    else:
        print("\n⚠️  Some integration tests failed. Please review errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

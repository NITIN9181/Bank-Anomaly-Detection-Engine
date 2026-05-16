"""
Adversarial Test Runner

Orchestrates execution of all adversarial tests and calculates overall robustness score.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from tests.adversarial.evasion_attack import EvasionAttack
from tests.adversarial.flooding_attack import FloodingAttack
from tests.adversarial.spoofing_attack import SpoofingAttack
from tests.adversarial.temporal_spoofing import TemporalSpoofingAttack
from tests.adversarial.velocity_attack import VelocityAttack

logger = logging.getLogger(__name__)


def run_all_adversarial_tests(db: Session) -> dict[str, Any]:
    """
    Run all adversarial tests in sequence.
    
    Each test is wrapped in try/except to prevent one failure from
    crashing the entire suite.
    
    Args:
        db: Database session
    
    Returns:
        Complete test results with summary and robustness score
    """
    logger.info("Starting adversarial test suite")
    
    # Initialize all tests
    tests = [
        EvasionAttack(),
        FloodingAttack(),
        SpoofingAttack(),
        TemporalSpoofingAttack(),
        VelocityAttack()
    ]
    
    # Run each test
    results = {}
    for test in tests:
        try:
            logger.info(f"Running test: {test.name}")
            result = test.run(db)
            results[test.name] = result
            logger.info(f"Test {test.name} completed: {'PASSED' if result['passed'] else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test.name} crashed: {e}")
            results[test.name] = {
                "test_name": test.name,
                "description": test.description,
                "passed": False,
                "error": str(e),
                "metrics": {},
                "details": [f"Test crashed with error: {e}"],
                "severity": "critical"
            }
    
    # Calculate summary
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r.get("passed", False))
    failed = total_tests - passed
    
    # Calculate robustness score
    robustness_score = calculate_robustness_score(results)
    
    # Identify critical vulnerabilities
    critical_vulnerabilities = identify_critical_vulnerabilities(results)
    
    logger.info(f"Adversarial test suite complete: {passed}/{total_tests} passed, score: {robustness_score:.2f}")
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system_version": "1.2.0",
        "tests": results,
        "summary": {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "overall_robustness_score": round(robustness_score, 3),
            "critical_vulnerabilities": critical_vulnerabilities
        }
    }


def calculate_robustness_score(results: dict[str, Any]) -> float:
    """
    Calculate weighted robustness score.
    
    Weights:
    - evasion_attack: 0.25 (most critical - gradual fraud)
    - flooding_attack: 0.25 (high volume scenarios)
    - spoofing_attack: 0.15 (name obfuscation)
    - temporal_spoofing: 0.20 (backdating attacks)
    - velocity_attack: 0.15 (burst spending)
    
    Args:
        results: Dictionary of test results
    
    Returns:
        Weighted robustness score (0.0-1.0)
    """
    weights = {
        "evasion_attack": 0.25,
        "flooding_attack": 0.25,
        "spoofing_attack": 0.15,
        "temporal_spoofing": 0.20,
        "velocity_attack": 0.15
    }
    
    score = 0.0
    for test_name, weight in weights.items():
        if test_name in results:
            passed = results[test_name].get("passed", False)
            score += weight if passed else 0.0
    
    return score


def identify_critical_vulnerabilities(results: dict[str, Any]) -> list[str]:
    """
    Identify failed tests with high severity.
    
    Args:
        results: Dictionary of test results
    
    Returns:
        List of test names that failed with severity="high" or "critical"
    """
    vulnerabilities = []
    
    for test_name, result in results.items():
        passed = result.get("passed", False)
        severity = result.get("severity", "low")
        
        if not passed and severity in ["high", "critical"]:
            vulnerabilities.append(test_name)
    
    return vulnerabilities

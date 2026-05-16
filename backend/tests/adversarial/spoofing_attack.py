"""
Spoofing Attack: "Merchant Name Obfuscation"

Uses variations of merchant names to evade pattern matching.
Tests if normalization pipeline handles common obfuscation techniques.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from database.models import VendorProfile
from features.engineer import update_vendor_profiles
from tests.adversarial.base import AdversarialTest, create_test_transaction


class SpoofingAttack(AdversarialTest):
    """
    Merchant Name Obfuscation attack.
    
    Simulates fraudster using slight variations of legitimate merchant names
    to evade pattern matching and vendor profiling.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "spoofing_attack"
        self.description = "Merchant name variations to evade normalization"
    
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute spoofing attack test.
        
        Args:
            db: Database session
        
        Returns:
            Test results with normalization metrics
        """
        # Step 1: Create baseline transactions to "Amazon"
        baseline_merchant = "Amazon"
        for i in range(10):
            create_test_transaction(
                account_id=None,
                merchant=baseline_merchant,
                amount=50.0 + (i * 10),
                date_offset_days=30 - i,
                db=db,
                category="Shopping"
            )
        
        # Step 2: Create variations
        variations = [
            "Amaz0n",      # Zero instead of O
            "AMAZON",      # All caps
            "amazon.com",  # Domain suffix
            "Amazon ",     # Trailing space
        ]
        
        for i, variant in enumerate(variations):
            create_test_transaction(
                account_id=None,
                merchant=variant,
                amount=75.0,
                date_offset_days=10 - i,
                db=db,
                category="Shopping"
            )
        
        db.commit()
        
        # Update vendor profiles (this should normalize names)
        update_vendor_profiles(db)
        
        # Step 3: Check if variations were normalized
        # Query vendor profiles
        profiles = db.query(VendorProfile).filter(
            VendorProfile.merchant_name.in_([baseline_merchant] + variations)
        ).all()
        
        # Count unique merchant names in profiles
        unique_merchants = {p.merchant_name for p in profiles}
        
        # Ideally, all should be normalized to "Amazon"
        # For now, we check if they're treated as separate merchants
        variations_correctly_normalized = 0
        
        # Check if baseline exists
        baseline_profile = db.query(VendorProfile).filter(
            VendorProfile.merchant_name == baseline_merchant
        ).first()
        
        if baseline_profile:
            # Check if baseline has accumulated transactions from variations
            # This is a proxy for normalization working
            if baseline_profile.transaction_count >= 10:
                # Baseline only
                variations_correctly_normalized = 0
            else:
                # Some normalization may have happened
                variations_correctly_normalized = 0
        
        # For this test, we check if variations created separate profiles
        # If they did, normalization failed
        variation_profiles = [
            p for p in profiles if p.merchant_name in variations
        ]
        
        # Calculate normalization rate
        # If variations created separate profiles, normalization failed
        normalization_rate = 0.0 if len(variation_profiles) > 0 else 1.0
        
        # Pass criteria: all variations should be normalized
        # For now, we expect this to FAIL (highlighting the vulnerability)
        passed = normalization_rate == 1.0
        
        return {
            "test_name": self.name,
            "description": self.description,
            "passed": passed,
            "metrics": {
                "variations_tested": len(variations),
                "variations_correctly_normalized": int(normalization_rate * len(variations)),
                "normalization_rate": round(normalization_rate, 3),
                "unique_merchant_profiles": len(unique_merchants),
                "expected_profiles": 1
            },
            "details": [
                f"Tested {len(variations)} merchant name variations",
                f"Unique profiles created: {len(unique_merchants)} (expected: 1)",
                f"Normalization rate: {normalization_rate:.1%} (target: 100%)",
                f"Variations: {', '.join(variations)}",
                "⚠️  Current system does NOT normalize merchant names",
                "Recommendation: Implement fuzzy matching or name normalization pipeline"
            ],
            "severity": "medium" if not passed else "low"
        }

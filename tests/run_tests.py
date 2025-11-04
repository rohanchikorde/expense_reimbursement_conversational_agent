#!/usr/bin/env python3
"""Automated testing script for the expense reimbursement system"""

import sys
import os
import json
import time
from PIL import Image

# Add the parent directory to the path so we can import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.workflow import expense_agent_system
from src.types.state import ExpenseState

def load_test_cases():
    """Load test cases from JSON file"""
    with open('tests/sample_data/inputs/test_cases.json', 'r') as f:
        return json.load(f)

def run_single_test(receipt_path, test_case):
    """Run a single test case"""
    print(f"\n=== Testing: {test_case['name']} ===")
    print(f"Description: {test_case['description']}")

    # Load receipt image
    if os.path.exists(receipt_path):
        image = Image.open(receipt_path)
        print(f"Loaded receipt: {receipt_path}")
    else:
        print(f"ERROR: Receipt not found: {receipt_path}")
        return False

    # Create initial state
    initial_state = ExpenseState(
        receipt_image=image,
        ocr_text=None,
        ocr_complete=False,
        amount=None,
        currency=None,
        expense_date=None,
        merchant=None,
        pickup_location=None,
        dropoff_location=None,
        country=None,
        city=None,
        country_identified=False,
        department=None,
        purpose=None,
        classification_confidence=None,
        department_confirmed=False,
        needs_clarification=False,
        clarification_questions=[],
        user_provided_context=None,
        rules_applied=False,
        applied_rule=None,
        requires_manager_approval=None,
        approval_status=None,
        policy_violation=False,
        violations=[],
        current_agent=None,
        messages=[],
        employee_id="test_user_123",
        approval_determined=False
    )

    try:
        # Run the workflow
        config = {"configurable": {"thread_id": f"test_{test_case['name']}_{int(time.time())}"}}
        result = expense_agent_system.invoke(initial_state, config)

        # Get final state
        final_state = expense_agent_system.get_state(config).values

        print("=== Results ===")
        print(f"OCR Complete: {final_state.get('ocr_complete', False)}")
        print(f"Amount: {final_state.get('amount', 'N/A')}")
        print(f"Merchant: {final_state.get('merchant', 'N/A')}")
        print(f"Department: {final_state.get('department', 'N/A')}")
        print(f"Purpose: {final_state.get('purpose', 'N/A')}")
        print(f"Approval Status: {final_state.get('approval_status', 'N/A')}")
        print(f"Needs Clarification: {final_state.get('needs_clarification', False)}")

        # Validate against expected results
        success = True
        if 'expected_department' in test_case:
            if final_state.get('department') != test_case['expected_department']:
                print(f"❌ Department mismatch: expected {test_case['expected_department']}, got {final_state.get('department')}")
                success = False
            else:
                print(f"✅ Department: {final_state.get('department')}")

        if 'expected_purpose' in test_case:
            if final_state.get('purpose') != test_case['expected_purpose']:
                print(f"❌ Purpose mismatch: expected {test_case['expected_purpose']}, got {final_state.get('purpose')}")
                success = False
            else:
                print(f"✅ Purpose: {final_state.get('purpose')}")

        if 'expected_approval' in test_case:
            if final_state.get('approval_status') != test_case['expected_approval']:
                print(f"❌ Approval mismatch: expected {test_case['expected_approval']}, got {final_state.get('approval_status')}")
                success = False
            else:
                print(f"✅ Approval: {final_state.get('approval_status')}")

        if test_case.get('needs_clarification', False):
            if not final_state.get('needs_clarification', False):
                print("❌ Expected clarification but none needed")
                success = False
            else:
                print("✅ Clarification triggered as expected")

        if success:
            print("🎉 TEST PASSED")
        else:
            print("❌ TEST FAILED")

        return success

    except Exception as e:
        print(f"ERROR during test execution: {e}")
        return False

def run_all_tests():
    """Run all test cases"""
    print("=== EXPENSE REIMBURSEMENT SYSTEM TEST SUITE ===")

    test_cases = load_test_cases()
    total_tests = len(test_cases['test_cases'])
    passed_tests = 0

    for test_case in test_cases['test_cases']:
        # Map test case to receipt file
        if 'uber' in test_case['name']:
            receipt_filename = 'uber_receipt_1.png'
        elif 'lyft' in test_case['name']:
            receipt_filename = 'lyft_receipt_1.png'
        elif 'taxi' in test_case['name']:
            receipt_filename = 'taxi_receipt_1.png'
        else:
            receipt_filename = f"{test_case['name'].replace('_', '_')}.png"

        receipt_path = f"tests/sample_data/receipts/{receipt_filename}"

        if run_single_test(receipt_path, test_case):
            passed_tests += 1

    print("\n=== TEST SUMMARY ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
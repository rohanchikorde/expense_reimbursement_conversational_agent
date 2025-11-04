from typing import TypedDict, Optional, Literal, List, Dict, Any
from PIL import Image

class ExpenseState(TypedDict):
    """State schema for the expense reimbursement workflow"""

    # Receipt data
    receipt_image: Optional[Image.Image]
    ocr_text: Optional[str]
    ocr_complete: bool

    # Extracted fields
    amount: Optional[float]
    currency: Optional[str]
    expense_date: Optional[str]
    merchant: Optional[str]
    pickup_location: Optional[str]
    dropoff_location: Optional[str]

    # Location analysis
    country: Optional[str]
    city: Optional[str]
    country_identified: bool

    # Classification
    department: Optional[str]
    purpose: Optional[str]
    classification_confidence: Optional[float]
    department_confirmed: bool

    # HITL
    needs_clarification: bool
    clarification_questions: List[str]
    user_provided_context: Optional[str]

    # Policy
    rules_applied: bool
    applied_rule: Optional[Dict]
    requires_manager_approval: Optional[bool]
    approval_status: Optional[Literal["pending", "auto_approved", "requires_manager"]]

    # Exceptions
    policy_violation: bool
    violations: List[Dict]

    # Workflow control
    current_agent: Optional[str]
    messages: List[Dict]
    employee_id: Optional[str]
    approval_determined: bool
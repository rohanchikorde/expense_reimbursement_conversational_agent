# 📚 API Documentation

<div align="center">

![API](https://img.shields.io/badge/API-Documented-green.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Stable-orange.svg)

**Complete API reference for the Expense Reimbursement Conversational Agent**

</div>

---

## 📋 API Overview

The Expense Reimbursement Conversational Agent provides a programmatic interface for expense processing through its core components. This documentation covers all public APIs, data structures, and integration points.

### 🔧 Core Components

- **Workflow API**: Main orchestration interface
- **Agent APIs**: Individual agent functions
- **State Management**: Data structures and schemas
- **Configuration**: Settings and environment variables

---

## 🔄 Workflow API

### `expense_agent_system`

**Main workflow orchestrator for expense processing**

#### Methods

##### `invoke(initial_state, config)`

Execute the expense processing workflow

**Parameters:**
- `initial_state` (ExpenseState): Initial expense data
- `config` (dict): Configuration with thread_id

**Returns:**
- Workflow execution result

**Example:**
```python
from src.workflow import expense_agent_system
from src.types.state import ExpenseState

# Create initial state
state = ExpenseState(
    receipt_image=image,
    messages=[HumanMessage(content="Process this receipt")]
)

# Execute workflow
config = {"configurable": {"thread_id": "session_123"}}
result = expense_agent_system.invoke(state, config)
```

##### `get_state(config)`

Retrieve current workflow state

**Parameters:**
- `config` (dict): Configuration with thread_id

**Returns:**
- Current state snapshot

**Example:**
```python
state = expense_agent_system.get_state(config)
current_messages = state.values.get("messages", [])
```

---

## 🤖 Agent APIs

### Supervisor Agent

#### `supervisor_agent(state)`

**Central workflow coordinator**

**Parameters:**
- `state` (ExpenseState): Current workflow state

**Returns:**
- `Command`: Next agent routing decision

**Decision Logic:**
```python
# Routes based on completion status
if not state.get("ocr_complete"):
    return Command(goto="receipt_processor")
elif not state.get("country_identified"):
    return Command(goto="location_analyst")
# ... additional routing rules
```

### Receipt Processor Agent

#### `receipt_processor_agent_node(state)`

**OCR processing and data extraction**

**Parameters:**
- `state` (ExpenseState): Must contain `receipt_image`

**Returns:**
- `Command`: Routes to supervisor

**Processing Steps:**
1. Extract text using Tesseract OCR
2. Parse structured data with LLM
3. Update state with extracted fields
4. Remove image to prevent serialization issues

**State Updates:**
```python
state.update({
    "ocr_text": extracted_text,
    "ocr_complete": True,
    "amount": parsed_amount,
    "currency": parsed_currency,
    "expense_date": parsed_date,
    "merchant": parsed_merchant,
    "pickup_location": parsed_pickup,
    "dropoff_location": parsed_dropoff
})
```

### Location Analyst Agent

#### `location_analyst_agent_node(state)`

**Geographic context analysis**

**Parameters:**
- `state` (ExpenseState): Must contain location data

**Returns:**
- `Command`: Routes to supervisor

**Analysis Process:**
```python
locations = f"{state.get('pickup_location', '')} {state.get('dropoff_location', '')}"
prompt = f"Identify the country from these locations: {locations}"
response = llm.invoke([HumanMessage(content=prompt)])
country = response.content.strip()
```

**State Updates:**
```python
state.update({
    "country": country,
    "country_identified": True
})
```

### Classification Agent

#### `classification_agent_node(state)`

**Expense categorization and confidence scoring**

**Parameters:**
- `state` (ExpenseState): Must contain extracted data

**Returns:**
- `Command`: Routes to supervisor or HITL

**Classification Process:**
```python
prompt = f"""
Analyze this expense:
Dropoff: {state.get('dropoff_location', '')}
Date: {state.get('expense_date', '')}
Amount: {state.get('amount', '')}

Infer department and purpose. Confidence 0-100.
"""

response = llm.invoke([HumanMessage(content=prompt)])
parsed = extract_json_from_llm_response(response.content)
```

**Decision Logic:**
```python
if parsed["confidence"] < CLASSIFICATION_CONFIDENCE_THRESHOLD:
    state["needs_clarification"] = True
    return Command(goto="hitl", update=state)
else:
    state.update({
        "department": parsed["department"],
        "purpose": parsed["purpose"],
        "classification_confidence": parsed["confidence"],
        "department_confirmed": True
    })
    return Command(goto="supervisor", update=state)
```

### HITL Agent

#### `hitl_agent_node(state)`

**Human-in-the-loop clarification handling**

**Parameters:**
- `state` (ExpenseState): Must have `clarification_questions`

**Returns:**
- `Command`: Interrupt for user input

**Interrupt Creation:**
```python
clarification_questions = state.get("clarification_questions", [])
interrupt_message = f"""
I need clarification for this expense:
{chr(10).join(f"- {q}" for q in clarification_questions)}
"""
return Command(interrupt=interrupt_message, update=state)
```

### Policy Engine Agent

#### `policy_engine_agent_node(state)`

**Business rule application and approval logic**

**Parameters:**
- `state` (ExpenseState): Must contain amount and date

**Returns:**
- `Command`: Routes to supervisor

**Rule Application:**
```python
amount = state.get("amount", 0)
expense_date = state.get("expense_date", "")

# Determine threshold based on date
if expense_date < "2024-01-01":
    threshold = 50.00
else:
    threshold = 75.00

# Apply approval logic
if amount <= threshold:
    state.update({
        "requires_manager_approval": False,
        "applied_rule": f"Auto-approved: amount ≤ ${threshold}"
    })
else:
    state.update({
        "requires_manager_approval": True,
        "applied_rule": f"Requires approval: amount > ${threshold}"
    })

state["rules_applied"] = True
```

### Approval Router Agent

#### `approval_router_agent_node(state)`

**Final approval decision making**

**Parameters:**
- `state` (ExpenseState): Must have rule evaluation results

**Returns:**
- `Command`: Routes to supervisor

**Decision Logic:**
```python
if state.get("policy_violation", False):
    approval_status = "rejected"
elif state.get("requires_manager_approval", False):
    approval_status = "requires_approval"
else:
    approval_status = "auto_approved"

state.update({
    "approval_status": approval_status,
    "approval_determined": True
})
```

### Finalize Agent

#### `finalize_agent_node(state)`

**Workflow completion and finalization**

**Parameters:**
- `state` (ExpenseState): Complete workflow state

**Returns:**
- `Command`: Final state update (workflow ends)

**Completion Tasks:**
```python
# Log completion
print("=== WORKFLOW COMPLETED ===")

# Add completion message
state["messages"].append(AIMessage(content="Expense processing completed."))

return Command(update=state)
```

---

## 📊 Data Structures

### ExpenseState

**Complete state schema for expense processing**

```python
class ExpenseState(TypedDict):
    # Receipt Processing
    receipt_image: Optional[Image.Image]        # PIL Image object
    ocr_text: str                               # Raw OCR text
    ocr_complete: bool                          # OCR processing status

    # Extracted Data
    amount: Optional[float]                     # Expense amount
    currency: Optional[str]                     # Currency code (USD, EUR, etc.)
    expense_date: Optional[str]                 # YYYY-MM-DD format
    merchant: Optional[str]                     # Merchant name
    pickup_location: Optional[str]              # Pickup location
    dropoff_location: Optional[str]             # Drop-off location

    # Geographic Context
    country: Optional[str]                      # Identified country
    city: Optional[str]                         # Identified city
    country_identified: bool                    # Country identification status

    # Classification
    department: Optional[str]                   # Department (Sales, HR, etc.)
    purpose: Optional[str]                      # Purpose (Meeting, Training, etc.)
    classification_confidence: Optional[int]    # Confidence score 0-100
    department_confirmed: bool                  # Classification confirmation status

    # Human Clarification
    needs_clarification: bool                   # Clarification required flag
    clarification_questions: List[str]          # Questions for user
    user_provided_context: Optional[str]        # User-provided context

    # Business Rules
    rules_applied: bool                         # Rule application status
    applied_rule: Optional[str]                 # Applied rule description
    requires_manager_approval: Optional[bool]   # Approval requirement
    approval_status: Optional[str]              # Final status
    policy_violation: bool                      # Violation flag
    violations: List[str]                       # Violation details

    # Workflow Control
    current_agent: Optional[str]                # Currently executing agent
    messages: List[Union[HumanMessage, AIMessage]]  # Conversation history
    employee_id: str                            # Employee identifier
    approval_determined: bool                   # Final approval status
```

### Command

**Workflow routing and state update structure**

```python
class Command:
    def __init__(
        self,
        goto: Optional[str] = None,              # Next agent to execute
        update: Optional[Dict] = None,           # State updates
        interrupt: Optional[str] = None          # Human interrupt message
    ):
        pass
```

### Message Types

**Conversation message structures**

```python
# Human message
human_msg = HumanMessage(content="Process this receipt")

# AI assistant message
ai_msg = AIMessage(content="Extracted amount: $45.67")
```

---

## ⚙️ Configuration API

### Settings Module (`src/config/settings.py`)

**Configuration constants and environment variables**

```python
# LLM Configuration
LLM_MODEL: str = "anthropic/claude-3-haiku"
LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
LLM_DEFAULT_HEADERS: Dict[str, str] = {"HTTP-Referer": "..."}
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# Processing Thresholds
CLASSIFICATION_CONFIDENCE_THRESHOLD: int = 70
OCR_CONFIDENCE_THRESHOLD: int = 80

# Business Rules
AUTO_APPROVAL_THRESHOLD_PRE_2024: float = 50.00
AUTO_APPROVAL_THRESHOLD_POST_2024: float = 75.00

# Workflow Settings
MAX_RETRIES: int = 3
TIMEOUT_SECONDS: int = 30
```

### Environment Variables

**Required environment configuration**

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Override defaults
LLM_MODEL=anthropic/claude-3-sonnet
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## 🔧 Utility Functions

### Helper Functions (`src/utils/helpers.py`)

#### `extract_json_from_llm_response(response_content)`

**Extract JSON data from LLM response**

**Parameters:**
- `response_content` (str): Raw LLM response

**Returns:**
- `Dict`: Parsed JSON data

**Example:**
```python
response = llm.invoke([HumanMessage(content=prompt)])
data = extract_json_from_llm_response(response.content)
# Returns: {"amount": 45.67, "currency": "USD", ...}
```

#### `validate_expense_data(state)`

**Validate expense data completeness**

**Parameters:**
- `state` (ExpenseState): Current state

**Returns:**
- `bool`: Validation result

**Validation Checks:**
- Amount is numeric and positive
- Date is valid YYYY-MM-DD format
- Required fields are present
- Currency is valid code

#### `calculate_approval_threshold(expense_date)`

**Determine approval threshold based on date**

**Parameters:**
- `expense_date` (str): Expense date in YYYY-MM-DD format

**Returns:**
- `float`: Approval threshold amount

**Logic:**
```python
if expense_date < "2024-01-01":
    return 50.00
else:
    return 75.00
```

---

## 🚨 Error Handling

### Exception Types

```python
class ProcessingError(Exception):
    """Base exception for processing errors"""
    pass

class OCRError(ProcessingError):
    """OCR processing failures"""
    pass

class LLMError(ProcessingError):
    """LLM API failures"""
    pass

class ValidationError(ProcessingError):
    """Data validation failures"""
    pass
```

### Error Handling Patterns

```python
# OCR with fallback
try:
    text = pytesseract.image_to_string(image)
except TesseractNotFoundError:
    print("Tesseract not available, using fallback")
    text = get_mock_ocr_data()

# LLM with retry
for attempt in range(MAX_RETRIES):
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        break
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise LLMError(f"LLM failed after {MAX_RETRIES} attempts") from e
        time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 📈 Performance Metrics

### API Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| OCR Processing | <5s | ~2s |
| LLM Inference | <10s | ~3s |
| State Serialization | <1s | ~0.5s |
| Total Processing | <30s | ~15s |

### Monitoring Endpoints

```python
# Get workflow metrics
metrics = expense_agent_system.get_metrics()

# Log performance data
logger.info("Workflow completed", extra={
    "duration": end_time - start_time,
    "agent_count": len(executed_agents),
    "interrupt_count": interrupt_count
})
```

---

## 🔌 Integration Examples

### Basic Integration

```python
from PIL import Image
from src.workflow import expense_agent_system
from src.types.state import ExpenseState

def process_expense_receipt(image_path: str) -> Dict:
    """Process a single expense receipt"""

    # Load image
    image = Image.open(image_path)

    # Create initial state
    state = ExpenseState(
        receipt_image=image,
        messages=[],
        employee_id="user_123"
    )

    # Execute workflow
    config = {"configurable": {"thread_id": f"process_{int(time.time())}"}}
    result = expense_agent_system.invoke(state, config)

    # Return final state
    return expense_agent_system.get_state(config).values
```

### Batch Processing

```python
def process_batch_receipts(image_paths: List[str]) -> List[Dict]:
    """Process multiple receipts"""

    results = []
    for i, image_path in enumerate(image_paths):
        try:
            result = process_expense_receipt(image_path)
            results.append({
                "file": image_path,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "file": image_path,
                "status": "error",
                "error": str(e)
            })

    return results
```

### Real-time Processing

```python
def process_realtime_updates(thread_id: str):
    """Monitor workflow progress in real-time"""

    while True:
        state = expense_agent_system.get_state({"configurable": {"thread_id": thread_id}})

        if state.next:  # Still running
            current_agent = state.values.get("current_agent", "unknown")
            print(f"Processing: {current_agent}")
            time.sleep(1)
        else:  # Completed
            print("Workflow completed!")
            break
```

---

<div align="center">

**📚 Complete API reference for seamless integration**

[⬆️ Back to Top](#-api-documentation) • [🏗️ Architecture](architecture.md) • [🏠 Home](../README.md)

</div>
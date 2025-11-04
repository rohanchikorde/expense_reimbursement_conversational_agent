# 🏗️ System Architecture

<div align="center">

![Architecture](https://img.shields.io/badge/Architecture-Modular-blue.svg)
![Design](https://img.shields.io/badge/Design-Agent--Based-green.svg)
![Flow](https://img.shields.io/badge/Flow-State--Driven-orange.svg)

**Detailed technical architecture of the Expense Reimbursement Conversational Agent**

</div>

---

## 📋 Architecture Overview

The Expense Reimbursement Conversational Agent follows a **modular, agent-based architecture** built on LangGraph, designed for scalability, maintainability, and extensibility.

### 🏛️ Core Principles

- **🔄 Event-Driven**: State transitions trigger agent actions
- **🤖 Agent-Based**: Specialized AI agents for specific tasks
- **📊 State Management**: Centralized state with immutable updates
- **🔀 Workflow Orchestration**: Declarative workflow definitions
- **🧪 Testability**: Modular design enables comprehensive testing

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🎨 Streamlit UI                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 💬 Chat Interface                   │    │
│  │  ┌─────────────┬─────────────┬─────────────────┐   │    │
│  │  │ File Upload │ Text Input  │ Message Display │   │    │
│  │  └─────────────┴─────────────┴─────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 🔄 LangGraph Workflow                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              📊 State Management                    │    │
│  │  ┌─────────────┬─────────────┬─────────────────┐   │    │
│  │  │   State     │  Config     │   Checkpoints   │   │    │
│  │  └─────────────┴─────────────┴─────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 🤖 AI Agent System                           │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐          │
│  │  📋 │  🌍 │  🏷️ │  👥 │  ⚖️ │  🚫 │  ✅ │  🎯 │          │
│  │Supervisor│Location│Classification│ HITL │Policy│Exception│Approval│Finalize│
│  │         │Analyst│             │     │Engine│Handler │Router  │        │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Component Analysis

### 🎨 User Interface Layer

#### Streamlit Application (`app.py`)

**Responsibilities:**
- File upload handling for receipt images
- Conversational chat interface
- Real-time status updates and progress indicators
- Interrupt handling for human clarification
- Session state management

**Key Features:**
```python
# Session management
st.session_state.thread_id
st.session_state.workflow_started
st.session_state.last_interrupt

# UI components
st.file_uploader("Upload receipt")
st.chat_message("assistant")
st.chat_input("Your response")
```

### 🔄 Workflow Orchestration Layer

#### LangGraph Workflow (`src/workflow.py`)

**Core Components:**
- **StateGraph**: Defines the workflow structure
- **MemorySaver**: Provides checkpointing for HITL
- **Interrupt Handling**: Pauses for human input
- **Agent Routing**: Deterministic next-agent selection

**Workflow Definition:**
```python
workflow = StateGraph(ExpenseState)

# Add nodes (agents)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("receipt_processor", receipt_processor_agent_node)
# ... other agents

# Define edges
workflow.add_edge(START, "supervisor")
workflow.add_edge("receipt_processor", "supervisor")
# ... other connections

# Compile with checkpointer
app = workflow.compile(checkpointer=MemorySaver())
```

### 🤖 Agent Layer

#### Supervisor Agent (`src/agents/supervisor.py`)

**Decision Logic:**
```python
def supervisor_agent(state: ExpenseState) -> Command:
    if not state.get("ocr_complete", False):
        return Command(goto="receipt_processor", update=state)
    elif not state.get("country_identified", False):
        return Command(goto="location_analyst", update=state)
    # ... additional routing logic
```

**Routing Table:**

| Condition | Next Agent | Purpose |
|-----------|------------|---------|
| `not ocr_complete` | `receipt_processor` | Extract text from receipt |
| `not country_identified` | `location_analyst` | Determine geographic context |
| `not department_confirmed` | `classification` | Classify expense type |
| `needs_clarification` | `hitl` | Human clarification needed |
| `not rules_applied` | `policy_engine` | Apply business rules |
| `policy_violation` | `exception_handler` | Handle violations |
| `not approval_determined` | `approval_router` | Final approval decision |
| All complete | `finalize` | Complete workflow |

#### Receipt Processor Agent (`src/agents/receipt_processor.py`)

**OCR Pipeline:**
```python
def receipt_processor_agent_node(state: ExpenseState) -> Command:
    # 1. Extract text using Tesseract
    text = pytesseract.image_to_string(state["receipt_image"])

    # 2. Parse with LLM
    response = llm.invoke([HumanMessage(content=prompt)])
    info = extract_json_from_llm_response(response.content)

    # 3. Update state
    state.update(info)
    state["ocr_complete"] = True

    return Command(goto="supervisor", update=state)
```

#### Location Analyst Agent (`src/agents/location_analyst.py`)

**Geographic Analysis:**
```python
def location_analyst_agent_node(state: ExpenseState) -> Command:
    locations = f"{state.get('pickup_location', '')} {state.get('dropoff_location', '')}"
    prompt = f"Identify the country from these locations: {locations}"

    response = llm.invoke([HumanMessage(content=prompt)])
    country = response.content.strip()

    state["country"] = country
    state["country_identified"] = True

    return Command(goto="supervisor", update=state)
```

#### Classification Agent (`src/agents/classification.py`)

**Expense Classification:**
```python
def classification_agent_node(state: ExpenseState) -> Command:
    prompt = f"""
    Analyze this expense:
    Dropoff: {state.get('dropoff_location', '')}
    Date: {state.get('expense_date', '')}
    Amount: {state.get('amount', '')}

    Infer department and purpose. Confidence 0-100.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = extract_json_from_llm_response(response.content)

    if parsed["confidence"] < CLASSIFICATION_CONFIDENCE_THRESHOLD:
        state["needs_clarification"] = True
        return Command(goto="hitl", update=state)
    else:
        state["department_confirmed"] = True
        return Command(goto="supervisor", update=state)
```

#### HITL Agent (`src/agents/hitl.py`)

**Human-in-the-Loop:**
```python
def hitl_agent_node(state: ExpenseState) -> Command:
    clarification_questions = state.get("clarification_questions", [])

    # Create interrupt for user input
    interrupt_message = f"""
    I need clarification for this expense:
    {chr(10).join(f"- {q}" for q in clarification_questions)}
    """

    # This will pause execution and wait for user input
    return Command(interrupt=interrupt_message, update=state)
```

#### Policy Engine Agent (`src/agents/policy_engine.py`)

**Business Rules Application:**
```python
def policy_engine_agent_node(state: ExpenseState) -> Command:
    amount = state.get("amount", 0)
    expense_date = state.get("expense_date", "")

    # Apply approval rules
    if expense_date < "2024-01-01":
        threshold = 50.00
    else:
        threshold = 75.00

    if amount <= threshold:
        state["requires_manager_approval"] = False
        state["applied_rule"] = f"Auto-approved: amount ≤ ${threshold}"
    else:
        state["requires_manager_approval"] = True
        state["applied_rule"] = f"Requires approval: amount > ${threshold}"

    state["rules_applied"] = True
    return Command(goto="supervisor", update=state)
```

#### Approval Router Agent (`src/agents/approval_router.py`)

**Final Approval Decision:**
```python
def approval_router_agent_node(state: ExpenseState) -> Command:
    if state.get("policy_violation", False):
        state["approval_status"] = "rejected"
    elif state.get("requires_manager_approval", False):
        state["approval_status"] = "requires_approval"
    else:
        state["approval_status"] = "auto_approved"

    state["approval_determined"] = True
    return Command(goto="supervisor", update=state)
```

#### Finalize Agent (`src/agents/finalize.py`)

**Workflow Completion:**
```python
def finalize_agent_node(state: ExpenseState) -> Command:
    # Log completion
    print("=== WORKFLOW COMPLETED ===")

    # Add completion message
    state["messages"].append(AIMessage(content="Expense processing completed."))

    # Return final state (workflow ends)
    return Command(update=state)
```

---

## 📊 State Management

### ExpenseState Schema (`src/types/state.py`)

```python
class ExpenseState(TypedDict):
    # Receipt processing
    receipt_image: Optional[Image.Image]
    ocr_text: str
    ocr_complete: bool

    # Extracted data
    amount: Optional[float]
    currency: Optional[str]
    expense_date: Optional[str]
    merchant: Optional[str]
    pickup_location: Optional[str]
    dropoff_location: Optional[str]

    # Geographic context
    country: Optional[str]
    city: Optional[str]
    country_identified: bool

    # Classification
    department: Optional[str]
    purpose: Optional[str]
    classification_confidence: Optional[int]
    department_confirmed: bool

    # Human clarification
    needs_clarification: bool
    clarification_questions: List[str]
    user_provided_context: Optional[str]

    # Business rules
    rules_applied: bool
    applied_rule: Optional[str]
    requires_manager_approval: Optional[bool]
    approval_status: Optional[str]
    policy_violation: bool
    violations: List[str]

    # Workflow control
    current_agent: Optional[str]
    messages: List[Union[HumanMessage, AIMessage]]
    employee_id: str
    approval_determined: bool
```

### State Transitions

```
Initial State
    ↓ (receipt upload)
OCR Processing → Data Extraction
    ↓
Geographic Analysis → Country Identification
    ↓
Expense Classification → Department/Purpose
    ↓ (if unclear)
Human Clarification ←→ Re-classification
    ↓
Policy Application → Rule Evaluation
    ↓ (if violation)
Exception Handling → Violation Resolution
    ↓
Approval Routing → Final Decision
    ↓
Workflow Finalization → Completion
```

---

## 🔄 Data Flow

### Receipt Processing Pipeline

```
Receipt Image
    ↓
Tesseract OCR → Raw Text
    ↓
LLM Extraction → Structured Data
    ↓
State Update → Next Agent
```

### Classification Pipeline

```
Structured Data
    ↓
LLM Analysis → Department & Purpose
    ↓
Confidence Check → High/Low Confidence
    ↓
Auto-Classification ←→ Human Clarification
    ↓
Confirmed Classification
```

### Approval Pipeline

```
Classification + Amount + Date
    ↓
Rule Evaluation → Approval Threshold
    ↓
Auto-Approval ←→ Manager Review
    ↓
Final Status
```

---

## 🛡️ Error Handling & Resilience

### Exception Handling Strategy

1. **OCR Failures**: Fallback to mock data with user notification
2. **LLM Errors**: Retry with exponential backoff
3. **State Corruption**: Checkpoint restoration
4. **Network Issues**: Graceful degradation with cached responses

### Logging & Monitoring

```python
# Structured logging throughout agents
logger.info("OCR processing started", extra={
    "agent": "receipt_processor",
    "image_size": image.size,
    "timestamp": datetime.now()
})
```

---

## 🔧 Configuration Management

### Settings Hierarchy (`src/config/settings.py`)

```python
# API Configuration
LLM_MODEL = "anthropic/claude-3-haiku"
LLM_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Processing Thresholds
CLASSIFICATION_CONFIDENCE_THRESHOLD = 70
OCR_CONFIDENCE_THRESHOLD = 80

# Business Rules
AUTO_APPROVAL_THRESHOLD_PRE_2024 = 50.00
AUTO_APPROVAL_THRESHOLD_POST_2024 = 75.00
```

### Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=your_api_key
DEBUG=true  # Enable debug logging
LOG_LEVEL=INFO
```

---

## 🚀 Performance Considerations

### Optimization Strategies

- **Lazy Loading**: Load agents only when needed
- **Caching**: Cache LLM responses for repeated queries
- **Async Processing**: Non-blocking I/O operations
- **Memory Management**: Clean up large objects (images)

### Performance Metrics

| Component | Target | Current |
|-----------|--------|---------|
| OCR Processing | <5s | ~2s |
| LLM Inference | <10s | ~3s |
| Total Processing | <30s | ~15s |
| Memory Usage | <500MB | ~200MB |

---

## 🔮 Extensibility

### Adding New Agents

1. **Create Agent Module**
   ```python
   # src/agents/new_agent.py
   def new_agent_node(state: ExpenseState) -> Command:
       # Agent logic here
       return Command(goto="supervisor", update=state)
   ```

2. **Register in Workflow**
   ```python
   # src/workflow.py
   workflow.add_node("new_agent", new_agent_node)
   workflow.add_edge("new_agent", "supervisor")
   ```

3. **Update Supervisor Logic**
   ```python
   # src/agents/supervisor.py
   elif condition_for_new_agent:
       next_agent = "new_agent"
   ```

### Customizing Business Rules

```python
# src/agents/policy_engine.py
def apply_custom_rules(state: ExpenseState) -> None:
    # Custom business logic
    if custom_condition:
        state["custom_flag"] = True
```

---

## 🧪 Testing Architecture

### Test Structure

```
tests/
├── unit/              # Unit tests for individual agents
├── integration/       # Integration tests for workflows
├── e2e/              # End-to-end user journey tests
└── fixtures/         # Test data and mock objects
```

### Test Categories

- **Unit Tests**: Individual agent functions
- **Integration Tests**: Agent-to-agent communication
- **Workflow Tests**: Complete state transitions
- **UI Tests**: Streamlit interface interactions

---

<div align="center">

**🏗️ Built for scalability, maintainability, and extensibility**

[⬆️ Back to Top](#️-system-architecture) • [🏠 Home](../README.md) • [📚 API Docs](api.md)

</div>
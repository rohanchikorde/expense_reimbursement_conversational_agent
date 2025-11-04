# 🔧 Troubleshooting Guide

<div align="center">

![Issues](https://img.shields.io/badge/Issues-Resolved-green.svg)
![Support](https://img.shields.io/badge/Support-Community-blue.svg)
![Debug](https://img.shields.io/badge/Debug-Enabled-orange.svg)

**Comprehensive troubleshooting guide for the Expense Reimbursement Conversational Agent**

</div>

---

## 📋 Quick Issue Resolution

### 🚀 Getting Started Issues

#### **Streamlit won't start**
```bash
# Check Python installation
python --version

# Verify virtual environment
.\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Check Streamlit installation
pip list | grep streamlit

# Start with verbose logging
streamlit run app.py --logger.level=debug
```

#### **Tesseract OCR not found**
```bash
# Check installation
tesseract --version

# Verify PATH
echo $PATH | grep -i tesseract

# Manual path configuration (in receipt_processor.py)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### **OpenRouter API errors**
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

---

## 🐛 Common Issues & Solutions

### 🔄 Workflow Issues

#### **Workflow stuck at supervisor**
**Symptoms:** Agent routing loops or doesn't progress

**Debug Steps:**
```python
# Check state values
state = expense_agent_system.get_state(config)
print("Current state:", state.values)

# Verify completion flags
print("OCR Complete:", state.values.get("ocr_complete"))
print("Country Identified:", state.values.get("country_identified"))
```

**Common Causes:**
- Missing state updates in agents
- Incorrect routing logic in supervisor
- State corruption during serialization

**Solutions:**
```python
# Reset workflow state
expense_agent_system.update_state(config, {
    "ocr_complete": False,
    "country_identified": False,
    "department_confirmed": False
})
```

#### **HITL interrupts not working**
**Symptoms:** Workflow doesn't pause for user input

**Debug Steps:**
```python
# Check interrupt configuration
print("Interrupts configured:", expense_agent_system.interrupt_before)

# Verify HITL conditions
needs_clarification = state.values.get("needs_clarification", False)
print("Needs clarification:", needs_clarification)
```

**Solutions:**
- Ensure `interrupt_before=["hitl"]` in workflow compilation
- Check that `needs_clarification` flag is set correctly
- Verify HITL agent returns proper interrupt command

### 📸 OCR Processing Issues

#### **Tesseract returns empty text**
**Symptoms:** OCR completes but returns empty or gibberish text

**Debug Steps:**
```python
# Test Tesseract directly
from PIL import Image
import pytesseract

img = Image.open("test_receipt.png")
text = pytesseract.image_to_string(img)
print("Raw OCR output:", repr(text))
```

**Common Causes:**
- Poor image quality
- Incorrect image format
- Tesseract language not configured

**Solutions:**
```python
# Preprocess image
img = img.convert('L')  # Convert to grayscale
img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize

# Use specific language
text = pytesseract.image_to_string(img, lang='eng')

# Configure PSM mode
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(img, config=custom_config)
```

#### **PIL Image serialization error**
**Symptoms:** `Type is not msgpack serializable: PngImageFile`

**Solution:**
```python
# In receipt_processor.py, after OCR:
del state["receipt_image"]  # Remove image completely
# Don't use state["receipt_image"] = None
```

### 🤖 LLM Processing Issues

#### **LLM responses are malformed**
**Symptoms:** JSON parsing fails on LLM output

**Debug Steps:**
```python
# Check raw LLM response
response = llm.invoke([HumanMessage(content=prompt)])
print("Raw response:", response.content)

# Test JSON extraction
try:
    data = extract_json_from_llm_response(response.content)
    print("Parsed data:", data)
except Exception as e:
    print("Parsing error:", e)
```

**Solutions:**
- Improve prompt formatting with clear JSON structure
- Add response validation before parsing
- Use more specific LLM instructions

#### **LLM API rate limits**
**Symptoms:** `429 Too Many Requests` errors

**Solutions:**
```python
import time

def call_llm_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return response
        except Exception as e:
            if "429" in str(e):
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### 💬 UI/UX Issues

#### **Chat messages not displaying**
**Symptoms:** Messages sent but not shown in UI

**Debug Steps:**
```python
# Check session state
print("Thread ID:", st.session_state.thread_id)
print("Workflow started:", st.session_state.workflow_started)

# Verify state retrieval
config = {"configurable": {"thread_id": st.session_state.thread_id}}
state = expense_agent_system.get_state(config)
print("Messages in state:", len(state.values.get("messages", [])))
```

**Solutions:**
- Ensure thread_id consistency
- Check state persistence
- Verify message format (HumanMessage/AIMessage)

#### **File upload not triggering workflow**
**Symptoms:** File uploaded but no processing starts

**Debug Steps:**
```python
# Check upload handling
if uploaded_file:
    print("File uploaded:", uploaded_file.name)
    print("File size:", uploaded_file.size)
    print("Workflow started:", st.session_state.workflow_started)
```

**Solutions:**
- Verify file type validation
- Check image loading with PIL
- Ensure workflow initialization succeeds

---

## 🔍 Advanced Debugging

### Enable Debug Logging

```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# In agents
logger = logging.getLogger(__name__)
logger.debug("Processing started", extra={"agent": "receipt_processor"})
```

### State Inspection

```python
# Complete state dump
config = {"configurable": {"thread_id": st.session_state.thread_id}}
state = expense_agent_system.get_state(config)

print("=== STATE INSPECTION ===")
print("Values:", state.values)
print("Next:", state.next)
print("Tasks:", [task.name for task in state.tasks])
print("Interrupts:", state.interrupts)
```

### Workflow Tracing

```python
# Add tracing to workflow
from langgraph.callbacks import LangChainTracer

tracer = LangChainTracer()
result = expense_agent_system.invoke(
    state,
    config,
    callbacks=[tracer]
)
```

### Memory Profiling

```python
# Check memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

---

## 🚨 Critical Error Recovery

### Workflow Corruption

**Symptoms:** Workflow stuck in invalid state

**Recovery:**
```python
# Force reset
config = {"configurable": {"thread_id": "new_thread_id"}}
expense_agent_system.update_state(config, initial_state)

# Clear session
st.session_state.workflow_started = False
st.session_state.thread_id = "reset_thread"
```

### Database/Checkpoint Issues

**Symptoms:** State not persisting between runs

**Recovery:**
```python
# Clear checkpoints
expense_agent_system.checkpointer = None

# Reinitialize workflow
from src.workflow import build_expense_workflow
expense_agent_system = build_expense_workflow()
```

### API Key Issues

**Symptoms:** Authentication failures

**Recovery:**
```bash
# Verify key format
echo $OPENROUTER_API_KEY | head -c 10

# Test API access
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/auth/key
```

---

## 📊 Performance Issues

### Slow OCR Processing

**Optimization:**
```python
# Use faster PSM mode
custom_config = r'--oem 1 --psm 8'
text = pytesseract.image_to_string(img, config=custom_config)

# Resize large images
if img.size[0] > 2000:
    img = img.resize((2000, int(2000 * img.size[1] / img.size[0])))
```

### High Memory Usage

**Optimization:**
```python
# Process images in chunks
def process_large_image(img):
    # Split large images
    chunks = split_image(img)
    texts = [pytesseract.image_to_string(chunk) for chunk in chunks]
    return ' '.join(texts)

# Clean up after processing
del state["receipt_image"]
import gc
gc.collect()
```

### LLM Latency

**Optimization:**
```python
# Use streaming responses
response = llm.stream([HumanMessage(content=prompt)])
full_response = ""
for chunk in response:
    full_response += chunk.content
    print(".", end="", flush=True)  # Progress indicator
```

---

## 🧪 Testing & Validation

### Run Test Suite

```bash
# Execute all tests
python tests/run_tests.py

# Run specific test
python -m pytest tests/ -k "test_uber_business_trip"

# Generate coverage report
python -m pytest --cov=src tests/ --cov-report=html
```

### Manual Validation

```python
# Test individual components
from src.agents.receipt_processor import receipt_processor_agent_node

test_state = ExpenseState(receipt_image=test_image)
result = receipt_processor_agent_node(test_state)
print("Agent result:", result)
```

---

## 📞 Getting Help

### Community Support

- **GitHub Issues**: [Create an issue](../../issues)
- **Discussions**: [Start a discussion](../../discussions)
- **Documentation**: Check [API docs](api.md) and [Architecture](architecture.md)

### Debug Information to Provide

When reporting issues, include:

```markdown
**Environment:**
- OS: Windows 11
- Python: 3.9.7
- Streamlit: 1.28.1
- Tesseract: 5.3.0

**Error Logs:**
```
Paste complete error traceback
```

**Steps to Reproduce:**
1. Upload receipt image
2. Click process
3. See error at step X

**Expected vs Actual:**
- Expected: Workflow completes successfully
- Actual: Stuck at OCR processing
```

---

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clear cache
streamlit cache clear

# Update Tesseract
# Download latest version from GitHub

# Test API endpoints
curl -X GET "https://openrouter.ai/api/v1/models" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Version Compatibility

| Component | Tested Version | Known Issues |
|-----------|----------------|--------------|
| Python | 3.8-3.11 | 3.12+ has PIL issues |
| Streamlit | 1.28+ | <1.20 has UI bugs |
| Tesseract | 5.0+ | <4.1 has accuracy issues |
| OpenRouter | Latest | Rate limiting on free tier |

---

<div align="center">

**🔧 Diagnose and resolve issues quickly with this comprehensive guide**

[⬆️ Back to Top](#-troubleshooting-guide) • [📚 API Docs](api.md) • [🏠 Home](../README.md)

</div>
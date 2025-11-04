# 🤝 Contributing to Expense Reimbursement Agent

<div align="center">

![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)
![PRs](https://img.shields.io/badge/PRs-Accepted-blue.svg)
![Issues](https://img.shields.io/badge/Issues-Open-orange.svg)

**We welcome contributions from the community! 🎉**

</div>

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🐛 Reporting Issues](#-reporting-issues)
- [🔧 Development Setup](#-development-setup)
- [💻 Development Workflow](#-development-workflow)
- [🧪 Testing Guidelines](#-testing-guidelines)
- [📝 Coding Standards](#-coding-standards)
- [🔄 Pull Request Process](#-pull-request-process)
- [🏗️ Architecture Guidelines](#️-architecture-guidelines)
- [📚 Documentation](#-documentation)
- [🎯 Feature Requests](#-feature-requests)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Tesseract OCR
- OpenRouter API key

### Setup for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/expense_reimbursement_conversational_agent.git
cd expense_reimbursement_conversational_agent

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run tests to verify setup
python tests/run_tests.py

# Start development
streamlit run app.py
```

---

## 🐛 Reporting Issues

### Bug Reports

**🐛 Found a bug?** Please create an issue with:

```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.9]
- Browser: [e.g., Chrome 91]

**Screenshots**
If applicable, add screenshots

**Additional Context**
Any other relevant information
```

### Feature Requests

**💡 Have an idea?** Submit a feature request with:

```markdown
**Feature Summary**
Brief description of the proposed feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
Detailed description of the solution

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Screenshots, mockups, or examples
```

---

## 🔧 Development Setup

### Environment Configuration

1. **Python Environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Tesseract OCR**
   ```bash
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   # Install and ensure it's in PATH
   tesseract --version
   ```

3. **API Keys**
   ```bash
   # Create .env file
   OPENROUTER_API_KEY=your_api_key_here
   ```

### IDE Setup

**Recommended VS Code Extensions:**
- Python
- Pylance
- GitLens
- Python Docstring Generator
- Code Runner

**VS Code Settings:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## 💻 Development Workflow

### Branching Strategy

```
main (protected)
├── feature/feature-name
├── bugfix/bug-description
├── hotfix/critical-fix
└── docs/documentation-update
```

### Development Process

1. **Choose an issue** from the [issue tracker](../../issues)
2. **Create a branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make changes** following our guidelines
4. **Write tests** for new functionality
5. **Run tests** to ensure everything works
   ```bash
   python tests/run_tests.py
   ```
6. **Update documentation** if needed
7. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
8. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

---

## 🧪 Testing Guidelines

### Test Categories

- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Agent interactions and workflows
- **End-to-End Tests**: Complete user journeys
- **Performance Tests**: OCR accuracy and processing speed

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test category
python -m pytest tests/ -k "unit"

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

```python
def test_receipt_processor():
    """Test receipt processing functionality"""
    # Arrange
    test_image = create_test_receipt()
    state = ExpenseState(receipt_image=test_image)

    # Act
    result = receipt_processor_agent_node(state)

    # Assert
    assert state["ocr_complete"] == True
    assert "amount" in state
    assert isinstance(state["amount"], (int, float))
```

### Test Coverage Requirements

- **Minimum Coverage**: 85%
- **Critical Paths**: 95% coverage
- **New Features**: 100% coverage for new code

---

## 📝 Coding Standards

### Python Style Guide

**Follow PEP 8** with these additions:

```python
# Good: Descriptive variable names
expense_amount = 45.67
customer_location = "Downtown"

# Bad: Abbreviations
exp_amt = 45.67
cust_loc = "Downtown"

# Good: Type hints
def process_receipt(image: Image.Image) -> Dict[str, Any]:
    pass

# Good: Docstrings
def classify_expense(state: ExpenseState) -> Command:
    """
    Classify expense by department and purpose.

    Args:
        state: Current expense state

    Returns:
        Next workflow command
    """
    pass
```

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

**Examples:**
```
feat: add OCR confidence scoring
fix: resolve PIL image serialization issue
docs: update API documentation
test: add integration tests for HITL workflow
```

### Code Organization

```
src/
├── agents/          # AI agent implementations
├── config/          # Configuration management
├── types/           # Type definitions
├── utils/           # Utility functions
└── workflow.py      # Main orchestration
```

---

## 🔄 Pull Request Process

### PR Checklist

- [ ] **Tests pass** locally
- [ ] **Code coverage** maintained
- [ ] **Documentation updated**
- [ ] **Changelog updated** (if applicable)
- [ ] **Breaking changes** documented

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots of UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] Ready for review
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs
2. **Peer Review**: At least one maintainer review
3. **Testing**: Reviewer runs tests locally
4. **Approval**: Maintainers approve and merge

---

## 🏗️ Architecture Guidelines

### Agent Design Principles

1. **Single Responsibility**: Each agent has one clear purpose
2. **Stateless Operations**: Agents don't maintain internal state
3. **Error Resilience**: Graceful handling of failures
4. **Testability**: Easy to unit test individual components

### State Management

```python
# Good: Immutable state updates
new_state = state.copy()
new_state["processed"] = True
return Command(goto="next_agent", update=new_state)

# Bad: Direct state mutation
state["processed"] = True  # Side effects
```

### Error Handling

```python
# Good: Specific exception handling
try:
    result = ocr_processor.process(image)
except TesseractNotFoundError:
    logger.warning("Tesseract not available, using fallback")
    result = fallback_processor.process(image)
except Exception as e:
    logger.error(f"OCR processing failed: {e}")
    raise ProcessingError("Unable to process receipt") from e
```

---

## 📚 Documentation

### Documentation Standards

- **README.md**: Project overview and setup
- **Code Comments**: Explain complex logic
- **Docstrings**: Function and class documentation
- **API Docs**: Public interface documentation

### Documentation Updates

When making changes:

1. Update relevant documentation
2. Add examples for new features
3. Update screenshots if UI changes
4. Verify all links work

---

## 🎯 Feature Requests

### Feature Request Process

1. **Check existing issues** for similar requests
2. **Create a feature request** with detailed description
3. **Community discussion** and feedback
4. **Prioritization** by maintainers
5. **Implementation planning** for approved features

### Feature Request Template

```markdown
## Feature Request

### Summary
Brief description of the requested feature

### Problem
What problem does this solve?

### Solution
Detailed description of the proposed solution

### Alternatives
Other approaches considered

### Additional Context
Screenshots, mockups, or related issues
```

---

## 🎉 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **GitHub** contributor statistics
- **Release notes** for significant contributions

### Contributor Levels

- **🥉 Contributor**: Bug fixes, documentation
- **🥈 Collaborator**: Feature implementations
- **🥇 Core Contributor**: Major features, architecture decisions

---

## 📞 Getting Help

### Communication Channels

- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions
- **Email**: For sensitive matters

### Response Times

- **Issues**: Acknowledged within 24 hours
- **PR Reviews**: Within 3 business days
- **Critical Bugs**: Immediate attention

---

<div align="center">

**Thank you for contributing to the Expense Reimbursement Conversational Agent! 🚀**

[⬆️ Back to Top](#-contributing-to-expense-reimbursement-agent) • [🏠 Home](../README.md)

</div>
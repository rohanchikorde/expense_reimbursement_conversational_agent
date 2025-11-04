# Test Cases and Sample Data

This folder contains test cases and sample data for testing the expense reimbursement conversational agent.

## Folder Structure

```
tests/
├── sample_data/
│   ├── receipts/          # Sample receipt images
│   │   ├── uber_receipt_1.png
│   │   ├── lyft_receipt_1.png
│   │   └── taxi_receipt_1.png
│   └── inputs/            # Test case definitions
│       └── test_cases.json
```

## Sample Receipts

Three professionally designed sample receipts are available:

1. **uber_receipt_1.png** - Uber ride receipt ($45.67)
2. **lyft_receipt_1.png** - Lyft ride receipt ($18.50)
3. **taxi_receipt_1.png** - City Taxi receipt ($28.75)

## Test Cases

The `test_cases.json` file contains predefined test scenarios with expected outcomes:

- **Business classifications**: Sales meetings, conferences, training
- **Approval logic**: Auto-approved vs requires manager approval
- **Edge cases**: High amounts, unclear purposes
- **Different merchants**: Uber, Lyft, and traditional taxi

## How to Use

1. **Manual Testing**: Upload the sample receipt images through the Streamlit UI
2. **Automated Testing**: Use the test cases JSON to validate agent behavior
3. **Integration Testing**: Test the complete workflow from upload to approval

## Expected Behavior

- Amounts under $50 (pre-2024) or $75 (post-2024) should be auto-approved
- Business-related expenses should be properly classified
- Unclear expenses should trigger HITL clarification
- All receipts should be accurately parsed by Tesseract OCR

## Adding New Test Cases

1. Create new receipt images in `receipts/` folder
2. Add corresponding test case entries to `test_cases.json`
3. Update expected classifications and approval logic as needed
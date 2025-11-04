import streamlit as st
from PIL import Image
from src.graph import expense_agent_system, ExpenseState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
import os
from dotenv import load_dotenv

load_dotenv()

st.title("Expense Reimbursement Conversational Agent")

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "default_thread"
if "last_interrupt" not in st.session_state:
    st.session_state.last_interrupt = None
if "workflow_started" not in st.session_state:
    st.session_state.workflow_started = False

# Display chat messages from state if available
try:
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state = expense_agent_system.get_state(config)
    if state.values and "messages" in state.values:
        messages = state.values["messages"]
        for msg in messages:
            if isinstance(msg, AIMessage):
                with st.chat_message("assistant"):
                    st.write(msg.content)
            elif isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.write(msg.content)
except Exception as e:
    st.write(f"Error loading state: {e}")

# Sidebar for upload
with st.sidebar:
    st.header("Upload Receipt")
    uploaded_file = st.file_uploader("Upload your Uber/Lyft receipt", type=["png", "jpg", "jpeg"])
    if uploaded_file and not st.session_state.workflow_started:
        image = Image.open(uploaded_file)
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
            employee_id="user_123",
            approval_determined=False
        )
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        try:
            result = expense_agent_system.invoke(initial_state, config)
            st.session_state.workflow_started = True
            st.rerun()
        except Exception as e:
            st.error(f"Error starting workflow: {e}")

# Check for interrupts
config = {"configurable": {"thread_id": st.session_state.thread_id}}
try:
    state = expense_agent_system.get_state(config)
    if state.next and any("hitl" in str(task) for task in state.tasks if task.interrupts):
        for task in state.tasks:
            if task.interrupts:
                interrupt_value = task.interrupts[0].value
                st.session_state.last_interrupt = interrupt_value
                with st.chat_message("assistant"):
                    st.write(interrupt_value)
                break
except:
    pass

# Chat input for user responses
if st.session_state.last_interrupt:
    user_input = st.chat_input("Your response:")
    if user_input:
        # Resume workflow with user input
        try:
            result = expense_agent_system.invoke(Command(resume=user_input), config)
            st.session_state.last_interrupt = None
            st.rerun()
        except Exception as e:
            st.error(f"Error resuming workflow: {e}")
elif st.session_state.workflow_started:
    # Check if workflow is complete
    try:
        state = expense_agent_system.get_state(config)
        if not state.next:
            with st.chat_message("assistant"):
                st.write("Workflow complete!")
                final_state = state.values
                if final_state.get("approval_status") == "auto_approved":
                    st.write("Your expense has been auto-approved.")
                else:
                    st.write("Your expense requires manager approval.")
            if st.button("Start New Request"):
                # Reset
                st.session_state.workflow_started = False
                st.session_state.thread_id = f"thread_{len(st.session_state.thread_id.split('_'))}"
                st.rerun()
    except Exception as e:
        st.error(f"Error checking completion: {e}")
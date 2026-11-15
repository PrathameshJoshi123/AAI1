"""Tests for Human-in-the-Loop Interruption and Resumption."""
import sqlite3
import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from app.ai.graph.orchestrator import InsuranceWorkflowOrchestrator
from app.ai.graph.state import create_initial_agent_state


@pytest.mark.asyncio
async def test_human_in_the_loop_interruption_and_resume():
    """
    Workflow triggers interrupt when coverage > 500k,
    pauses execution, and resumes once reviewer approves.
    """
    orchestrator = InsuranceWorkflowOrchestrator()
    # In-memory checkpointer for test
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    graph = orchestrator.build_graph().compile(checkpointer=saver)

    thread_id = "hitl-test-thread-101"
    config = {"configurable": {"thread_id": thread_id}}

    state = create_initial_agent_state(
        thread_id=thread_id,
        session_id="hitl-session",
        user_role="Customer",
        initial_messages=[HumanMessage(content="I want 1,000,000 life insurance coverage")],
    )
    # Trigger high coverage flag
    state["qualification_data"] = {
        "desired_coverage": 1000000.0,
        "has_pre_existing_conditions": True,
    }

    # First execution: Pauses at interrupt
    output_state = await graph.ainvoke(state, config=config)

    # Verify graph paused at interrupt
    snapshot = graph.get_state(config)
    assert len(snapshot.tasks) > 0
    assert snapshot.tasks[0].interrupts is not None
    interrupt_payload = snapshot.tasks[0].interrupts[0].value
    assert interrupt_payload["reason"] == "UNDERWRITING_ESCALATION_REQUIRED"

    # Human Underwriter Review Decision Submitted via Resume Command
    human_decision = {
        "reviewer": "underwriter@ps21.com",
        "decision": "Approved Standard",
        "notes": "Medical records reviewed. Clean history.",
    }
    resume_cmd = Command(resume=human_decision)
    resumed_state = await graph.ainvoke(resume_cmd, config=config)

    # Workflow finishes successfully
    assert resumed_state["is_completed"] is True
    assert resumed_state["underwriting_decision"]["decision"] == "Approved Standard"
    last_msg = resumed_state["messages"][-1].content
    assert "approved" in last_msg.lower()

    conn.close()


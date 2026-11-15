"""Tests for LangGraph Multi-Agent Workflow and State transitions."""
import pytest
from langchain_core.messages import HumanMessage
from app.ai.graph.orchestrator import InsuranceWorkflowOrchestrator
from app.ai.graph.state import create_initial_agent_state


@pytest.mark.asyncio
async def test_langgraph_flow_quote_intent():
    """Workflow state transitions properly when user expresses quote intent."""
    orchestrator = InsuranceWorkflowOrchestrator()
    graph = orchestrator.build_graph().compile()

    state = create_initial_agent_state(
        thread_id="test-thread-quote",
        session_id="test-session-1",
        user_role="Customer",
        initial_messages=[HumanMessage(content="Can you give me a quote for term life?")],
    )

    output = await graph.ainvoke(state)

    assert output["is_completed"] is True
    assert output["next_step"] == "get_quote"
    assert len(output["messages"]) > 1
    # Check last message mentions quote
    last_msg = output["messages"][-1].content
    assert "indicative quote" in last_msg.lower() or "quote" in last_msg.lower()


@pytest.mark.asyncio
async def test_langgraph_flow_advisor_handoff_intent():
    """Workflow routes to advisor handoff when human representative requested."""
    orchestrator = InsuranceWorkflowOrchestrator()
    graph = orchestrator.build_graph().compile()

    state = create_initial_agent_state(
        thread_id="test-thread-advisor",
        session_id="test-session-2",
        user_role="Customer",
        initial_messages=[HumanMessage(content="I want to speak with a human advisor please")],
    )

    output = await graph.ainvoke(state)

    assert output["is_completed"] is True
    assert output["next_step"] == "speak_to_human"
    assert output["requires_human_review"] is True


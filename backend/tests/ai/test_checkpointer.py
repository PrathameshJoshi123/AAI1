"""Tests for SQLite Checkpointing and Multi-Turn Thread Persistence."""
import sqlite3
import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from app.ai.graph.orchestrator import InsuranceWorkflowOrchestrator
from app.ai.graph.state import create_initial_agent_state


@pytest.mark.asyncio
async def test_checkpoint_persistence_across_turns():
    """State and message history persist in SQLite checkpointer across separate invocations."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()

    orchestrator = InsuranceWorkflowOrchestrator()
    graph = orchestrator.build_graph().compile(checkpointer=saver)

    thread_id = "persistence-thread-555"
    config = {"configurable": {"thread_id": thread_id}}

    # Turn 1: Customer asks for recommendations
    state_turn1 = create_initial_agent_state(
        thread_id=thread_id,
        session_id="session-persist",
        user_role="Customer",
        initial_messages=[HumanMessage(content="Hello, what insurance options do you offer?")],
    )
    await graph.ainvoke(state_turn1, config=config)

    # Inspect persisted state in checkpointer
    snapshot_turn1 = graph.get_state(config)
    assert snapshot_turn1 is not None
    assert len(snapshot_turn1.values["messages"]) == 2  # Human + AI

    # Turn 2: Follow-up question on same thread
    state_turn2 = {
        "messages": [HumanMessage(content="Give me an indicative quote for Term Life")]
    }
    await graph.ainvoke(state_turn2, config=config)

    # Inspect persisted state after Turn 2
    snapshot_turn2 = graph.get_state(config)
    assert len(snapshot_turn2.values["messages"]) == 4  # 2 Human + 2 AI
    assert snapshot_turn2.values["execution_steps_count"] >= 2

    conn.close()


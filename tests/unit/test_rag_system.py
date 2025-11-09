"""
Unit tests for RAG System (from refactoring.md).
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.mark.asyncio
async def test_rag_system_initialization(temp_working_dir):
    """Test RAG system initialization."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    # Mock memory manager
    mock_memory = Mock()
    mock_memory.get_recent_conversation = Mock(return_value=[])
    mock_memory.query_similar_patterns = Mock(return_value=[])

    # Initialize RAG system
    rag = RAGSystem(memory_manager=mock_memory)

    assert rag is not None
    assert rag.memory == mock_memory


@pytest.mark.asyncio
async def test_augment_query_basic(temp_working_dir):
    """Test basic query augmentation."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    # Mock memory manager
    mock_memory = Mock()
    mock_memory.get_recent_conversation = Mock(
        return_value=[{"role": "user", "content": "Hello"}]
    )
    mock_memory.query_similar_patterns = Mock(return_value=[])

    rag = RAGSystem(memory_manager=mock_memory, embedding_model=None)

    # Test query augmentation
    result = await rag.augment_query("Create a login page")

    assert "original_query" in result
    assert "augmented_query" in result
    assert "context" in result
    assert result["original_query"] == "Create a login page"


def test_rag_without_dependencies(temp_working_dir):
    """Test RAG system gracefully handles missing dependencies."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    mock_memory = Mock()

    # Should not crash even if chromadb/transformers not installed
    rag = RAGSystem(memory_manager=mock_memory)

    # Verify it handles missing dependencies gracefully
    assert rag.memory == mock_memory


@pytest.mark.asyncio
async def test_code_indexing_disabled_without_embeddings():
    """Test that code indexing is disabled without embedding model."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    mock_memory = Mock()
    rag = RAGSystem(memory_manager=mock_memory, embedding_model=None)

    # Index code should not crash
    rag.index_code("test.py", "print('hello')", {})

    # Search should return empty list
    results = rag.search_code("test query")
    assert results == []


@pytest.mark.asyncio
async def test_context_augmentation_structure():
    """Test that augmented context has correct structure."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    mock_memory = Mock()
    mock_memory.get_recent_conversation = Mock(
        return_value=[
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Response"},
        ]
    )
    mock_memory.query_similar_patterns = Mock(return_value=[])

    rag = RAGSystem(memory_manager=mock_memory, embedding_model=None)

    result = await rag.augment_query("New query")

    # Check structure
    assert "context" in result
    context = result["context"]

    assert "conversation_context" in context
    assert len(context["conversation_context"]) == 2


@pytest.mark.asyncio
async def test_retrieve_for_task():
    """Test retrieve_for_task method."""
    from apps.realtime_poc.big_three_realtime_agents.memory.rag_system import RAGSystem

    mock_memory = Mock()
    rag = RAGSystem(memory_manager=mock_memory, embedding_model=None)

    # Test backend task
    context = await rag.retrieve_for_task(
        task_description="Build API endpoints", expert_type="BackendExpert"
    )

    assert context is not None
    assert "relevant_code" in context or "similar_tasks" in context

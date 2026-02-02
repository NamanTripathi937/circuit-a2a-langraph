import logging
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage
from langchain_core.messages import AIMessage, AIMessageChunk
from typing_extensions import TypedDict
from llm import get_llm
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


class State(TypedDict):
    messages: list  # Contains messages with HumanMessage AIMessage
    metadata: dict
    thread_id: str


def generate_joke(state: State) -> State:
    """generate_joke with error handling"""
    try:
        logger.info("generate_joke node called")
        input_data = {"messages": state["messages"][-1]}
        #print(input_data)
        thread_id = state["thread_id"]
        metadata = state["metadata"]

        chat_messages = [
            {"role": "system", "content": "You are an assistant that tells jokes."},
            {"role": "user", "content": state["messages"][-1].content}, # Use the actual user query
        ]
        llm = get_llm()
        for chunk in llm.stream(
                chat_messages,
                config={"configurable": {"thread_id": thread_id}},
                stream=True, metadata=metadata
        ):
            yield chunk


    except Exception as e:
        logger.error(f"question_answer error: {str(e)}", exc_info=True)
        raise
    yield {"messages": [AIMessage("")], "metadata": metadata, "thread_id": thread_id}


def build_graph():
    builder = StateGraph(State)
    try:
        builder.add_edge(START, "generate_joke")
        builder.add_node("generate_joke", generate_joke)
        builder.add_edge("generate_joke", END)
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        return graph
    except Exception as e:
        logger.error(f"Graph compilation failed: {str(e)}", exc_info=True)
        raise


class JokeAgent:
    def __init__(self):
        self.graph = build_graph()

    async def stream(self, query: str, context_id: str):
        """Stream the graph with input data."""
        input_data = {
            "messages": [
                HumanMessage(content=query)
            ],
            "thread_id": context_id,
            "metadata": {
                "source": "joke_agent",
                "description": "This is a joke agent that tells jokes based on user input."
            }
        }
        config = {'configurable': {'thread_id': context_id}}
        try:
            for event_type, chunk_data in self.graph.stream(input_data, config, stream_mode=["updates", "messages"]):
                #print(f"Event type: {event_type}, Chunk data: {chunk_data}")
                if event_type == "updates":
                    # Handle updates
                    if isinstance(chunk_data, dict):
                        for key, value in chunk_data.items():
                            #print(f"Update key: {key}, value: {value}")
                            msgs = value.get("messages", [])
                            for msg in msgs:
                                if isinstance(msg, AIMessage):
                                    #print(f"Chunk content: {i.content}")
                                    yield {
                                        'is_task_complete': False,
                                        'require_user_input': False,
                                        'content': msg.content,
                                    }
                elif event_type == "messages":
                    for chunk in chunk_data:
                        if isinstance(chunk, AIMessageChunk):
                            yield {
                                'is_task_complete': False,
                                'require_user_input': False,
                                'content': chunk.content,
                            }
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': ""
            }
        except Exception as e:
            logger.error(f"Error in JokeAgent stream: {str(e)}", exc_info=True)
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': "An error occurred while generating the joke."
            }


    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
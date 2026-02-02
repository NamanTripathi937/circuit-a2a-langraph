import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from joke_agent import JokeAgent

log = logging.getLogger(__name__)


class JokeAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = JokeAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue,) -> None:
        log.info(f"Executing JokeAgentExecutor with context: {context}")
        if not isinstance(self.agent, JokeAgent):
            raise UnsupportedOperationError("This executor only supports JokeAgentExecutor.")

        query = context.get_user_input('query')
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        session_id = task.context_id
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for part in self.agent.stream(query, session_id):
                if not part['is_task_complete']:
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            part['content'],
                            task.context_id,
                            task.id,
                        ),
                    )
                else:
                    await updater.add_artifact(
                        [Part(root=TextPart(text=part['content']))],
                        name='Joke generated',
                    )
                    await updater.complete()
        except Exception as e:
            await updater.update_status(
                TaskState.FAILED,
                new_agent_text_message(
                    "An error occurred during execution.",
                    task.context_id,
                    task.id,
                ),
            )
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> Task:
        task = context.current_task
        if task:
            updater = TaskUpdater(event_queue, task.id, task.context_id)
            await updater.update_status(
                TaskState.CANCELLED,
                new_agent_text_message(
                    "Task has been cancelled.",
                    task.context_id,
                    task.id,
                ),
            )
            return task

        raise InvalidParamsError("No current task to cancel.")

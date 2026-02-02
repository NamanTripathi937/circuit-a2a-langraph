import logging
import os
import sys

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from joke_agent import JokeAgent
from agent_executors import JokeAgentExecutor
from oauth2_middleware import OAuth2Middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPPKeyError(Exception):
    """Exception for missing APP key."""


class MissingCredentialsError(Exception):
    """Exception for missing Credentials key."""

class MissingAPIEndpoint(Exception):
    """Exception for missing API Endpoint key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10000)
def main(host, port):
    """Starts the Currency Agent server."""
    try:
        if os.getenv('GOOGLE_API_KEY') is None:
            raise MissingAPPKeyError(
                'GOOGLE_API_KEY environment variable not set.'
            )
        # if os.getenv("CIRCUIT_LLM_API_CLIENT_ID") is None or os.getenv("CIRCUIT_LLM_API_CLIENT_SECRET") is None:
        #     raise MissingCredentialsError(
        #         'CIRCUIT_LLM_API_CLIENT_ID or CIRCUIT_LLM_API_CLIENT_SECRET environment variables not set.'
        #     )

        # if os.getenv("CIRCUIT_LLM_API_ENDPOINT") is None:
        #     raise MissingCredentialsError(
        #         'CIRCUIT_LLM_API_ENDPOINT environment variables not set.'
        #     )



        capabilities = AgentCapabilities(streaming=True, push_notifications=True)
        skill = AgentSkill(
            id='say_joke',
            name='Joke Generator',
            description='AI system designed to generate or deliver humor',
            tags=['joke','humor', 'entertainment', 'funny', 'comedy'],
            examples=['Craft a joke about caffeine', 'Create a joke about the first time someone used a smartphone'],
        )
        agent_card = AgentCard(
            name='Joke Agent',
            description='AI system designed to generate or deliver humor',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            default_input_modes=JokeAgent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=JokeAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )


        # --8<-- [start:DefaultRequestHandler]
        httpx_client = httpx.AsyncClient()
        push_config_store = InMemoryPushNotificationConfigStore()
        push_sender = BasePushNotificationSender(httpx_client=httpx_client,
                        config_store=push_config_store)
        request_handler = DefaultRequestHandler(
            agent_executor=JokeAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_config_store=push_config_store,
            push_sender=push_sender
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )


        app = server.build()
        # app.add_middleware(
        #     OAuth2Middleware,
        #     agent_card=agent_card,
        #     public_paths=['/.well-known/agent.json', '/.well-known/agent-card.json'],
        # )
        uvicorn.run(app, host=host, port=port)
        # --8<-- [end:DefaultRequestHandler]

    except MissingAPPKeyError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except MissingCredentialsError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
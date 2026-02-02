import logging
import uuid

from typing import Any
from uuid import uuid4
import asyncio
import httpx
import json
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    TextPart,
    Task,
    Message,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    MessageSendConfiguration,
    SendMessageRequest,
    SendStreamingMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
    JSONRPCErrorResponse,
    AgentCard,
)
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)


async def main() -> None:
    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    # --8<-- [start:A2ACardResolver]

    base_url = 'http://localhost:8080'
    thread_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )
        # --8<-- [end:A2ACardResolver]

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f'Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}'
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info('Successfully fetched public agent card:')
            logger.info(
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card
            logger.info(
                '\nUsing PUBLIC agent card for client initialization (default).'
            )

            if _public_card.supports_authenticated_extended_card:
                try:
                    logger.info(
                        '\nPublic card supports authenticated extended card. '
                        'Attempting to fetch from: '
                        f'{base_url}{EXTENDED_AGENT_CARD_PATH}'
                    )
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    logger.info(
                        'Successfully fetched authenticated extended agent card:'
                    )
                    logger.info(
                        _extended_card.model_dump_json(
                            indent=2, exclude_none=True
                        )
                    )
                    final_agent_card_to_use = (
                        _extended_card  # Update to use the extended card
                    )
                    logger.info(
                        '\nUsing AUTHENTICATED EXTENDED agent card for client '
                        'initialization.'
                    )
                except Exception as e_extended:
                    logger.warning(
                        f'Failed to fetch extended agent card: {e_extended}. '
                        'Will proceed with public card.',
                        exc_info=True,
                    )
            elif (
                _public_card
            ):  # supports_authenticated_extended_card is False or None
                logger.info(
                    '\nPublic card does not indicate support for an extended card. Using public card.'
                )

        except Exception as e:
            logger.error(
                f'Critical error fetching public agent card: {e}', exc_info=True
            )
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e

        # --8<-- [start:send_message]
        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info('A2AClient initialized.')

        message = Message(
            role='user',
            parts=[TextPart(text="Tell me a joke which is trending")],
            message_id=request_id,
            context_id=thread_id,
            metadata={"request_id": request_id,
                      "thread_id": thread_id}
        )

        a2a_payload = MessageSendParams(
            message=message,
            configuration=MessageSendConfiguration(
                accepted_output_modes=['text'],
            ),
        )
        logger.info(f"Sending message to agent: {final_agent_card_to_use.url}")
        # Send the message using the A2A client
        response_stream = client.send_message_streaming(
            SendStreamingMessageRequest(
                id=request_id,
                params=a2a_payload,
            )
        )
        logger.info(f"Streaming response:")
        combined_text = ""
        async for result in response_stream:
            logger.debug(f"Received result: {result.model_dump_json(exclude_none=True)}")
            # print(result)
            # print(get_response_text_and_is_final(result))
            if isinstance(result.root, JSONRPCErrorResponse):
                logger.warning("Error: %s", result.root.error)
            event = result.root.result
            #print(event)
            contextId = event.context_id
            if (
                    isinstance(event, Task)
            ):
                taskId = event.id
            elif (isinstance(event, TaskStatusUpdateEvent)
                  or isinstance(event, TaskArtifactUpdateEvent)
            ):
                taskId = event.task_id
            elif isinstance(event, Message):
                message = event
            print(
                'stream event =>', json.loads(event.model_dump_json(exclude_none=True))
            )
            #print(result.model_dump_json(exclude_none=True))
        # Upon completion of the stream. Retrieve the full task if one was made.
        if taskId:
            taskResult = await client.get_task(
                GetTaskRequest(
                    id=str(uuid4()),
                    params=TaskQueryParams(id=taskId),
                )
            )
            taskResult = taskResult.root.result

            print(
                'Task Result => ', json.loads(taskResult.model_dump_json(exclude_none=True))
            )


if __name__ == '__main__':

    asyncio.run(main())
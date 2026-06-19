from copy import deepcopy
from typing import List

from chat.domain.entities import ChatMessage


class ChatMessageProjector:
    """负责把内部 ChatMessage 投影为持久化、Memory、摘要等不同消费方需要的形态。"""

    def for_persistence(
        self,
        chat_record_messages: List[ChatMessage],
    ) -> List[ChatMessage]:
        messages = deepcopy(chat_record_messages)
        for message in messages:
            if message.persisted_output_placeholder is None:
                continue
            message.content = message.persisted_output_placeholder
            message.persisted_output_placeholder = None
        return messages
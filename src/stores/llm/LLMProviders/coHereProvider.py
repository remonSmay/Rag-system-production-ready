import logging  # noqa: N999

import cohere

from ..LLMEnums import CoHereEnums, DocumentTypeEnum
from ..LLMInterface import LLMinterface


class CoHereProvider(LLMinterface):
    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int = 1000,
        default_generation_max_output: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output = default_generation_max_output
        self.default_generation_temperature = default_generation_temperature
        # * the init include the variable from class parameter and own variable initiation
        self.client = cohere.ClientV2(api_key=api_key)
        self.generation_model_id: str | None = None
        self.embedding_model_id: str | None = None
        self.embedding_size: int | None = None
        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def generate_text(
        self,
        prompt: str,
        chat_history: list,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str | None:
        if not self.client:
            self.logger.error("the client in cohere is not found ")
            return None
        if not self.generation_model_id:
            self.logger.error("the model_id  in cohere is not found ")
            return None
        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_generation_max_output
        )
        if max_output_tokens <= 0:
            self.logger.error("max_output_tokens must be greater than 0")
            return None

        temperature = (
            temperature if temperature is not None else self.default_generation_temperature
        )
        if temperature < 0:
            self.logger.error("temperature must be greater than or equal to 0")
            return None

        # copy the provided chat history so we don't mutate the caller's list
        if chat_history is None:
            messages = []
        elif isinstance(chat_history, list):
            messages = list(chat_history)
        else:
            self.logger.error("chat_history must be a list or None")
            return None

        messages.append(self.construct_prompt(prompt, CoHereEnums.USER.value))
        try:
            response = self.client.chat(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature,
            )
        except Exception as e:
            self.logger.exception(f"the error while generation the cohere text {e}")
            return None
        if (
            not response
            or not response.message
            or not response.message.content
            or not getattr(response.message.content[0], "text", None)
        ):
            self.logger.error("while generation the text found error")
            return None
        return getattr(response.message.content[0], "text", None)
    
    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {
            "role": role,
            "content": self.process_text(prompt),
        }

    def generate_embedding(self, text: str, document_type: str | None = None):
        if not self.client:
            self.logger.error("the client in cohere is not found ")
            return None
        if not self.embedding_model_id:
            self.logger.error("the embedding model_id in cohere is not found ")
            return None
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[self.process_text(text)],
                input_type=input_type,
                output_dimension=self.embedding_size,
                embedding_types=["float"],
            )
        except Exception as e:
            self.logger.exception(f"error generating cohere embedding: {e}")
            return None
        if not response or not getattr(response, "embeddings", None):
            self.logger.error("empty embedding the text ")
            return None

        embeddings = getattr(response, "embeddings")
        # Support multiple possible response shapes: list of embeddings, or object with .float or .values
        if isinstance(embeddings, list) and len(embeddings) > 0:
            return embeddings[0]
        float_attr = getattr(embeddings, "float", None)
        if isinstance(float_attr, list) and len(float_attr) > 0:
            return float_attr[0]
        values_attr = getattr(embeddings, "values", None)
        if isinstance(values_attr, list) and len(values_attr) > 0:
            return values_attr[0]
        self.logger.error("empty embedding the text ")
        return None
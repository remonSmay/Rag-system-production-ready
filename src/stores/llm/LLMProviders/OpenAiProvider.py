import logging  # noqa: N999

from openai import OpenAI

from ..LLMEnums import OpenAIEnums
from ..LLMInterface import LLMinterface


class OpenAiProvider(LLMinterface):
    def __init__(
        self,
        api_key: str,
        api_url: str,
        default_input_max_characters: int = 1000,
        default_generation_max_output: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output = default_generation_max_output
        self.default_generation_temperature = default_generation_temperature
        # client from openai (api,api_url)
        # model_text_id
        # model _embedding_id & size model embedding
        # logging

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.generation_model_id: str | None = None
        self.embedding_model_id: str | None = None
        self.embedding_size: int | None = None
        self.enums = OpenAIEnums
        self.logger = logging.getLogger(
            __name__
        )  # __name__ : Special variable that indicates the current module's name.

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
        chat_history: list ,
        max_output_tokens: int | None = None,
        temperature: float = 0.1,
    ) -> str | None:
        # Validate client and model ID
        # Set max_output_tokens if not provided
        # Append prompt to chat_history
        # Call OpenAI API to create response
        # Return generated text
        if not self.client:
            self.logger.error("OpenAi client not found ")
            return None
        if not self.generation_model_id:
            self.logger.error("the generation model id is not found ")
            return None

        if chat_history is None:
            chat_history = []

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens
            else self.default_input_max_characters
        )
        temperature = (
            temperature if temperature else self.default_generation_temperature
        )

        chat_history.append(self.construct_prompt(prompt, role=OpenAIEnums.USER.value))

        try:
            response = self.client.responses.create(
                model=self.generation_model_id,
                input=chat_history,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        except Exception as exc:
            self.logger.exception("Error while generating response: %s", exc)
            return None

        output_text = getattr(response, "output_text", None)
        if not output_text:
            self.logger.error("Empty response text from OpenAI.")
            return None
        return output_text
    
    def generate_embedding(self, text: str, document_type: str | None = None):
        if not self.client:
            self.logger.error("OpenAi client not found ")
            return None
        if not self.embedding_model_id:
            self.logger.error("the generation model id is not found with OpenAi")
            return None

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id, input=text , encoding_format="float" , dimensions=384
            )
        except Exception as exc:
            self.logger.exception("error while creating embedding : %s",exc)
            return None

        if not response.data or not response.data[0].embedding:
            self.logger.error("Invalid embedding response from OpenAI.")
            return None
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {"role": role, "content": self.process_text(prompt)}

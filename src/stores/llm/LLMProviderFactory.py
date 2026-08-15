from .LLMProviders import CoHereProvider, OpenAiProvider
from .LLMEnums import LLMEnums
from .LLMInterface import LLMinterface
from helpers.config import Settings


class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config

    def create(self, provider: str | None) -> LLMinterface | None:
        if provider is None:
            return None

        if provider == LLMEnums.OPENAI.value:
            if not self.config.OPENAI_API_KEY or not self.config.OPENAI_API_URL:
                return None
            return OpenAiProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS
                if self.config.INPUT_DEFAULT_MAX_CHARACTERS is not None
                else 1000,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
                if self.config.GENERATION_DEFAULT_TEMPERATURE is not None
                else 0.1,
                default_generation_max_output=self.config.GENERATION_DEFAULT_MAX_TOKENS
                if self.config.GENERATION_DEFAULT_MAX_TOKENS is not None
                else 1000,
            )
        elif provider == LLMEnums.COHERE.value:
            if not self.config.COHERE_API_KEY:
                return None
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS
                if self.config.INPUT_DEFAULT_MAX_CHARACTERS is not None
                else 1000,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
                if self.config.GENERATION_DEFAULT_TEMPERATURE is not None
                else 0.1,
                default_generation_max_output=self.config.GENERATION_DEFAULT_MAX_TOKENS
                if self.config.GENERATION_DEFAULT_MAX_TOKENS is not None
                else 1000,
            )
        else:
            return None

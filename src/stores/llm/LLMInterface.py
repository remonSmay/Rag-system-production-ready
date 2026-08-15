from typing import List
from abc import ABC , abstractmethod
class LLMinterface (ABC):
    @abstractmethod
    def set_generation_model(self , model_id : str):
        """
        set_generation_model Set the model ID to be used for text generation.

        Args:
            model_id (str): id of the model
        Ex:
            self.model_id = model_id
        """
        pass
    @abstractmethod 
    def set_embedding_model ( self , model_id:str , embedding_size : int ) :
        pass
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        chat_history: List ,
        max_output_tokens: int | None = None,
        temperature: float = 0.1,
    ) -> str | None:
        pass

    @abstractmethod
    def generate_embedding(self,text:str , document_type:str |None = None):
        pass
    @abstractmethod
    def construct_prompt(self, prompt :str , role:str )->dict:
        pass

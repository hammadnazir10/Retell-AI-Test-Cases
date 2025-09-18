
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """Initialize the agent with OpenAI LLM - optimized for speed"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=api_key,
            max_tokens=3000,  # Limit tokens for faster response
        )
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return result"""
        pass
    
    def get_llm(self) -> ChatOpenAI:
        """Get the LLM instance"""
        return self.llm

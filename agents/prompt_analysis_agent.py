"""
Agent responsible for analyzing AI prompts to understand their purpose and context
"""

from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent

class PromptAnalysisAgent(BaseAgent):
    """Agent that analyzes AI prompts to understand their type and context"""
    
    def process(self, prompt: str) -> str:
        """Analyze the prompt and return insights about its purpose and context"""
        analysis_prompt = f"""
        Analyze this AI prompt from a human user's perspective and determine:
        1. What type of AI system this is (chatbot, voice assistant, API, content generator, etc.)
        2. What the main functionality is that users would want
        3. What inputs users would naturally provide
        4. What outputs users would expect
        5. What real-world scenarios users might encounter
        6. What problems or frustrations users might have
        7. How different types of users (impatient, confused, detailed, casual) would interact with it
        
        Think about how real people would actually use this system in their daily lives.
        
        Prompt: {prompt}...
        """
        
        messages = [
            SystemMessage(content="You are an expert at analyzing AI prompts from a human user's perspective, understanding how real people would interact with these systems."),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

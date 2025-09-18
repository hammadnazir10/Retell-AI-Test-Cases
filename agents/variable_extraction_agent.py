
import re
import json
from typing import Dict, List
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent

class VariableExtractionAgent(BaseAgent):
    """Agent that extracts and generates values for dynamic variables in prompts"""
    
    def process(self, prompt: str) -> Dict[str, any]:
        """Extract variables and generate realistic values for them"""
        # Extract variables using regex
        variables = self._extract_variables(prompt)
        
        if not variables:
            return {}
        
        # Generate realistic values for the variables
        variable_values = self._generate_variable_values(variables, prompt)
        
        return variable_values
    
    def _extract_variables(self, prompt: str) -> List[str]:
        """Extract all dynamic variables from the prompt using {{}} pattern"""
        pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(pattern, prompt)
        return list(set(variables))  # Remove duplicates
    
    def _generate_variable_values(self, variables: List[str], prompt_context: str) -> Dict[str, str]:
        """Generate realistic values for all dynamic variables in the prompt"""
        if not variables:
            return {}
        
        # Create a prompt to generate realistic values - OPTIMIZED FOR SPEED
        values_prompt = f"""
        Generate realistic values for these variables: {', '.join(variables)}
        
        Context: {prompt_context[:500]}...
        
        Return ONLY JSON:
        {{
            "variable1": "value1",
            "variable2": "value2"
        }}
        
        Generate realistic business/customer service values for ALL {len(variables)} variables.
        """
        
        messages = [
            SystemMessage(content="You are a fast variable generator. Return only JSON."),
            HumanMessage(content=values_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: generate simple values
        return self._generate_fallback_values(variables)
    
    def _generate_fallback_values(self, variables: List[str]) -> Dict[str, str]:
        """Generate fallback values when LLM response parsing fails"""
        fallback_values = {}
        for var in variables:
            if 'language' in var.lower():
                fallback_values[var] = "English"
            elif 'name' in var.lower():
                fallback_values[var] = "Assistant"
            elif 'company' in var.lower():
                fallback_values[var] = "TechCorp"
            else:
                fallback_values[var] = f"Sample_{var}"
        
        return fallback_values
    
    def get_detected_variables(self, prompt: str) -> List[str]:
        """Get list of detected variables for informational purposes"""
        return self._extract_variables(prompt)

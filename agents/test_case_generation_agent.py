
import re
import json
from typing import List, Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent

class TestCaseGenerationAgent(BaseAgent):
    """Agent that generates human-like test cases for any AI prompt"""
    
    def process(self, prompt: str, variable_values: Dict[str, Any] = None, all_variables: List[str] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive test cases for the given prompt"""
        system_prompt = self._build_system_prompt(variable_values, all_variables)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate test cases for this prompt: {prompt}...")
        ]
        
        response = self.llm.invoke(messages)
        test_cases = self._parse_test_cases(response.content)
        
        # GPT should generate exactly 10 test cases - no post-processing needed
        if len(test_cases) != 10:
            print(f"Warning: Expected 10 test cases, but got {len(test_cases)}")
        
        # Let GPT handle variable generation naturally - no post-processing
        
        return test_cases
    
    
    def _build_system_prompt(self, variable_values: Dict[str, Any] = None, all_variables: List[str] = None) -> str:
        """Build the system prompt for test case generation"""
        variables_text = ""
        if variable_values:
            variables_text = f"Using these EXACT variable values for ALL test cases: {variable_values}"
        else:
            variables_text = "No specific variable values provided - generate realistic ones as needed"
        
        # Add information about all detected variables
        all_vars_text = ""
        if all_variables:
            all_vars_text = f"\n\nDETECTED VARIABLES:\n{', '.join(all_variables)}\n\nNote: These variables will be handled separately and not included in individual test cases."
        
        return f"""
        You are a fast test case generator. Generate EXACTLY 10 realistic test scenarios.
        
        STRUCTURE: Each test case = {{"user_prompt": "...", "success_criteria": "..."}}
        
        {variables_text}{all_vars_text}
        
        ANALYZE the prompt and create 10 scenarios covering:
        - Normal usage (3 cases)
        - Challenging situations (3 cases) 
        - Edge cases (2 cases)
        - Error scenarios (2 cases)
        
        Example format:
        {{
          "user_prompt": "Detailed realistic user message with context and emotion",
          "success_criteria": "What the AI should accomplish"
        }}
        
        Make scenarios realistic with:
        - Natural speech patterns
        - Emotional context
        - Specific details
        - Varied complexity
        
        Return ONLY a JSON array of exactly 10 test cases.
        NO dynamic_variables in individual cases.
        """
    
    def _parse_test_cases(self, response_content: str) -> List[Dict[str, Any]]:
        """Parse test cases from LLM response"""
        # Clean the response content first
        cleaned_content = response_content.strip()
        
        # Try multiple patterns to find JSON
        json_patterns = [
            r'```json\s*(\[.*?\])\s*```',  # JSON in code blocks
            r'```\s*(\[.*?\])\s*```',      # JSON in generic code blocks
            r'\[\s*\{.*?\}\s*\]',          # Direct JSON array
            r'\[.*?\]'                     # Any array-like structure
        ]
        
        json_text = None
        for pattern in json_patterns:
            json_match = re.search(pattern, cleaned_content, re.DOTALL)
            if json_match:
                if json_match.groups() and json_match.group(1):
                    json_text = json_match.group(1)
                else:
                    json_text = json_match.group(0)
                break
        
        if not json_text:
                raise ValueError("Failed to generate valid test cases. Agent response did not contain valid JSON.")
        
        # Clean up the JSON text
        json_text = json_text.strip()
        
        # Try to fix common JSON issues
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            # Try to fix common issues
            try:
                # Remove any text after the last ]
                if json_text.count(']') > 0:
                    last_bracket = json_text.rfind(']')
                    json_text = json_text[:last_bracket + 1]
                
                # Try parsing again
                return json.loads(json_text)
            except json.JSONDecodeError as e2:
                # If still failing, try to extract individual objects
                try:
                    # Find all individual JSON objects
                    objects = re.findall(r'\{[^{}]*\}', json_text)
                    if objects:
                        test_cases = []
                        for obj_str in objects:
                            try:
                                obj = json.loads(obj_str)
                                test_cases.append(obj)
                            except:
                                continue
                        if test_cases:
                            return test_cases
                except:
                    pass
                
                raise ValueError(f"Failed to parse test cases JSON: {str(e2)}. Raw response: {response_content[:500]}...")

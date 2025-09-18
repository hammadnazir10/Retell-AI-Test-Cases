
from typing import Dict, List, Any
from .prompt_analysis_agent import PromptAnalysisAgent
from .variable_extraction_agent import VariableExtractionAgent
from .test_case_generation_agent import TestCaseGenerationAgent

class TestCaseOrchestrator:
    """Orchestrates the test case generation process using multiple specialized agents"""
    
    def __init__(self):
        """Initialize all agents"""
        self.prompt_analyzer = PromptAnalysisAgent()
        self.variable_extractor = VariableExtractionAgent()
        self.test_case_generator = TestCaseGenerationAgent()
    
    def generate_test_cases(self, prompt: str) -> Dict[str, Any]:
        """
        Generate comprehensive test cases for any AI prompt using agent orchestration
        OPTIMIZED FOR SPEED - reduced sequential API calls
        
        Args:
            prompt: The AI prompt to generate test cases for
            
        Returns:
            Dictionary containing test cases and extracted variables
        """
        try:
            print("🚀 Fast test case generation starting...")
            
            # Step 1: Extract variables (quick regex operation)
            print("� Extracting variables...")
            extracted_variables = self.variable_extractor.get_detected_variables(prompt)
            print(f"Found {len(extracted_variables)} variables: {extracted_variables}")
            
            # Step 2: Generate variable values and test cases in parallel concept
            # (Sequential but optimized for speed)
            if extracted_variables:
                print("🔧 Generating variable values...")
                variable_values = self.variable_extractor.process(prompt)
                print(f"Generated variable values: {variable_values}")
            else:
                variable_values = {}
                print("No variables to generate")
            
            # Step 3: Generate test cases (main operation)
            print("🎯 Generating test cases...")
            test_cases = self.test_case_generator.process(prompt, variable_values, extracted_variables)
            print(f"Generated {len(test_cases)} test cases")
            
            # Skip detailed analysis for speed - use simple prompt analysis
            analysis = "Fast generation mode - detailed analysis skipped for speed"
            
            return {
                "test_cases": test_cases,
                "extracted_variables": extracted_variables,
                "dynamic_variables": variable_values,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"❌ Error in orchestrator: {str(e)}")
            raise e
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get the status of all agents in the system"""
        return {
            "prompt_analyzer": "✅ Ready",
            "variable_extractor": "✅ Ready", 
            "test_case_generator": "✅ Ready",
            "orchestrator": "✅ Ready"
        }

import utils.session
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from agents.orchestrator import TestCaseOrchestrator
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Generic Prompt Test Case Generator", version="1.0.0")
# Initialize the orchestrator
orchestrator = TestCaseOrchestrator()
class TestCaseRequest(BaseModel):
    prompt: str

class TestCase(BaseModel):
    user_prompt: str
    success_criteria: str

class TestCaseResponse(BaseModel):
    test_cases: List[TestCase]
    extracted_variables: List[str]
    dynamic_variables: Dict[str, Any]


@app.post("/generate-test-cases", response_model=TestCaseResponse)
async def generate_test_cases_endpoint(request: TestCaseRequest):
    """Generate comprehensive test cases for ANY AI prompt using agent orchestration"""
    
    try:
        # Use the orchestrator to generate test cases
        result = orchestrator.generate_test_cases(request.prompt)
        
        # Convert to TestCase objects with validation
        test_cases = []
        for i, case in enumerate(result["test_cases"]):
            try:
                # Ensure all required fields exist with defaults
                user_prompt = case.get("user_prompt", f"Test case {i+1}")
                success_criteria = case.get("success_criteria", "Test should pass")
                
                test_cases.append(TestCase(
                    user_prompt=user_prompt,
                    success_criteria=success_criteria
                ))
            except Exception as case_error:
                print(f"Warning: Skipping malformed test case {i+1}: {str(case_error)}")
                continue
        
        return TestCaseResponse(
            test_cases=test_cases,
            extracted_variables=result["extracted_variables"],
            dynamic_variables=result.get("dynamic_variables", {})
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Generic Prompt Test Case Generator API", "version": "1.0.0"}

@app.get("/agent-status")
async def get_agent_status():
    """Get the status of all agents in the system"""
    return orchestrator.get_agent_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
#!/usr/bin/env python3
"""
Streamlit app for generating test cases from AI prompts
"""

import streamlit as st
import json
import requests
from typing import Dict, Any, List
import time

# Configure page
st.set_page_config(
    page_title="AI Prompt Test Case Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .json-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_test_cases(prompt: str) -> Dict[str, Any]:
    """Generate test cases using the FastAPI backend"""
    try:
        response = requests.post(
            "http://localhost:8000/generate-test-cases",
            json={"prompt": prompt},
            timeout=45  # Reduced to 45 seconds for faster feedback
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "detail": response.text
            }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection Error",
            "detail": "Make sure the FastAPI server is running on http://localhost:8000"
        }
    except Exception as e:
        return {
            "error": "Unexpected Error",
            "detail": str(e)
        }

def display_test_case(test_case: Dict[str, Any], index: int):
    """Display a single test case in an expandable section"""
    with st.expander(f"Test Case {index + 1}", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("👤 User Prompt")
            st.write(test_case.get('user_prompt', 'N/A'))
            
        with col2:
            st.subheader("✅ Success Criteria")
            st.write(test_case.get('success_criteria', 'N/A'))

def main():
    # Header
    st.markdown('<h1 class="main-header">🧪 AI Prompt Test Case Generator</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Enter your AI prompt** in the text area
        2. **Click Generate** to create test cases
        3. **View results** in JSON format
        4. **Copy/download** the generated test cases
        
        **Tips:**
        - Use complex prompts with variables like `{{variable_name}}`
        - Include detailed instructions and scenarios
        - The system will automatically detect variables and generate realistic test cases
        
        **⚠️ Processing Time:**
        - Optimized for speed: 30-45 seconds
        - Complex prompts: up to 1 minute
        - System uses GPT-3.5-turbo for faster responses
        - Much faster than previous 5-minute generation!
        """)
        
        st.header("🔧 System Status")
        try:
            response = requests.get("http://localhost:8000/agent-status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                for agent, status_text in status.items():
                    st.write(f"**{agent.replace('_', ' ').title()}**: {status_text}")
            else:
                st.error("❌ Backend not responding")
        except:
            st.error("❌ Backend not available")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Enter Your AI Prompt")
        
        # Text area for prompt input
        prompt = st.text_area(
            "Paste your AI prompt here:",
            height=400,
            placeholder="Enter your AI prompt with variables like {{variable_name}}...",
            help="You can paste complex prompts with newlines, special characters, and variables. The system will handle them properly."
        )
        
        # Generate button
        if st.button("🚀 Generate Test Cases", type="primary", use_container_width=True):
            if not prompt.strip():
                st.error("Please enter a prompt first!")
            else:
                # Create progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔄 Starting fast generation... Expected time: 30-45 seconds.")
                    progress_bar.progress(10)
                    
                    status_text.text("🤖 Analyzing prompt and extracting variables...")
                    progress_bar.progress(30)
                    
                    status_text.text("🎯 Generating 10 test cases (optimized for speed)...")
                    progress_bar.progress(60)
                    
                    result = generate_test_cases(prompt)
                    
                    status_text.text("✅ Processing complete!")
                    progress_bar.progress(100)
                    
                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out after 45 seconds. The system is optimized for speed - if this persists, try a shorter prompt.")
                    return
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    return
                
                if "error" in result:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ {result['error']}")
                    st.write(f"**Details:** {result['detail']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Test cases generated successfully!")
                    st.write(f"**Generated:** {len(result.get('test_cases', []))} test cases")
                    st.write(f"**Variables detected:** {len(result.get('extracted_variables', []))} variables")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store result in session state
                    st.session_state['last_result'] = result
    
    with col2:
        st.header("📊 Quick Stats")
        if 'last_result' in st.session_state and 'error' not in st.session_state['last_result']:
            result = st.session_state['last_result']
            st.metric("Test Cases", len(result.get('test_cases', [])))
            st.metric("Variables", len(result.get('extracted_variables', [])))
            
            st.subheader("🔍 Detected Variables")
            variables = result.get('extracted_variables', [])
            if variables:
                for var in variables[:10]:  # Show first 10
                    st.write(f"• `{var}`")
                if len(variables) > 10:
                    st.write(f"... and {len(variables) - 10} more")
            else:
                st.write("No variables detected")
        else:
            st.info("Generate test cases to see statistics")
    
    # Display results
    if 'last_result' in st.session_state and 'error' not in st.session_state['last_result']:
        result = st.session_state['last_result']
        
        st.header("📋 Generated Test Cases")
        
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📖 Detailed View", "📄 JSON Output", "📥 Download"])
        
        with tab1:
            st.subheader("Individual Test Cases")
            test_cases = result.get('test_cases', [])
            
            if test_cases:
                for i, test_case in enumerate(test_cases):
                    display_test_case(test_case, i)
            else:
                st.warning("No test cases generated")
        
        with tab2:
            st.subheader("Complete JSON Output")
            st.markdown('<div class="json-container">', unsafe_allow_html=True)
            st.json(result)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.subheader("Download Options")
            
            # Download as JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name="test_cases.json",
                mime="application/json",
                use_container_width=True
            )
            
            # Download as CSV (test cases only)
            if result.get('test_cases'):
                import pandas as pd
                df = pd.DataFrame(result['test_cases'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv,
                    file_name="test_cases.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Copy to clipboard
            if st.button("📋 Copy JSON to Clipboard", use_container_width=True):
                st.code(json_str)
                st.success("JSON copied! You can now paste it anywhere.")

if __name__ == "__main__":
    main()

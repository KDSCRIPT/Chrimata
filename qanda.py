import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
# Global variables for caching
_workflow_report = None
_gemini_model = None

def initialize_chatbot(api_key=os.getenv("GEMINI_API_KEY"), report_file_path="reports/workflow_formal_report.txt"):
    """
    Initialize the chatbot components (call this once when server starts)
    
    Args:
        api_key (str): Gemini API key
        report_file_path (str): Path to workflow report file
    
    Returns:
        dict: Initialization status
    """
    global _workflow_report, _gemini_model
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Load workflow report
        try:
            with open(report_file_path, 'r') as file:
                _workflow_report = file.read()
            report_loaded = True
            report_length = len(_workflow_report)
        except FileNotFoundError:
            _workflow_report = ""
            report_loaded = False
            report_length = 0
        
        return {
            "status": "success",
            "message": "Chatbot initialized successfully",
            "report_loaded": report_loaded,
            "report_length": report_length
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize chatbot: {str(e)}"
        }

def get_chatbot_response(user_question, chat_history=None, include_report_context=True):
    """
    Single function to get chatbot response - Perfect for API calls
    
    Args:
        user_question (str): The user's question
        chat_history (list, optional): Previous chat history for context
        include_report_context (bool): Whether to include workflow report context
    
    Returns:
        dict: Response with answer and metadata
    """
    global _workflow_report, _gemini_model
    
    # Initialize if not already done
    if _gemini_model is None:
        init_result = initialize_chatbot()
        if init_result["status"] == "error":
            return {
                "status": "error",
                "message": "Chatbot not initialized",
                "response": None,
                "timestamp": datetime.now().isoformat()
            }
    
    try:
        # Generate context-aware prompt
        prompt = _generate_api_prompt(user_question, chat_history, include_report_context)
        
        # Get response from Gemini
        response = _gemini_model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            return {
                "status": "success",
                "message": "Response generated successfully",
                "response": response.text,
                "question": user_question,
                "timestamp": datetime.now().isoformat(),
                "report_context_used": include_report_context and bool(_workflow_report)
            }
        else:
            return {
                "status": "error",
                "message": "Failed to generate response from AI model",
                "response": None,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating response: {str(e)}",
            "response": None,
            "timestamp": datetime.now().isoformat()
        }

def _generate_api_prompt(user_question, chat_history=None, include_report_context=True):
    """Generate context-aware prompt for API usage"""
    global _workflow_report
    
    # Base prompt
    base_prompt = """You are an AI assistant specialized in workflow analysis, AI architecture, and business process optimization."""
    
    # Add workflow report context if available and requested
    context_section = ""
    if include_report_context and _workflow_report:
        context_section = f"""
WORKFLOW REPORT CONTEXT:
{_workflow_report}

Use this workflow report to answer questions about AI agents, costs, implementation strategies, and technical recommendations.
"""
    
    # Add chat history if provided
    history_section = ""
    if chat_history and isinstance(chat_history, list) and len(chat_history) > 0:
        formatted_history = []
        for entry in chat_history[-3:]:  # Keep last 3 exchanges
            if isinstance(entry, dict) and 'question' in entry and 'response' in entry:
                formatted_history.append(f"Previous Q: {entry['question']}")
                formatted_history.append(f"Previous A: {entry['response'][:150]}...")
        
        if formatted_history:
            history_section = f"""
RECENT CONVERSATION HISTORY:
{chr(10).join(formatted_history)}
"""
    
    # Instructions
    instructions = f"""
{base_prompt}

{context_section}

{history_section}

USER QUESTION: {user_question}

Instructions:
1. Answer the user's question clearly and helpfully
2. If the question relates to the workflow report, reference specific details
3. Be concise but comprehensive
4. Provide actionable insights when possible
5. If you don't have specific information, say so clearly

Please provide your response:
"""
    
    return instructions.strip()

# Utility functions for server integration
def chatbot_health_check():
    """Check if chatbot is properly initialized"""
    global _workflow_report, _gemini_model
    
    return {
        "gemini_model_ready": _gemini_model is not None,
        "workflow_report_loaded": bool(_workflow_report),
        "report_length": len(_workflow_report) if _workflow_report else 0,
        "timestamp": datetime.now().isoformat()
    }

def reload_workflow_report(report_file_path="workflow_formal_report.txt"):
    """Reload the workflow report (useful if report file is updated)"""
    global _workflow_report
    
    try:
        with open(report_file_path, 'r', encoding='utf-8') as file:
            _workflow_report = file.read()
        return {
            "status": "success",
            "message": "Workflow report reloaded successfully",
            "report_length": len(_workflow_report)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to reload report: {str(e)}"
        }

# Example usage functions for testing
def test_chatbot():
    """Test function to verify chatbot works"""
    # Initialize
    init_result = initialize_chatbot()
    print("Initialization:", init_result)
    
    # Test questions
    test_questions = [
        "What is the estimated monthly cost for the workflow?",
        "What AI agents are recommended?",
        "What are the main implementation risks?",
        "Hello, how are you?"
    ]
    
    chat_history = []
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = get_chatbot_response(question, chat_history)
        print(f"Status: {response['status']}")
        if response['status'] == 'success':
            print(f"A: {response['response'][:200]}...")
            # Add to history for context
            chat_history.append({
                'question': question,
                'response': response['response']
            })
        else:
            print(f"Error: {response['message']}")

if __name__ == "__main__":
    # Run test
    test_chatbot()
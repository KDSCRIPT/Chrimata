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
            os.makedirs('reports',exist_ok=True)
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

def get_chatbot_response(user_question, chat_history=None, include_report_context=True, report_context=None):
    global _gemini_model

    if _gemini_model is None:
        init_result = initialize_chatbot()
        if init_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Gemini model not initialized",
                "response": None,
                "timestamp": datetime.now().isoformat()
            }

    try:
        prompt = _generate_api_prompt(
            user_question=user_question,
            chat_history=chat_history,
            include_report_context=include_report_context,
            report_context=report_context
        )

        response = _gemini_model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return {
                "status": "success",
                "message": "Response generated",
                "response": response.text,
                "question": user_question,
                "timestamp": datetime.now().isoformat(),
                "report_context_used": include_report_context and bool(report_context)
            }

        else:
            return {
                "status": "error",
                "message": "Gemini response empty",
                "response": None,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception: {e}",
            "response": None,
            "timestamp": datetime.now().isoformat()
        }

def _generate_api_prompt(user_question, chat_history=None, include_report_context=True, report_context=None):
    """
    Builds a prompt with workflow report and last chat messages to guide Gemini's response.
    
    Args:
        user_question (str): The current user query.
        chat_history (list): List of prior messages (dicts with 'role' and 'content').
        include_report_context (bool): Whether to include the report.
        report_context (str): The actual report content.
    
    Returns:
        str: Final prompt string to send to Gemini.
    """
    base_prompt = (
        "You are an expert AI assistant specialized in analyzing workflow reports, AI cost insights, and implementation strategies."
    )

    # Insert report context if requested and available
    context_section = ""
    if include_report_context and report_context:
        context_section = f"""
WORKFLOW REPORT CONTEXT:
{report_context}
"""

    # Add recent Q&A chat history
    history_section = ""
    if chat_history and isinstance(chat_history, list):
        last_qas = []
        for msg in chat_history[-6:]:  # Max 3 pairs
            role = msg.get("role", "").lower()
            content = msg.get("content", "").strip()
            if role in ["user", "assistant"] and content:
                formatted_role = "User" if role == "user" else "Assistant"
                last_qas.append(f"{formatted_role}: {content}")
        if last_qas:
            history_section = "\n\nRECENT CHAT:\n" + "\n".join(last_qas)

    # Final assembled prompt
    prompt = f"""{base_prompt}

{context_section}

{history_section}

USER QUESTION: {user_question}

INSTRUCTIONS:
- Answer only based on the workflow report and recent conversation.
- Do NOT hallucinate or speculate beyond the report.
- If the report lacks enough detail to answer, clearly say so.
- Be concise, technically accurate, and helpful.

Assistant:"""

    return prompt.strip()


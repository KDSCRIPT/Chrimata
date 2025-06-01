from flask import Flask, request, jsonify
from main import main  # assuming main() is in main.py
from inputs import InputData
from rag_implementation import main1
import google.generativeai as genai
import json
import os
from datetime import datetime

app = Flask(__name__)

# Global variables for chatbot
_workflow_report = None
_gemini_model = None

# Helper to build InputData from JSON
def build_input_data_from_json(data):
    inputs = InputData()
    inputs.industry_model = data.get("industry_model", "")
    inputs.company_size = data.get("company_size", "")
    inputs.goals = data.get("goals", "")
    inputs.top_challenges = data.get("top_challenges", "")
    inputs.tools_platforms = data.get("tools_platforms", "")
    inputs.departments_str = data.get("departments_str", "")
    inputs.team_summaries = data.get("team_summaries", {})
    inputs.task_number = data.get("task_number", 1)
    inputs.optional_bottleneck_clues = data.get("optional_bottleneck_clues", {})
    inputs.roi_inputs = data.get("roi_inputs", {})
    inputs.step7_inputs = data.get("step7_inputs", {})
    return inputs

# Initialize chatbot components
def initialize_chatbot(api_key="AIzaSyBxESJZhk8uUUMzJxJUZou-eu3b5pIrn6A", report_file_path="workflow_formal_report.txt"):
    """Initialize the chatbot components"""
    global _workflow_report, _gemini_model
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Load workflow report
        try:
            with open(report_file_path, 'r', encoding='utf-8') as file:
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
    """Get chatbot response with workflow context"""
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
        prompt = generate_api_prompt(user_question, chat_history, include_report_context)
        
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

def generate_api_prompt(user_question, chat_history=None, include_report_context=True):
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

# Existing workflow endpoint
@app.route('/run-workflow', methods=['POST'])
def run_workflow():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    inputs = build_input_data_from_json(data)
    summary = main(inputs)  # Call your workflow
    formal_report = main1()

    return jsonify(summary)

# New chatbot endpoint
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Chatbot endpoint that uses workflow report context
    
    Expected JSON:
    {
        "question": "What is the estimated cost?",
        "chat_history": [optional previous conversations],
        "include_report_context": true/false (optional, defaults to true)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'question' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'question' in request body"
            }), 400
        
        user_question = data['question']
        chat_history = data.get('chat_history', [])
        include_report_context = data.get('include_report_context', True)
        
        # Get chatbot response
        result = get_chatbot_response(
            user_question=user_question,
            chat_history=chat_history,
            include_report_context=include_report_context
        )
        
        # Return appropriate HTTP status
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}",
            "response": None
        }), 500

# Simple chat endpoint for quick testing
@app.route('/api/chat/simple', methods=['GET'])
def simple_chat_endpoint():
    """
    Simple GET endpoint for testing
    Usage: /api/chat/simple?question=What is the cost?
    """
    question = request.args.get('question')
    
    if not question:
        return jsonify({
            "status": "error",
            "message": "Missing 'question' parameter"
        }), 400
    
    result = get_chatbot_response(question)
    
    if result['status'] == 'success':
        return jsonify(result), 200
    else:
        return jsonify(result), 500

# Chatbot health check
@app.route('/api/chat/health', methods=['GET'])
def chatbot_health():
    """Check if chatbot is working properly"""
    global _workflow_report, _gemini_model
    
    health_status = {
        "gemini_model_ready": _gemini_model is not None,
        "workflow_report_loaded": bool(_workflow_report),
        "report_length": len(_workflow_report) if _workflow_report else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(health_status), 200

# Initialize chatbot when server starts
@app.before_first_request
def startup():
    """Initialize chatbot when server starts"""
    result = initialize_chatbot()
    print(f"Chatbot initialization: {result}")

if __name__ == '__main__':
    app.run(debug=True)
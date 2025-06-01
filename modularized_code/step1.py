from helper import call_gemini_api
# import inputs  # This imports the hardcoded input values

def step1_collect_business_context(inputs):
    """Step 1: Collect high-level business context, infer AI opportunities using Gemini."""
    print("\n--- Step 1: Business Context & AI Opportunity Mapping ---")
    context = {}

    # Load inputs from the inputs.py module
    context['industry_model'] = inputs.industry_model
    context['company_size'] = inputs.company_size
    context['goals'] = inputs.goals.strip()
    context['top_challenges'] = inputs.top_challenges.strip()
    context['tools_platforms'] = inputs.tools_platforms
    context['departments_str'] = inputs.departments_str
    context['departments'] = [d.strip() for d in context['departments_str'].split(',')]

    # Compose a prompt for Gemini to suggest repetitive/manual tasks for each department
    prompt = f"""
You are an AI assistant helping analyze business operations for AI opportunities.
The company works in: {context['industry_model']}
Company size: {context['company_size']}
Main goals: {context['goals']}
Key challenges: {context['top_challenges']}
Tools/platforms in use: {context['tools_platforms']}
Departments: {', '.join(context['departments'])}

For each department, list 3–5 tasks that are highly repetitive, manual, or involve decision-making.
Respond in JSON with department as keys and task lists as values.
"""

    # Use Gemini to infer task lists
    inferred_tasks = call_gemini_api(prompt_text=prompt, instruction_type="department task inference")

    if not inferred_tasks:
        print("⚠️ Failed to get task suggestions from Gemini. Please populate manually in inputs.py or add fallback logic.")
        context['department_tasks'] = {}
    else:
        print("✅ Gemini-suggested tasks for each department:")
        context['department_tasks'] = inferred_tasks

    return context

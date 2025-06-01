from helper import call_gemini_api
# import inputs

def step2_identify_team_specific_workflows(business_context, inputs):
    """Step 2: Streamlined Workflow Discovery using AI Inference"""
    print("\n--- Step 2: Workflow Discovery by Department ---")
    all_tasks = []
    departments = business_context.get('departments', [])

    if not departments:
        print("No departments found. Please complete Step 1 correctly.")
        return []

    for dept in departments:
        print(f"\n🔍 Exploring {dept} Department...")
        team_summary = inputs.team_summaries.get(dept, "").strip()

        if not team_summary:
            print(f"⚠️ No team summary found for {dept} in inputs.py. Skipping.")
            continue

        # --- Gemini Prompt to extract tasks ---
        task_extraction_prompt = (
            f"A user briefly described what their '{dept}' department works on daily:\n"
            f"\"\"\"\n{team_summary}\n\"\"\"\n\n"
            "Based on this, extract up to 3 recurring or critical workflows.\n"
            "Return each as a JSON object with the following:\n"
            "- task_name: Short name of the task\n"
            "- frequency: Daily, Weekly, Monthly, As needed, Other\n"
            "- characteristics: Is it manual, repetitive, or prone to delay?\n"
            "- tools_used: Mention tools involved if known\n"
            "- dependencies: Other departments involved, or 'None'"
        )

        schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "task_name": {"type": "STRING"},
                    "frequency": {"type": "STRING", "enum": ["Daily", "Weekly", "Monthly", "As needed", "Other"]},
                    "characteristics": {"type": "STRING"},
                    "tools_used": {"type": "STRING"},
                    "dependencies": {"type": "STRING"}
                },
                "required": ["task_name", "frequency", "characteristics", "tools_used", "dependencies"]
            }
        }

        extracted_tasks = call_gemini_api(task_extraction_prompt, schema=schema, instruction_type=f"Task inference for {dept}")

        if not extracted_tasks:
            print(f"⚠️ Couldn’t infer structured tasks for {dept}.")
            continue

        for task_data in extracted_tasks:
            task_data['team'] = dept

            ai_suggestion_prompt = (
                f"Suggest an AI/automation solution to improve the task:\n"
                f"- Task: {task_data['task_name']}\n"
                f"- Frequency: {task_data['frequency']}\n"
                f"- Characteristics: {task_data['characteristics']}\n"
                f"- Tools Used: {task_data['tools_used']}\n"
                f"- Dependencies: {task_data['dependencies']}\n\n"
                "Return a JSON object with:\n"
                "- ai_solution_summary: 1-line idea\n"
                "- ai_tools_or_techniques: e.g., RPA, LLMs, ML Forecasting\n"
                "- expected_impact: Low / Medium / High\n"
                "- notes: Optional assumptions or context"
            )

            insight_schema = {
                "type": "OBJECT",
                "properties": {
                    "ai_solution_summary": {"type": "STRING"},
                    "ai_tools_or_techniques": {"type": "STRING"},
                    "expected_impact": {"type": "STRING", "enum": ["Low", "Medium", "High"]},
                    "notes": {"type": "STRING"}
                },
                "required": ["ai_solution_summary", "ai_tools_or_techniques", "expected_impact"]
            }

            ai_insight = call_gemini_api(ai_suggestion_prompt, schema=insight_schema, instruction_type=f"AI suggestion for {task_data['task_name']}")
            task_data['ai_insights'] = ai_insight or {}

            all_tasks.append(task_data)
            print(f"✅ {dept} task identified: {task_data['task_name']}")

    if not all_tasks:
        print("No tasks identified. Consider retrying with better descriptions.")
        return None

    print("\n📋 Summary of Identified Tasks:")
    for i, task in enumerate(all_tasks, 1):
        print(f"{i}. [{task['team']}] {task['task_name']} ({task['frequency']})")
        insights = task.get('ai_insights', {})
        if insights:
            print(f"   🔍 {insights.get('ai_solution_summary')} (Impact: {insights.get('expected_impact')})")

    # You can remove this if no task selection is needed
    return all_tasks

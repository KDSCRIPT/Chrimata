from helper import call_gemini_api
# from inputs import roi_inputs

def step6_roi_feasibility_and_implementation(selected_task, business_context, inputs):
    
    """Step 6: ROI, Feasibility & AI Readiness & Implementation Planning (Loads inputs from input.py)"""
    print(f"\n--- Step 6: ROI, Feasibility & Implementation Planning for Task: {selected_task.get('task_name')} ---")

    # Load all predefined user inputs from input.py
    selected_task.update(inputs.roi_inputs)

    # --- AI-Assisted Inference ---
    print("\n🤖 Inferring ROI-related metrics and AI-fit details using Gemini...")

    inference_prompt = (
        f"Task: {selected_task.get('task_name')}\n"
        f"Business Context: {business_context}\n"
        f"Monthly Task Volume: {selected_task['tasks_per_month']}\n"
        f"Average Time per Task (minutes): {selected_task['current_time_per_task_minutes']}\n"
        f"People Involved per Task: {selected_task['people_involved_count']}\n"
        f"Hourly Cost per Person: {selected_task['avg_hourly_cost_per_employee']}\n\n"
        "Infer and return the following as a JSON:\n"
        "- estimated_time_saved_percent\n"
        "- other_quantitative_benefits\n"
        "- qualitative_benefits\n"
        "- estimated_investment_cost\n"
        "- roi_rating_and_justification\n"
        "- ai_capability_type\n"
        "- ai_integration_method\n"
        "- ai_monitoring_needs\n"
        "- change_management_needs"
    )

    inference_schema = {
        "type": "OBJECT",
        "properties": {
            "estimated_time_saved_percent": {"type": "NUMBER"},
            "other_quantitative_benefits": {"type": "STRING"},
            "qualitative_benefits": {"type": "STRING"},
            "estimated_investment_cost": {"type": "NUMBER"},
            "roi_rating_and_justification": {"type": "STRING"},
            "ai_capability_type": {"type": "STRING"},
            "ai_integration_method": {"type": "STRING"},
            "ai_monitoring_needs": {"type": "STRING"},
            "change_management_needs": {"type": "STRING"},
        },
        "required": list([
            "estimated_time_saved_percent",
            "other_quantitative_benefits",
            "qualitative_benefits",
            "estimated_investment_cost",
            "roi_rating_and_justification",
            "ai_capability_type",
            "ai_integration_method",
            "ai_monitoring_needs",
            "change_management_needs"
        ])
    }

    ai_inferred = call_gemini_api(prompt_text=inference_prompt, schema=inference_schema)
    selected_task.update(ai_inferred)

    # --- Calculations ---
    time_saved_per_task = (
        selected_task['current_time_per_task_minutes'] *
        selected_task['people_involved_count'] *
        (selected_task['estimated_time_saved_percent'] / 100)
    )
    selected_task['calculated_time_saved_per_task_minutes'] = round(time_saved_per_task, 2)

    total_time_saved_hours = (time_saved_per_task * selected_task['tasks_per_month']) / 60
    selected_task['calculated_total_time_saved_per_month_hours'] = round(total_time_saved_hours, 2)

    cost_saving = total_time_saved_hours * selected_task['avg_hourly_cost_per_employee']
    selected_task['calculated_potential_cost_saving_per_month'] = round(cost_saving, 2)

    if cost_saving > 0 and selected_task['estimated_investment_cost'] > 0:
        selected_task['estimated_payback_period_months'] = round(
            selected_task['estimated_investment_cost'] / cost_saving, 1
        )
    else:
        selected_task['estimated_payback_period_months'] = "N/A"

    # --- AI Feasibility Analysis ---
    print("\n--- AI Readiness & Feasibility Analysis (Gemini) ---")
    feasibility_prompt = (
        f"Task: {selected_task.get('task_name')}\n"
        f"Business Context: {business_context}\n"
        f"Financials:\n"
        f"  Monthly cost saving: {selected_task['calculated_potential_cost_saving_per_month']}\n"
        f"  Investment: {selected_task['estimated_investment_cost']}\n"
        f"  Payback Period: {selected_task['estimated_payback_period_months']} months\n"
        f"  Qualitative Benefits: {selected_task['qualitative_benefits']}\n"
        f"  Quantitative Benefits: {selected_task['other_quantitative_benefits']}\n\n"
        f"Implementation:\n"
        f"  Feasibility: {selected_task['technical_feasibility_rating']}\n"
        f"  Notes: {selected_task['technical_feasibility_notes']}\n"
        f"  Skills/Resources: {selected_task['required_skills_resources']}\n"
        f"  Timeline: {selected_task['estimated_implementation_timeline']}\n\n"
        f"AI Insight:\n"
        f"  Capability Type: {selected_task['ai_capability_type']}\n"
        f"  Integration: {selected_task['ai_integration_method']}\n"
        f"  Monitoring: {selected_task['ai_monitoring_needs']}\n"
        f"  Change Mgmt: {selected_task['change_management_needs']}\n\n"
        f"Assess AI feasibility, risks, and fit. Return JSON with:\n"
        "- ai_solution_fit_rating (High, Medium, Low)\n"
        "- ai_model_type_recommended (e.g., LLM, Classifier, RPA)\n"
        "- adoption_risk_level (High, Medium, Low)\n"
        "- deployment_complexity_notes\n"
        "- scaling_leverage (High, Medium, Low)\n"
        "- summary_recommendation"
    )

    feasibility_schema = {
        "type": "OBJECT",
        "properties": {
            "ai_solution_fit_rating": {"type": "STRING", "enum": ["High", "Medium", "Low"]},
            "ai_model_type_recommended": {"type": "STRING"},
            "adoption_risk_level": {"type": "STRING", "enum": ["High", "Medium", "Low"]},
            "deployment_complexity_notes": {"type": "STRING"},
            "scaling_leverage": {"type": "STRING", "enum": ["High", "Medium", "Low"]},
            "summary_recommendation": {"type": "STRING"},
        },
        "required": [
            "ai_solution_fit_rating",
            "ai_model_type_recommended",
            "adoption_risk_level",
            "deployment_complexity_notes",
            "scaling_leverage",
            "summary_recommendation"
        ]
    }

    ai_analysis = call_gemini_api(prompt_text=feasibility_prompt, schema=feasibility_schema)
    selected_task['ai_feasibility_analysis'] = ai_analysis

    print(f"\n🎯 Gemini AI Analysis Summary:")
    print(f"  ✅ AI Fit: {ai_analysis.get('ai_solution_fit_rating')}")
    print(f"  🧠 Recommended Model: {ai_analysis.get('ai_model_type_recommended')}")
    print(f"  ⚠️ Adoption Risk: {ai_analysis.get('adoption_risk_level')}")
    print(f"  ⚙️ Deployment Notes: {ai_analysis.get('deployment_complexity_notes')}")
    print(f"  📈 Scalability: {ai_analysis.get('scaling_leverage')}")
    print(f"  💡 Summary:\n    {ai_analysis.get('summary_recommendation')}\n")

    return selected_task

from helper import call_gemini_api

def monitoring_feedback_integration_strategy(selected_task, business_context, inputs):
    print(f"\n--- Step 7: Monitoring, Feedback, Integration & Strategic Alignment for Task: {selected_task.get('task_name')} ---")

    # Use values from inputs["implementation_inputs"]
    implementation = inputs.get("implementation_inputs", {})

    selected_task['operational_ownership'] = implementation.get("operational_ownership", "")
    selected_task['sla_and_uptime_requirements'] = implementation.get("sla_and_uptime_requirements", "")
    selected_task['disaster_recovery_and_rollback'] = implementation.get("disaster_recovery_and_rollback", "")
    selected_task['user_training_and_communication'] = implementation.get("user_training_and_communication", "")
    selected_task['change_management_activities'] = implementation.get("change_management_activities", "")
    selected_task['recommended_next_steps'] = implementation.get("recommended_next_steps", "")

    # AI Inference Prompt
    ai_prompt = (
        f"Task details: {selected_task.get('task_name')}\n"
        f"Business goals: {business_context.get('goals')}\n"
        f"Context and previous AI initiatives: {business_context.get('ai_initiatives', 'None')}\n\n"
        "Based on this, infer appropriate AI-specific monitoring metrics, success KPIs, monitoring frequency, tools & alerts, "
        "feedback loop design, retraining strategy, data sensitivity & compliance measures, explainability & audit plans, "
        "risk mitigation and ethical fairness considerations, and how this aligns with strategic goals. "
        "Return a JSON with these fields."
    )

    ai_schema = {
        "type": "OBJECT",
        "properties": {
            "key_success_metrics_kpis": {"type": "STRING"},
            "monitoring_frequency": {"type": "STRING"},
            "monitoring_tools_and_alerts": {"type": "STRING"},
            "feedback_loop_description": {"type": "STRING"},
            "retraining_schedule_triggers": {"type": "STRING"},
            "data_sensitivity_and_governance": {"type": "STRING"},
            "audit_and_explainability": {"type": "STRING"},
            "risk_mitigation_strategies": {"type": "STRING"},
            "ethical_and_fairness_considerations": {"type": "STRING"},
            "strategic_goal_alignment": {"type": "STRING"},
            "business_outcome_targets": {"type": "STRING"},
            "addressing_past_failures": {"type": "STRING"},
        },
        "required": [
            "key_success_metrics_kpis", "monitoring_frequency", "monitoring_tools_and_alerts",
            "feedback_loop_description", "retraining_schedule_triggers", "data_sensitivity_and_governance",
            "audit_and_explainability", "risk_mitigation_strategies", "ethical_and_fairness_considerations",
            "strategic_goal_alignment", "business_outcome_targets", "addressing_past_failures"
        ]
    }

    ai_inferred = call_gemini_api(prompt_text=ai_prompt, schema=ai_schema)

    # Merge AI inferred results into selected_task
    if ai_inferred:
        selected_task.update(ai_inferred)
        print("\n🤖 AI-inferred monitoring, feedback, and strategic details have been added.")
    else:
        print("⚠️ AI inference failed. No updates made.")

    return selected_task

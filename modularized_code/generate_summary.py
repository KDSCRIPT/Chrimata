import json

def generate_final_summary(business_context, analyzed_task):
    """Generates the final JSON summary without emojis and without using safe_field()"""

    print("\n--- Generating Final Workflow Summary (Industrialist Focused) ---")

    def get(field, source='user'):
        v = analyzed_task.get(field)
        return v if v not in [None, "", " "] else "N/A"

    summary = {
        "executive_summary": {
            "task_being_addressed": f"{get('task_name')} in {get('team')} department.",
            "core_problem_bottleneck": f"{get('bottleneck_category')} - {get('bottleneck_reasoning')}",
            "proposed_ai_solution_type": get('suggested_tool_type', 'ai'),
            "key_expected_benefits": (
                f"Estimated monthly cost saving of ${analyzed_task.get('calculated_potential_cost_saving_per_month', 0):.2f}, "
                f"{analyzed_task.get('calculated_total_time_saved_per_month_hours', 0)} hours saved/month. "
                f"Qualitative: {get('qualitative_benefits')}"
            ),
            "estimated_investment": f"${analyzed_task.get('estimated_investment_cost', 0):.2f}",
            "estimated_payback_period": f"{analyzed_task.get('estimated_payback_period_months', 'N/A')} months",
            "overall_roi_potential": get('roi_potential_rating_justification', 'ai'),
            "recommended_next_step_primary": (
                get('recommended_next_steps', 'user').split(',')[0].strip()
                if get('recommended_next_steps', 'user') != "N/A" else "Further detailed planning"
            )
        },
        "business_context_overview": {
            "industry_model": business_context.get('industry_model', 'N/A'),
            "primary_business_goals": business_context.get('goals', 'N/A'),
            "key_departments_involved": business_context.get('departments', 'N/A'),
            "current_tools_platforms_in_use": business_context.get('tools_platforms', 'N/A'),
            "history_with_ai_automation": business_context.get('ai_initiatives', 'N/A')
        },
        "workflow_analysis_details": {
            "department": get('team'),
            "task_name": get('task_name'),
            "task_frequency": get('frequency'),
            "current_task_characteristics": get('characteristics'),
            "current_tools_used_for_task": get('tools_used'),
            "inter_departmental_dependencies": get('dependencies'),
            "identified_bottleneck": {
                "category": get('bottleneck_category'),
                "detailed_reasoning": get('bottleneck_reasoning'),
                "cost_of_inaction_or_error": get('cost_of_inaction_or_error')
            }
        },
        "proposed_ai_solution": {
            "matched_ai_primitives": get('ai_categories', 'ai'),
            "primitive_application_notes": get('ai_primitive_application_notes', 'ai'),
            "suggested_ai_tool_platform": get('suggested_tool_type', 'ai'),
            "build_vs_buy_initial_assessment": get('build_vs_buy_consideration', 'ai'),
            "human_in_the_loop_requirement": get('human_in_loop_summary', 'ai'),
            "human_oversight_details": {
                "final_review_needed": get('human_review_needed', 'ai'),
                "ai_as_assistant": get('ai_assist_not_replace', 'ai'),
                "human_feedback_for_improvement": get('feedback_improves_ai', 'ai')
            },
            "data_sensitivity_and_security_notes": get('data_sensitivity_and_governance'),
            "ethical_considerations_and_fairness_checks": get('ethical_and_fairness_considerations'),
            "explainability_and_transparency_measures": get('audit_and_explainability'),
            "sla_and_operational_requirements": get('sla_and_uptime_requirements'),
            "disaster_recovery_plans": get('disaster_recovery_and_rollback')
        },
        "financial_projections_and_roi": {
            "tasks_instances_per_month": get('tasks_per_month', 'ai'),
            "current_time_per_task_minutes": get('current_time_per_task_minutes', 'ai'),
            "people_involved_per_task_instance": get('people_involved_count', 'ai'),
            "average_employee_hourly_cost": get('avg_hourly_cost_per_employee', 'ai'),
            "estimated_time_saved_per_task_percentage": get('estimated_time_saved_per_task_percent', 'ai'),
            "calculated_time_saved_per_task_minutes": get('calculated_time_saved_per_task_minutes', 'ai'),
            "calculated_total_time_saved_per_month_hours": get('calculated_total_time_saved_per_month_hours', 'ai'),
            "calculated_potential_direct_cost_saving_per_month": get('calculated_potential_cost_saving_per_month', 'ai'),
            "other_quantitative_benefits_expected": get('other_quantitative_benefits'),
            "key_qualitative_benefits_expected": get('qualitative_benefits'),
            "estimated_initial_investment_cost": get('estimated_investment_cost', 'ai'),
            "estimated_simple_payback_period_months": get('estimated_payback_period_months', 'ai'),
            "overall_roi_potential_rating_and_justification": get('roi_potential_rating_justification', 'ai')
        },
        "implementation_plan_and_feasibility": {
            "technical_feasibility_rating": get('technical_feasibility_rating', 'ai'),
            "technical_feasibility_notes_and_challenges": get('technical_feasibility_notes', 'ai'),
            "required_skills_and_resources": get('required_skills_resources', 'ai'),
            "estimated_implementation_timeline": get('estimated_implementation_timeline', 'ai'),
            "key_integration_points_with_current_systems": get('integration_points_systems', 'ai'),
            "scalability_requirements_and_considerations": get('scalability_considerations', 'ai')
        },
        "monitoring_governance_and_improvement": {
            "key_success_metrics_and_kpis_with_targets": get('key_success_metrics_kpis'),
            "monitoring_frequency_and_tools": f"{get('monitoring_frequency')} | {get('monitoring_tools_and_alerts')}",
            "feedback_loop_for_continuous_improvement": get('feedback_loop_description'),
            "retraining_schedule_and_triggers": get('retraining_schedule_triggers'),
            "operational_ownership_and_roles": get('operational_ownership'),
            "training_and_change_management": f"{get('user_training_and_communication')} | {get('change_management_activities')}"
        },
        "risk_mitigation_and_change_management": {
            "addressing_lessons_from_past_initiatives": get('addressing_past_failures'),
            "risk_mitigation_measures": get('risk_mitigation_strategies'),
            "ethical_monitoring_and_fairness": get('ethical_and_fairness_considerations'),
            "initial_change_management_strategy": get('change_management_activities')
        },
        "strategic_alignment_and_next_steps": {
            "contribution_to_key_business_goals": get('strategic_goal_alignment'),
            "recommended_actionable_next_steps": [
                s.strip() for s in
                (get('recommended_next_steps', 'user') if get('recommended_next_steps', 'user') != "N/A" else "").split(',')
                if s.strip()
            ]
        }
    }

    summary_json = json.dumps(summary, indent=2, default=str)
    print("\n✅ Workflow Discovery Summary (JSON - Industrialist Focused):")

    filename = f"industrial_workflow_summary.json"
    try:
        with open(filename, 'w') as f:
            f.write(summary_json)
        print(f"\n📄 Summary saved to {filename}")
    except IOError as e:
        print(f"❌ Error saving summary to file: {e}")

    return summary_json

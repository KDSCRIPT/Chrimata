# inputs.py

class InputData:
    def __init__(self):
        self.industry_model = "Retail - B2C"
        self.company_size = "200 employees"
        self.goals = """
- Increase online sales by 20%
- Improve customer retention
- Expand to two new markets
"""

        self.top_challenges = """
- High cart abandonment rate
- Manual inventory tracking
- Delayed customer support response
"""

        self.tools_platforms = "Shopify, Salesforce, Slack, Jira"
        self.departments_str = "Sales, Marketing, Customer Support, IT, Logistics"

        self.team_summaries = {
            "Sales": """
The Sales team handles lead qualification, cold outreach, and client demos. 
They log activity in Salesforce and follow up with prospects daily.
""",
            "Marketing": """
Marketing runs email campaigns, manages social media, creates content, and tracks analytics weekly.
They use HubSpot and Google Analytics.
""",
            "Customer Support": """
Customer Support resolves tickets, answers live chats, and escalates technical issues to engineering.
They primarily use Zendesk and Slack.
""",
            "IT": """
IT supports employee onboarding, manages internal tools, handles outages and device issues.
Jira and internal dashboards are used often.
""",
            "Logistics": """
The Logistics team tracks shipments, manages warehouse inventory, and handles vendor coordination.
They rely on spreadsheets and ERP systems.
"""
        }
        self.task_number = 1
        self.optional_bottleneck_clues = {
            "Lead Qualification": "Sometimes reps don't update lead statuses on time, causing follow-up delays.",
            "Campaign Performance Tracking": "",
            "Customer Ticket Escalation": "Support delays occur due to waiting on engineering for fixes.",
            "Tool Onboarding": "",
            "Inventory Reconciliation": "Manual data entry causes discrepancies."
        }

        self.roi_inputs = {
            "tasks_per_month": 120,
            "current_time_per_task_minutes": 15.0,
            "people_involved_count": 2,
            "avg_hourly_cost_per_employee": 50.0,
            "technical_feasibility_rating": "Medium",
            "technical_feasibility_notes": "Needs integration with legacy system.",
            "required_skills_resources": "ML developers, data engineers, SME",
            "estimated_implementation_timeline": "PoC: 1 month, Full: 4 months"
        }

        self.step7_inputs = {
            "operational_ownership": "AI Operations Team",
            "sla_and_uptime_requirements": "99.9% uptime, SLA < 1 hour response",
            "disaster_recovery_and_rollback": """Rollback to last stable version using container snapshots. 
Redundant cloud deployment with failover.""",
            "user_training_and_communication": """Onboarding sessions, training videos, user handbook, and a helpdesk system.""",
            "change_management_activities": """Regular newsletters, leadership buy-in, pilot programs, and anonymous feedback forms.""",
            "recommended_next_steps": """Finalize PoC scope, allocate budget, assign cross-functional team, initiate vendor engagement."""
        }

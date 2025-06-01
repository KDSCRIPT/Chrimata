import json
import sqlite3
import numpy as np
import faiss
import google.generativeai as genai
import re
import time
import logging
import agentops
from agentops.sdk.decorators import session, agent, operation

# -----------------------------
# AgentOps and Logging Setup
# -----------------------------
agentops_api_key = "dd92331e-8838-4f06-969c-b4dfe3f2029b"  # Replace with your AgentOps API key
agentops.init(agentops_api_key)

logging.basicConfig(
    filename='gemini_requests.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

REQUEST_SIZE_THRESHOLD = 10240  # 10KB
LATENCY_THRESHOLD = 2.0         # 2 seconds

# Setup Gemini API
genai.configure(api_key="AIzaSyBxESJZhk8uUUMzJxJUZou-eu3b5pIrn6A")  # Replace with your Gemini API key
chat_model = genai.GenerativeModel("gemini-2.0-flash")

# -----------------------------
# Complex Workflow Input Examples
# -----------------------------
with open('C:\VIT\\100xengg\modularized_code\industrial_workflow_summary.json') as f:
    data = json.load(f)
COMPLEX_WORKFLOW_EXAMPLES = {
    "content_creation_pipeline": data,
    
    "ecommerce_automation": data,
    
    "research_development": data
}

# -----------------------------
# Enhanced Monitoring Wrapper
# -----------------------------
@operation
def monitored_generate_content(prompt, context="general"):
    start_time = time.time()
    response = None
    try:
        response = chat_model.generate_content(prompt)
        end_time = time.time()

        request_size = len(prompt)
        response_size = len(response.text) if hasattr(response, "text") else 0
        latency = end_time - start_time

        logging.info(f"Context: {context} | Request Size: {request_size} | Response Size: {response_size} | Latency: {latency:.2f}s")

        if request_size > REQUEST_SIZE_THRESHOLD:
            print(f"⚠️ Request size exceeded 10KB: {request_size} bytes for {context}")

        if latency > LATENCY_THRESHOLD:
            print(f"⚠️ Latency exceeded 2 seconds: {latency:.2f}s for {context}")

        return response
    except Exception as e:
        logging.error(f"Error in {context}: {str(e)}")
        raise

# -----------------------------
# Enhanced Agent Matching with Workflow Analysis
# -----------------------------
@operation
def analyze_workflow_requirements(workflow_description):
    """Extract detailed requirements from complex workflow description"""
    prompt = f"""
    You are an AI workflow architect. Analyze the following complex workflow description and extract structured requirements.

    Workflow Description:
    {workflow_description}

    Extract and return a JSON object with the following structure:
    {{
        "workflow_name": "string",
        "business_context": "string",
        "monthly_budget": "extract budget amount as number",
        "monthly_volume": "extract volume metrics",
        "key_steps": [
            {{
                "step_name": "string",
                "description": "string",
                "ai_capabilities_needed": ["list of specific AI capabilities"],
                "estimated_volume": "number or range",
                "priority": "high/medium/low"
            }}
        ],
        "technical_requirements": {{
            "latency_requirements": "string",
            "integration_needs": ["list of integrations"],
            "scalability_needs": "string",
            "compliance_requirements": ["list of compliance needs"]
        }},
        "success_metrics": ["list of success metrics"],
        "quality_standards": ["list of quality requirements"]
    }}

    Be specific and detailed in your analysis. Extract numbers where possible.
    """
    
    response = monitored_generate_content(prompt, context="workflow_analysis")
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse workflow analysis JSON")
        return None

@operation
def find_agents_for_workflow_step(step_requirements, all_agents):
    """Find best matching agents for a specific workflow step"""
    prompt = f"""
    You are an AI agent matching specialist. Find the best AI agents from the provided list for the following workflow step.

    Workflow Step Requirements:
    Step Name: {step_requirements['step_name']}
    Description: {step_requirements['description']}
    AI Capabilities Needed: {step_requirements['ai_capabilities_needed']}
    Estimated Volume: {step_requirements.get('estimated_volume', 'Not specified')}
    Priority: {step_requirements['priority']}

    Available AI Agents:
    {json.dumps(all_agents, indent=2)}

    Analyze each agent and return a JSON array of the top 3 most suitable agents with this structure:
    [
        {{
            "agent_name": "string",
            "suitability_score": "number 1-10",
            "reasons": ["list of specific reasons why this agent fits"],
            "estimated_usage": "how this agent would be used in this step",
            "potential_limitations": ["any limitations or concerns"]
        }}
    ]

    Consider use cases, pricing, latency, integration capabilities, and quality fit.
    """
    
    response = monitored_generate_content(prompt, context="agent_matching")
    if not response:
        return []
    
    try:
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse agent matching JSON")
        return []

@operation
def calculate_workflow_costs(workflow_analysis, agent_assignments):
    """Calculate detailed costs for the entire workflow"""
    prompt = f"""
    You are a cost analysis expert for AI workflows. Calculate detailed costs for the following workflow.

    Workflow Analysis:
    {json.dumps(workflow_analysis, indent=2)}

    Agent Assignments:
    {json.dumps(agent_assignments, indent=2)}

    Perform detailed cost calculations and return a JSON object with this structure:
    {{
        "total_monthly_cost": "number",
        "cost_breakdown": [
            {{
                "step_name": "string",
                "agents_used": ["list of agent names"],
                "input_costs": "number",
                "output_costs": "number",
                "step_total": "number",
                "volume_assumptions": "string explaining calculations"
            }}
        ],
        "cost_per_operation": "number",
        "budget_analysis": {{
            "budget_available": "number from workflow",
            "budget_utilization": "percentage",
            "cost_optimization_suggestions": ["list of suggestions"]
        }},
        "scaling_projections": {{
            "at_2x_volume": "number",
            "at_5x_volume": "number",
            "at_10x_volume": "number"
        }}
    }}

    Be specific with your calculations. Show your work for volume-based pricing.
    Extract pricing information from the agent data (InputPrice, OutputPrice fields).
    Consider that pricing might be in various formats (per token, per request, per minute, etc.).
    """
    
    response = monitored_generate_content(prompt, context="cost_calculation")
    if not response:
        return None
    
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse cost calculation JSON")
        return None

@operation
def generate_workflow_implementation_plan(workflow_analysis, agent_assignments, cost_analysis):
    """Generate a detailed implementation plan"""
    prompt = f"""
    You are a workflow implementation specialist. Create a detailed implementation plan.

    Workflow Analysis: {json.dumps(workflow_analysis, indent=2)}
    Agent Assignments: {json.dumps(agent_assignments, indent=2)}
    Cost Analysis: {json.dumps(cost_analysis, indent=2)}

    Create a comprehensive implementation plan with:
    1. Architecture overview
    2. Integration sequence
    3. Timeline and milestones
    4. Risk assessment
    5. Performance monitoring plan
    6. Optimization opportunities

    Return a detailed markdown document.
    """
    
    response = monitored_generate_content(prompt, context="implementation_planning")
    return response.text if response else "Implementation plan generation failed."

# -----------------------------
# Main Workflow Processing Function
# -----------------------------
@operation
def process_complex_workflow(workflow_description):
    """Process a complex workflow description and return complete solution"""
    
    print("🔍 Step 1: Analyzing workflow requirements...")
    workflow_analysis = analyze_workflow_requirements(workflow_description)
    if not workflow_analysis:
        print("❌ Failed to analyze workflow requirements")
        return None
    
    print("📊 Step 2: Loading available agents from database...")
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents")
    rows = cursor.fetchall()
    conn.close()
    
    all_agents = []
    for row in rows:
        agent_info = {
            "Name": row[0],
            "Provider": row[1],
            "UseCase": row[2],
            "Category": row[3],
            "InputPrice": row[4],
            "OutputPrice": row[5],
            "Integration": row[6],
            "FreeTier": row[7],
            "Latency": row[8],
            "Website": row[9],
            "Alternatives": row[10]
        }
        all_agents.append(agent_info)
    
    print("🎯 Step 3: Matching agents to workflow steps...")
    agent_assignments = {}
    for step in workflow_analysis.get('key_steps', []):
        print(f"   Processing step: {step['step_name']}")
        matched_agents = find_agents_for_workflow_step(step, all_agents)
        agent_assignments[step['step_name']] = matched_agents
        time.sleep(1)  # Rate limiting
    
    print("💰 Step 4: Calculating costs...")
    cost_analysis = calculate_workflow_costs(workflow_analysis, agent_assignments)
    
    print("📋 Step 5: Generating implementation plan...")
    implementation_plan = generate_workflow_implementation_plan(
        workflow_analysis, agent_assignments, cost_analysis
    )
    
    return {
        "workflow_analysis": workflow_analysis,
        "agent_assignments": agent_assignments,
        "cost_analysis": cost_analysis,
        "implementation_plan": implementation_plan
    }

# -----------------------------
# Original Functions (Restored)
# -----------------------------
@operation
def enrich_agent_data(agent):
    prompt = f"""
You are an AI product expert.

Take the following basic AI tool data and enhance each field with more clarity and detail. Make sure to elaborate the 'Use Case' by listing specific tasks. Also, make each field useful for cost estimation and quality assessment.

Example data:
Name: {agent['Name']}
Provider: {agent['Provider']}
Use Case: {agent['UseCase']}
Category: {agent['Category']}
Input Price: {agent['InputPrice']}
Output Price: {agent['OutputPrice']}
Integration: {agent['Integration']}
Free Tier: {agent['FreeTier']}
Latency: {agent['Latency']}
Website: {agent['Website']}
Alternatives: {agent['Alternatives']}
This is a JSON object with keys:
Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives.
Return updated fields in JSON format with the same keys.
No need to give anything else other than the JSON object.
"""

    response = monitored_generate_content(prompt, context="data_enrichment")
    if not response:
        return agent  # fallback

    print(f"\n📨 Gemini raw response:\n{response.text}")

    pattern = r'"?(Name|Provider|UseCase|Category|InputPrice|OutputPrice|Integration|FreeTier|Latency|Website|Alternatives)"?\s*:\s*[""]?(.+?)[""]?(?:,|\n|$)'
    matches = re.findall(pattern, response.text, re.DOTALL)

    enriched = {key: agent.get(key, "") for key in agent}
    for key, value in matches:
        enriched[key.strip()] = value.strip().rstrip(',')

    return enriched

@operation
def enrich_all_agents():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE agents ADD COLUMN Enriched BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    cursor.execute("SELECT * FROM agents WHERE Enriched = 0")
    rows = cursor.fetchall()
    enriched_rows = []
    for row in rows:
        agent = {
            "Name": row[0],
            "Provider": row[1],
            "UseCase": row[2],
            "Category": row[3],
            "InputPrice": row[4],
            "OutputPrice": row[5],
            "Integration": row[6],
            "FreeTier": row[7],
            "Latency": row[8],
            "Website": row[9],
            "Alternatives": row[10]
        }

        enriched = enrich_agent_data(agent)
        enriched_rows.append(tuple([
            enriched["Name"], enriched["Provider"], enriched["UseCase"], enriched["Category"],
            enriched["InputPrice"], enriched["OutputPrice"], enriched["Integration"],
            enriched["FreeTier"], enriched["Latency"], enriched["Website"], enriched["Alternatives"], 1
        ]))

    cursor.executemany('''
        INSERT OR REPLACE INTO agents 
        (Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives, Enriched)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', enriched_rows)

    conn.commit()
    conn.close()
    print("✅ Enriched only new agents and marked them in the DB.")
    return True

@operation
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

@operation
def build_faiss_index():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, UseCase, Category FROM agents")
    rows = cursor.fetchall()
    conn.close()

    embeddings = []
    agent_map = {}

    for i, (name, use_case, category) in enumerate(rows):
        combined_text = f"{use_case}. Category: {category}"
        embedding = get_embedding(combined_text)
        embeddings.append(embedding)
        agent_map[i] = name

    vectors = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vectors)

    faiss.write_index(index, "agents_faiss.index")
    with open("index_map.json", "w") as f:
        json.dump(agent_map, f)

    print("✅ FAISS index built and saved.")

# -----------------------------
# Output Generation Functions
# -----------------------------
@operation
def generate_ai_selection_summary(result):
    """Generate a focused summary of AI agents to be used"""
    prompt = f"""
You are an AI architecture consultant. Based on the workflow analysis, create a focused summary document listing all AI agents that will be used in this workflow.

Workflow Analysis Data:
{json.dumps(result, indent=2)}

Create a structured summary with:

1. AI AGENTS SELECTION OVERVIEW
   - Total number of AI agents recommended
   - Categories of AI tools being used
   - Key selection criteria applied

2. DETAILED AI AGENT LIST
   For each selected AI agent, provide:
   - Agent Name and Provider
   - Primary Use Case in this workflow
   - Expected Usage Volume
   - Cost per operation/month
   - Key capabilities being leveraged
   - Integration requirements

3. ARCHITECTURE DECISION RATIONALE
   - Why these specific AI agents were chosen
   - How they work together in the workflow
   - Alternative options considered and rejected
   - Technical compatibility considerations

4. FINANCIAL BREAKDOWN BY AI AGENT
   - Individual cost contribution
   - Volume-based pricing analysis
   - Scaling cost projections

Format as a clear, technical document that AI developers, product managers, and tech leads can use for implementation planning.
"""
    
    response = monitored_generate_content(prompt, context="ai_selection_summary")
    return response.text if response else "AI selection summary generation failed."

@operation
def generate_formal_report(result):
    """Generate a formal, readable report of the workflow analysis"""
    prompt = f"""
You are a senior business consultant writing a comprehensive report for AI developers, product managers, tech leads, and senior decision-makers who need clarity on AI architecture, selecting the right LLMs, calculating ROI, estimating implementation and inference costs, and developing financial literacy around the total cost and value of deploying AI agents.

Workflow Analysis Data:
{json.dumps(result, indent=2)}

Write a detailed report with the following sections:

1. EXECUTIVE SUMMARY
   - Strategic overview for senior decision-makers
   - Key financial metrics and ROI projections
   - Critical success factors and risks

2. AI ARCHITECTURE AND LLM SELECTION
   - Detailed explanation of AI architecture decisions
   - Rationale for specific LLM and AI agent selections
   - Technical compatibility and integration considerations
   - Performance benchmarks and quality metrics

3. COMPREHENSIVE COST ANALYSIS
   - Implementation costs breakdown
   - Ongoing inference costs analysis
   - Hidden costs and infrastructure requirements
   - Cost optimization opportunities
   - Scaling cost projections (2x, 5x, 10x volume)

4. ROI CALCULATION AND FINANCIAL LITERACY
   - Detailed ROI calculations with assumptions
   - Payback period analysis
   - Total Cost of Ownership (TCO) over 3 years
   - Financial risk assessment
   - Budget allocation recommendations

5. IMPLEMENTATION STRATEGY
   - Phase-wise implementation plan
   - Resource requirements (technical and human)
   - Timeline and milestones
   - Risk mitigation strategies

6. OPERATIONAL CONSIDERATIONS
   - Performance monitoring and KPIs
   - Maintenance and optimization requirements
   - Vendor management and contract considerations
   - Compliance and security implications

7. VALUE REALIZATION AND BUSINESS IMPACT
   - Quantified business benefits
   - Productivity improvements
   - Quality enhancements
   - Competitive advantages

8. STRATEGIC RECOMMENDATIONS
   - Next steps for implementation
   - Long-term AI strategy considerations
   - Technology roadmap alignment
   - Change management requirements

Use professional business language with technical depth appropriate for the target audience. Include specific numbers, metrics, and financial analysis. Make it actionable for both technical implementation and business decision-making.

Format it as a comprehensive professional document with clear headers, bullet points where appropriate, and well-structured analysis.
"""
    
    response = monitored_generate_content(prompt, context="formal_report_generation")
    return response.text if response else "Report generation failed."

@operation
def generate_python_output_code(result):
    """Generate Python code that outputs the results in a structured format"""
    prompt = f"""
You are a Python developer. Create a Python script that displays the workflow analysis results in a well-formatted, structured way.

Results Data:
{json.dumps(result, indent=2)}

Create a Python script that:
1. Defines the results data as variables/dictionaries
2. Creates functions to display different sections of the results
3. Formats the output nicely with proper spacing and headers
4. Includes summary statistics and key insights
5. Makes it easy to understand the workflow solution

The script should be clean, well-commented, and easy to run. Include functions like:
- display_workflow_summary()
- display_agent_assignments()
- display_cost_breakdown()
- display_implementation_timeline()

Make the output professional and easy to read when the script is executed.
"""
    
    response = monitored_generate_content(prompt, context="python_output_generation")
    return response.text if response else "Python code generation failed."

# -----------------------------
# Enhanced Main Execution
# -----------------------------
@session
def main1():
    print("🚀 AI Workflow Solution Generator")
    print("=" * 50)
    
    # Step 1: Enrich agent data
    print("📥 Step 1: Enriching agent data from Gemini...")
    # enrich_all_agents()
    
    # Step 2: Build FAISS index
    print("📊 Step 2: Building FAISS index...")
    # build_faiss_index()
    
    # Step 3: Choose and process workflow
    workflow_type = "content_creation_pipeline"  # Change this to test different workflows
    workflow_description = COMPLEX_WORKFLOW_EXAMPLES[workflow_type]
    
    print(f"📝 Step 3: Processing workflow: {workflow_type}")
    print(f"📄 Workflow description length: {len(workflow_description)} characters")
    
    # Process the workflow
    result = process_complex_workflow(workflow_description)
    
    if result:
        print("\n" + "="*50)
        print("📊 WORKFLOW ANALYSIS COMPLETE")
        print("="*50)
        
        # Display quick summary
        if result['workflow_analysis']:
            print(f"🎯 Workflow: {result['workflow_analysis'].get('workflow_name', 'Unknown')}")
            print(f"💰 Budget: ${result['workflow_analysis'].get('monthly_budget', 'Not specified')}/month")
            print(f"📈 Volume: {result['workflow_analysis'].get('monthly_volume', 'Not specified')}")
        
        if result['cost_analysis']:
            print(f"\n💵 TOTAL ESTIMATED COST: ${result['cost_analysis'].get('total_monthly_cost', 'Not calculated')}/month")
            if 'budget_analysis' in result['cost_analysis']:
                budget_util = result['cost_analysis']['budget_analysis'].get('budget_utilization', 'N/A')
                print(f"📊 Budget Utilization: {budget_util}")
        
        print(f"\n📋 Agent Assignments:")
        for step_name, agents in result['agent_assignments'].items():
            print(f"\n🔹 {step_name}:")
            for agent in agents[:2]:  # Show top 2 agents per step
                print(f"   • {agent.get('agent_name', 'Unknown')} (Score: {agent.get('suitability_score', 'N/A')}/10)")
        
        # Generate outputs
        print("\n" + "="*50)
        print("📄 GENERATING DETAILED OUTPUTS")
        print("="*50)
        
        # Generate formal report
        print("📝 Generating formal business report...")
        formal_report = generate_formal_report(result)
        
        # Generate Python output code
        print("🐍 Generating Python output code...")
        python_output = generate_python_output_code(result)
        
        # Save all outputs
        outputs = {
            'raw_analysis': result,
            'formal_report': formal_report,
            'python_output_code': python_output
        }
        
        # Save to files
        with open('workflow_solution_complete.json', 'w') as f:
            json.dump(outputs, f, indent=2)
        
        with open('workflow_formal_report.txt', 'w') as f:
            f.write(formal_report)
        
        with open('workflow_output_display.py', 'w') as f:
            f.write(python_output)
        
        print("\n💾 OUTPUTS SAVED:")
        print("   • workflow_solution_complete.json (All data)")
        print("   • workflow_formal_report.txt (Business report)")
        print("   • workflow_output_display.py (Python display code)")
        
        # Display formal report preview
        print("\n" + "="*50)
        print("📄 FORMAL REPORT PREVIEW")
        print("="*50)
        print(formal_report[:1500] + "\n...(continued in workflow_formal_report.txt)")
        
    else:
        print("❌ Failed to process workflow")
    
    return True

if __name__ == "__main__":
    main1()
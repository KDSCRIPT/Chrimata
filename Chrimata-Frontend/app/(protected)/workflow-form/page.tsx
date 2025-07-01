"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useUser, useClerk, SignInButton, useAuth } from "@clerk/nextjs";

import {
  Zap,
  ArrowLeft,
  ArrowRight,
  Plus,
  X,
  CheckCircle,
  FileText,
  Upload,
  LogOut,
  Shield,
  Loader2,
} from "lucide-react";

const removeFileExtension = (filename: string): string => {
  return filename.replace(/\.[^/.]+$/, ""); // removes last .xxx
};

interface FormData {
  // Business Context
  industry_model: string;
  company_size: string;

  // Goals & Challenges
  goals: string;
  top_challenges: string;

  // Tools & Departments
  tools_platforms: string;
  departments_str: string[];

  // Team Summaries
  team_summaries: { [key: string]: string };

  // Task Focus
  task_number: number;

  // Optional Bottleneck Clues
  optional_bottleneck_clues: { task: string; description: string }[];

  // Financial Documents (NEW)
  financial_documents: {
    balance_sheet: File | null;
    income_statement: File | null;
    cash_flow_statement: File | null;
    shareholders_equity: File | null;
  };
  // ROI Estimation
  roi_inputs: {
    tasks_per_month: number;
    current_time_per_task_minutes: number;
    people_involved_count: number;
    avg_hourly_cost_per_employee: number;
    technical_feasibility_rating: string;
    technical_feasibility_notes: string;
    required_skills_resources: string;
    estimated_implementation_timeline: string;
  };

  // Implementation & Operations
  implementation_inputs: {
    operational_ownership: string;
    sla_and_uptime_requirements: string;
    disaster_recovery_and_rollback: string;
    user_training_and_communication: string;
    change_management_activities: string;
    recommended_next_steps: string;
  };
}

export default function WorkflowFormPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newDepartment, setNewDepartment] = useState("");
  const [newBottleneck, setNewBottleneck] = useState({
    task: "",
    description: "",
  });
  const { isSignedIn, isLoaded } = useUser();
  const { signOut } = useClerk();
  const { getToken } = useAuth(); // <-- use Clerk's token hook
  const router = useRouter();

  const [formData, setFormData] = useState<FormData>({
    // Business Context
    industry_model: "",
    company_size: "",

    // Goals & Challenges
    goals: "",
    top_challenges: "",

    // Tools & Departments
    tools_platforms: "",
    departments_str: [],

    // Team Summaries
    team_summaries: {},

    // Task Focus
    task_number: 1,

    // Optional Bottleneck Clues
    optional_bottleneck_clues: [],

    // Financial Documents (NEW)
    financial_documents: {
      balance_sheet: null,
      income_statement: null,
      cash_flow_statement: null,
      shareholders_equity: null,
    },

    // ROI Estimation
    roi_inputs: {
      tasks_per_month: 0,
      current_time_per_task_minutes: 0,
      people_involved_count: 0,
      avg_hourly_cost_per_employee: 0,
      technical_feasibility_rating: "Medium",
      technical_feasibility_notes: "",
      required_skills_resources: "",
      estimated_implementation_timeline: "",
    },

    // Implementation & Operations
    implementation_inputs: {
      operational_ownership: "",
      sla_and_uptime_requirements: "",
      disaster_recovery_and_rollback: "",
      user_training_and_communication: "",
      change_management_activities: "",
      recommended_next_steps: "",
    },
  });

  const totalSteps = 7;
  const progress = (currentStep / totalSteps) * 100;

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNestedInputChange = (
    parent: string,
    field: string,
    value: any
  ) => {
    setFormData((prev) => ({
      ...prev,
      [parent]: {
        ...(prev[parent as keyof FormData] as any),
        [field]: value,
      },
    }));
  };

  const addDepartment = () => {
    if (newDepartment.trim()) {
      setFormData((prev) => ({
        ...prev,
        departments_str: [...prev.departments_str, newDepartment.trim()],
        team_summaries: {
          ...prev.team_summaries,
          [newDepartment.trim()]: "",
        },
      }));
      setNewDepartment("");
    }
  };

  const removeDepartment = (dept: string) => {
    setFormData((prev) => {
      const newTeamSummaries = { ...prev.team_summaries };
      delete newTeamSummaries[dept];
      return {
        ...prev,
        departments_str: prev.departments_str.filter((d) => d !== dept),
        team_summaries: newTeamSummaries,
      };
    });
  };

  const addBottleneck = () => {
    if (newBottleneck.task.trim() && newBottleneck.description.trim()) {
      setFormData((prev) => ({
        ...prev,
        optional_bottleneck_clues: [
          ...prev.optional_bottleneck_clues,
          { ...newBottleneck },
        ],
      }));
      setNewBottleneck({ task: "", description: "" });
    }
  };

  const removeBottleneck = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      optional_bottleneck_clues: prev.optional_bottleneck_clues.filter(
        (_, i) => i !== index
      ),
    }));
  };

  const handleFileUpload = (documentType: string, file: File | null) => {
    setFormData((prev) => ({
      ...prev,
      financial_documents: {
        ...prev.financial_documents,
        [documentType]: file,
      },
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    try {
      // Create FormData object for file uploads
      const submitFormData = new FormData();

      // Add all form fields based on your actual state structure
      submitFormData.append("industry_model", formData.industry_model);
      submitFormData.append("company_size", formData.company_size);
      submitFormData.append("goals", formData.goals);
      submitFormData.append("top_challenges", formData.top_challenges);
      submitFormData.append("tools_platforms", formData.tools_platforms);
      submitFormData.append("task_number", formData.task_number.toString());

      // Add departments as array
      formData.departments_str.forEach((dept) => {
        submitFormData.append("departments_str[]", dept);
      });

      // Add team summaries
      Object.entries(formData.team_summaries).forEach(([dept, summary]) => {
        submitFormData.append(`team_summaries[${dept}]`, summary);
      });

      // Add bottleneck clues
      formData.optional_bottleneck_clues.forEach((bottleneck, index) => {
        submitFormData.append(`bottleneck_${index}_task`, bottleneck.task);
        submitFormData.append(
          `bottleneck_${index}_description`,
          bottleneck.description
        );
      });

      // Add ROI inputs
      Object.entries(formData.roi_inputs).forEach(([key, value]) => {
        submitFormData.append(`roi_${key}`, value.toString());
      });

      // Add implementation inputs
      Object.entries(formData.implementation_inputs).forEach(([key, value]) => {
        submitFormData.append(`implementation_${key}`, value);
      });

      // Add financial documents (files)
      Object.entries(formData.financial_documents).forEach(
        ([docType, file]) => {
          if (file) {
            submitFormData.append(`financial_${docType}`, file);
          }
        }
      );

      // Get auth token
      const token = await getToken();
      if (!token) {
        throw new Error("Authentication required");
      }

      // Submit form with FormData
      const response = await fetch(
        "https://chrimata.onrender.com/api/run-workflow",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            // Don't set Content-Type - let browser set it for FormData
          },
          body: submitFormData, // Send FormData instead of JSON
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to submit workflow");
      }

      const result = await response.json();
      console.log("Workflow submitted successfully:", result);

      // Extract filename and redirect
      if (result.filename) {
        const filename = removeFileExtension(result.filename);

        // Preload chat history
        const freshToken = await getToken();
        await fetch(
          `https://chrimata.onrender.com/api/chat-history/${filename}`,
          {
            headers: {
              Authorization: `Bearer ${freshToken}`,
            },
          }
        );

        // Redirect to chat
        router.push(`/chat/${filename}`);
      }
    } catch (error) {
      console.error("Error submitting workflow:", error);
      // Handle error (show toast, set error state, etc.)
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // const handleLogout = () => {
  //   router.push("/login");
  // };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="industry">Industry Model</Label>
              <Select
                value={formData.industry_model}
                onValueChange={(value) =>
                  handleInputChange("industry_model", value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="retail-b2c">Retail - B2C</SelectItem>
                  <SelectItem value="technology-saas">
                    Technology - SaaS
                  </SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="education">Education</SelectItem>
                  <SelectItem value="consulting">Consulting</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="company_size">Company Size</Label>
              <Input
                id="company_size"
                placeholder="e.g., 200 employees"
                value={formData.company_size}
                onChange={(e) =>
                  handleInputChange("company_size", e.target.value)
                }
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="goals">Business Goals</Label>
              <Textarea
                id="goals"
                placeholder="Describe your main business goals and objectives (markdown-style bullets allowed)..."
                value={formData.goals}
                onChange={(e) => handleInputChange("goals", e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="challenges">Top Challenges</Label>
              <Textarea
                id="challenges"
                placeholder="What are your biggest operational challenges?"
                value={formData.top_challenges}
                onChange={(e) =>
                  handleInputChange("top_challenges", e.target.value)
                }
                rows={4}
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="tools">Current Tools & Platforms</Label>
              <Input
                id="tools"
                placeholder="Comma-separated list of tools (e.g., Salesforce, Slack, Google Workspace)"
                value={formData.tools_platforms}
                onChange={(e) =>
                  handleInputChange("tools_platforms", e.target.value)
                }
              />
            </div>
            <div>
              <Label>Departments</Label>
              <div className="flex gap-2 mb-3">
                <Input
                  placeholder="Add department"
                  value={newDepartment}
                  onChange={(e) => setNewDepartment(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && addDepartment()}
                />
                <Button type="button" onClick={addDepartment} size="sm">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.departments_str.map((dept, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    {dept}
                    <X
                      className="w-3 h-3 cursor-pointer"
                      onClick={() => removeDepartment(dept)}
                    />
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <Label>Team Summaries</Label>
              <p className="text-sm text-gray-600 mb-4">
                Provide a brief description for each department
              </p>
              {formData.departments_str.map((dept) => (
                <div key={dept} className="space-y-2 mb-4">
                  <Label htmlFor={`team_${dept}`}>{dept}</Label>
                  <Textarea
                    id={`team_${dept}`}
                    placeholder={`Describe the ${dept} team's role and responsibilities...`}
                    value={formData.team_summaries[dept] || ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        team_summaries: {
                          ...prev.team_summaries,
                          [dept]: e.target.value,
                        },
                      }))
                    }
                    rows={3}
                  />
                </div>
              ))}
            </div>
            <div>
              <Label htmlFor="task_number">Number of Key Tasks/Processes</Label>
              <Input
                id="task_number"
                type="number"
                placeholder="e.g., 1"
                value={formData.task_number}
                onChange={(e) =>
                  handleInputChange(
                    "task_number",
                    Number.parseInt(e.target.value) || 1
                  )
                }
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <Label>Bottleneck Clues (Optional)</Label>
              <p className="text-sm text-gray-600 mb-4">
                Identify specific tasks and their bottlenecks
              </p>
              <div className="space-y-3 mb-4">
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    placeholder="Task name"
                    value={newBottleneck.task}
                    onChange={(e) =>
                      setNewBottleneck((prev) => ({
                        ...prev,
                        task: e.target.value,
                      }))
                    }
                  />
                  <Input
                    placeholder="Bottleneck description"
                    value={newBottleneck.description}
                    onChange={(e) =>
                      setNewBottleneck((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                  />
                </div>
                <Button
                  type="button"
                  onClick={addBottleneck}
                  size="sm"
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Bottleneck
                </Button>
              </div>
              <div className="space-y-2">
                {formData.optional_bottleneck_clues.map((bottleneck, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium">{bottleneck.task}</div>
                      <div className="text-sm text-gray-600">
                        {bottleneck.description}
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeBottleneck(index)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div>
              <Label>Financial Documents (Optional)</Label>
              <p className="text-sm text-gray-600 mb-6">
                Upload your financial statements to help us provide more
                accurate ROI analysis and recommendations. All documents are
                processed securely and used only for analysis purposes.
              </p>

              <div className="grid gap-6">
                {/* Balance Sheet */}
                <div className="space-y-2">
                  <Label
                    htmlFor="balance_sheet"
                    className="flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Balance Sheet
                  </Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
                    <input
                      id="balance_sheet"
                      type="file"
                      accept=".csv,.xlsx"
                      onChange={(e) =>
                        handleFileUpload(
                          "balance_sheet",
                          e.target.files?.[0] || null
                        )
                      }
                      className="hidden"
                    />
                    <label
                      htmlFor="balance_sheet"
                      className="cursor-pointer block"
                    >
                      <div className="text-center">
                        {formData.financial_documents.balance_sheet ? (
                          <div className="flex items-center justify-center gap-2 text-green-600">
                            <CheckCircle className="w-5 h-5" />
                            <span className="font-medium">
                              {formData.financial_documents.balance_sheet.name}
                            </span>
                          </div>
                        ) : (
                          <div className="text-gray-500">
                            <Upload className="w-8 h-8 mx-auto mb-2" />
                            <p className="font-medium">
                              Click to upload Balance Sheet
                            </p>
                            <p className="text-sm">
                              Only Excel or CSV files accepted
                            </p>
                          </div>
                        )}
                      </div>
                    </label>
                  </div>
                </div>

                {/* Income Statement */}
                <div className="space-y-2">
                  <Label
                    htmlFor="income_statement"
                    className="flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Income Statement (P&L)
                  </Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
                    <input
                      id="income_statement"
                      type="file"
                      accept=".pdf,.xlsx,.xls,.csv"
                      onChange={(e) =>
                        handleFileUpload(
                          "income_statement",
                          e.target.files?.[0] || null
                        )
                      }
                      className="hidden"
                    />
                    <label
                      htmlFor="income_statement"
                      className="cursor-pointer block"
                    >
                      <div className="text-center">
                        {formData.financial_documents.income_statement ? (
                          <div className="flex items-center justify-center gap-2 text-green-600">
                            <CheckCircle className="w-5 h-5" />
                            <span className="font-medium">
                              {
                                formData.financial_documents.income_statement
                                  .name
                              }
                            </span>
                          </div>
                        ) : (
                          <div className="text-gray-500">
                            <Upload className="w-8 h-8 mx-auto mb-2" />
                            <p className="font-medium">
                              Click to upload Income Statement
                            </p>
                            <p className="text-sm">
                              PDF, Excel, or CSV files accepted
                            </p>
                          </div>
                        )}
                      </div>
                    </label>
                  </div>
                </div>

                {/* Cash Flow Statement */}
                <div className="space-y-2">
                  <Label
                    htmlFor="cash_flow_statement"
                    className="flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Cash Flow Statement
                  </Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
                    <input
                      id="cash_flow_statement"
                      type="file"
                      accept=".pdf,.xlsx,.xls,.csv"
                      onChange={(e) =>
                        handleFileUpload(
                          "cash_flow_statement",
                          e.target.files?.[0] || null
                        )
                      }
                      className="hidden"
                    />
                    <label
                      htmlFor="cash_flow_statement"
                      className="cursor-pointer block"
                    >
                      <div className="text-center">
                        {formData.financial_documents.cash_flow_statement ? (
                          <div className="flex items-center justify-center gap-2 text-green-600">
                            <CheckCircle className="w-5 h-5" />
                            <span className="font-medium">
                              {
                                formData.financial_documents.cash_flow_statement
                                  .name
                              }
                            </span>
                          </div>
                        ) : (
                          <div className="text-gray-500">
                            <Upload className="w-8 h-8 mx-auto mb-2" />
                            <p className="font-medium">
                              Click to upload Cash Flow Statement
                            </p>
                            <p className="text-sm">
                              PDF, Excel, or CSV files accepted
                            </p>
                          </div>
                        )}
                      </div>
                    </label>
                  </div>
                </div>

                {/* Statement of Shareholders' Equity */}
                <div className="space-y-2">
                  <Label
                    htmlFor="shareholders_equity"
                    className="flex items-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Statement of Shareholders' Equity
                  </Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
                    <input
                      id="shareholders_equity"
                      type="file"
                      accept=".pdf,.xlsx,.xls,.csv"
                      onChange={(e) =>
                        handleFileUpload(
                          "shareholders_equity",
                          e.target.files?.[0] || null
                        )
                      }
                      className="hidden"
                    />
                    <label
                      htmlFor="shareholders_equity"
                      className="cursor-pointer block"
                    >
                      <div className="text-center">
                        {formData.financial_documents.shareholders_equity ? (
                          <div className="flex items-center justify-center gap-2 text-green-600">
                            <CheckCircle className="w-5 h-5" />
                            <span className="font-medium">
                              {
                                formData.financial_documents.shareholders_equity
                                  .name
                              }
                            </span>
                          </div>
                        ) : (
                          <div className="text-gray-500">
                            <Upload className="w-8 h-8 mx-auto mb-2" />
                            <p className="font-medium">
                              Click to upload Statement of Shareholders' Equity
                            </p>
                            <p className="text-sm">
                              PDF, Excel, or CSV files accepted
                            </p>
                          </div>
                        )}
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-start gap-2">
                  <Shield className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-blue-900 mb-1">
                      Data Security & Privacy
                    </h4>
                    <p className="text-sm text-blue-800">
                      Your financial documents are processed securely and used
                      only for generating personalized workflow recommendations.
                      We do not store or share your financial data with third
                      parties.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 7:
        return (
          <div className="space-y-6">
            <div>
              <Label>ROI Estimation</Label>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <Label htmlFor="tasks_per_month">Tasks Per Month</Label>
                  <Input
                    id="tasks_per_month"
                    type="number"
                    placeholder="e.g., 100"
                    value={formData.roi_inputs.tasks_per_month}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "tasks_per_month",
                        Number.parseInt(e.target.value) || 0
                      )
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="current_time_per_task">
                    Minutes Per Task
                  </Label>
                  <Input
                    id="current_time_per_task"
                    type="number"
                    placeholder="e.g., 30"
                    value={formData.roi_inputs.current_time_per_task_minutes}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "current_time_per_task_minutes",
                        Number.parseInt(e.target.value) || 0
                      )
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="people_involved">People Involved</Label>
                  <Input
                    id="people_involved"
                    type="number"
                    placeholder="e.g., 3"
                    value={formData.roi_inputs.people_involved_count}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "people_involved_count",
                        Number.parseInt(e.target.value) || 0
                      )
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="avg_hourly_cost">Avg. Hourly Cost ($)</Label>
                  <Input
                    id="avg_hourly_cost"
                    type="number"
                    placeholder="e.g., 50"
                    value={formData.roi_inputs.avg_hourly_cost_per_employee}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "avg_hourly_cost_per_employee",
                        Number.parseInt(e.target.value) || 0
                      )
                    }
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="technical_feasibility">
                    Technical Feasibility
                  </Label>
                  <Select
                    value={formData.roi_inputs.technical_feasibility_rating}
                    onValueChange={(value) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "technical_feasibility_rating",
                        value
                      )
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select feasibility" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Low">Low</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="High">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="feasibility_notes">Feasibility Notes</Label>
                  <Textarea
                    id="feasibility_notes"
                    placeholder="Additional notes about technical feasibility..."
                    value={formData.roi_inputs.technical_feasibility_notes}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "technical_feasibility_notes",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>

                <div>
                  <Label htmlFor="required_skills">
                    Required Skills & Resources
                  </Label>
                  <Textarea
                    id="required_skills"
                    placeholder="What skills and resources are needed for implementation?"
                    value={formData.roi_inputs.required_skills_resources}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "required_skills_resources",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>

                <div>
                  <Label htmlFor="implementation_timeline">
                    Implementation Timeline
                  </Label>
                  <Input
                    id="implementation_timeline"
                    placeholder="e.g., PoC: 1 month, Full: 4 months"
                    value={
                      formData.roi_inputs.estimated_implementation_timeline
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "roi_inputs",
                        "estimated_implementation_timeline",
                        e.target.value
                      )
                    }
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 8:
        return (
          <div className="space-y-6">
            <div>
              <Label>Implementation & Operations</Label>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="operational_ownership">
                    Operational Ownership
                  </Label>
                  <Input
                    id="operational_ownership"
                    placeholder="Who will own and manage this AI implementation?"
                    value={formData.implementation_inputs.operational_ownership}
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "operational_ownership",
                        e.target.value
                      )
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="sla_requirements">
                    SLA & Uptime Requirements
                  </Label>
                  <Input
                    id="sla_requirements"
                    placeholder="What are your performance and availability requirements?"
                    value={
                      formData.implementation_inputs.sla_and_uptime_requirements
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "sla_and_uptime_requirements",
                        e.target.value
                      )
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="disaster_recovery">
                    Disaster Recovery & Rollback
                  </Label>
                  <Textarea
                    id="disaster_recovery"
                    placeholder="What are your disaster recovery and rollback plans?"
                    value={
                      formData.implementation_inputs
                        .disaster_recovery_and_rollback
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "disaster_recovery_and_rollback",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>
                <div>
                  <Label htmlFor="user_training">
                    User Training & Communication
                  </Label>
                  <Textarea
                    id="user_training"
                    placeholder="How will you train users and communicate changes?"
                    value={
                      formData.implementation_inputs
                        .user_training_and_communication
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "user_training_and_communication",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>
                <div>
                  <Label htmlFor="change_management">
                    Change Management Activities
                  </Label>
                  <Textarea
                    id="change_management"
                    placeholder="What change management activities will you implement?"
                    value={
                      formData.implementation_inputs
                        .change_management_activities
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "change_management_activities",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>
                <div>
                  <Label htmlFor="next_steps">Recommended Next Steps</Label>
                  <Textarea
                    id="next_steps"
                    placeholder="What are your recommended next steps?"
                    value={
                      formData.implementation_inputs.recommended_next_steps
                    }
                    onChange={(e) =>
                      handleNestedInputChange(
                        "implementation_inputs",
                        "recommended_next_steps",
                        e.target.value
                      )
                    }
                    rows={2}
                  />
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const stepTitles = [
    "Business Context",
    "Goals & Challenges",
    "Tools & Departments",
    "Team Details",
    "Process Analysis",
    "ROI Estimation",
    "Implementation Planning",
  ];

  const handleLogout = async () => {
    await signOut();
    router.push("/");
  };

  if (!isLoaded) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center bg-slate-50 p-4">
        <h2 className="text-2xl font-semibold mb-4">
          Please sign in to access your reports
        </h2>
        <SignInButton mode="modal">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white">
            Sign In
          </Button>
        </SignInButton>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      {/* <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Chrimata
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              Step {currentStep} of {totalSteps}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-1"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </header> */}

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-2xl font-bold">
              {stepTitles[currentStep - 1]}
            </h1>
            <span className="text-sm text-gray-600">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Form */}
        <Card className="border-0 shadow-xl">
          <CardHeader>
            <CardTitle>Workflow Discovery Form</CardTitle>
            <CardDescription>
              Help us understand your business to provide personalized AI
              workflow recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderStep()}

            {/* Navigation */}
            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              <Button
                type="button"
                onClick={nextStep}
                disabled={isSubmitting}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {currentStep === totalSteps ? (
                  isSubmitting ? (
                    "Generating Report..."
                  ) : (
                    "Generate Report"
                  )
                ) : (
                  <>
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useUser, useClerk, SignInButton, useAuth } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/card";
import { Zap, FileText, Plus, ArrowRight, Loader2, Clock } from "lucide-react";

interface Report {
  name: string;
  url: string;
  displayName?: string;
}

export default function ReportDashboard() {
  const { isSignedIn, isLoaded } = useUser();
  const { signOut } = useClerk();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { getToken } = useAuth(); // <-- use Clerk's token hook

  useEffect(() => {
    if (!isSignedIn) {
      setLoading(false);
      return;
    }

    const fetchReports = async () => {
      setLoading(true);
      try {
        const token = await getToken(); // Get Clerk session token
        if (!token) {
          console.error("No Clerk token found.");
          setLoading(false);
          return;
        }

        const response = await axios.get(
          "https://chrimata.onrender.com/api/reports/list",
          {
            headers: {
              Authorization: `Bearer ${token}`, // Send Clerk JWT
            },
          }
        );

        const processedData = response.data.map((report: Report) => ({
          ...report,
          displayName: formatReportName(report.name),
        }));

        setReports(processedData);
      } catch (error) {
        console.error("Error fetching reports:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [isSignedIn]);

  const formatReportName = (name: string): string => {
    const dateMatch = name.match(/_\$(\d+)_/);
    let dateStr = "Unknown date";

    if (dateMatch && dateMatch[1]) {
      const timestamp = Number.parseInt(dateMatch[1]);
      const date = new Date(timestamp * 1000);
      dateStr = date.toLocaleDateString();
    }

    const nameMatch = name.match(/_workflow_(.+)\.md/);
    const readableName = nameMatch
      ? nameMatch[1].replace(/_/g, " ")
      : "Workflow Report";

    return `${readableName}`;
  };

  const handleNewReport = () => {
    router.push("/workflow-form");
  };

  const handleViewReport = (fileName: string) => {
    router.push(`/chat/${encodeURIComponent(fileName)}`);
  };

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
      {/* <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
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
            <div className="text-sm text-white-600">
              Your AI Workflow Reports
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="text-red-600 border-red-200 hover:bg-red-50"
            >
              Logout
            </Button>
          </div>
        </div>
      </header> */}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Workflow Reports Dashboard</h1>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card
            className="border-0 shadow-xl hover:shadow-2xl transition-shadow bg-gradient-to-r from-blue-600 to-purple-600
                hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 space-y-4"
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-white" />
                Create New Report
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-white">
                Generate a new AI workflow discovery report by filling out our
                comprehensive form
              </p>
              <p className="text-white">
                Answer questions about your business, processes, and goals to
                receive personalized AI workflow recommendations and
                implementation strategies.
              </p>
              <div className="flex items-center gap-2 text-sm text-white">
                <Clock className="w-4 h-4" />
                <span>Takes approximately 10-15 minutes</span>
              </div>
              <Button size="lg" onClick={handleNewReport}>
                Start new Report
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </CardContent>
          </Card>

          <Card
            className="bg-gradient-to-r from-blue-600 to-purple-600
                hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 space-y-4 border-0 shadow-xl"
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-white" />
                About Workflow Reports
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                Our AI-generated workflow reports provide personalized
                recommendations for automating your business processes. Each
                report includes:
              </p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Custom AI workflow recommendations</li>
                <li>Implementation roadmap with timelines</li>
                <li>ROI analysis and cost-benefit projections</li>
                <li>Technical requirements and resource planning</li>
              </ul>
              <p>
                You can chat with our AI assistant about any report to get more
                detailed information and answers to your specific questions.
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Your Workflow Reports
            </CardTitle>
            <CardDescription>
              Select a report to view recommendations and continue your
              conversation
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            ) : reports.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-white mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No reports found</h3>
                <p className="text-white mb-6">
                  You haven't created any workflow reports yet.
                </p>
                <Button onClick={handleNewReport}>
                  Create Your First Report
                </Button>
              </div>
            ) : (
              <div className="grid gap-4">
                {reports.map((report) => (
                  <Card
                    key={report.name}
                    className="bg-gradient-to-r from-blue-600 to-purple-600
                hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3"
                    onClick={() => handleViewReport(report.name)}
                  >
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-white" />
                        <div>
                          <div className="font-medium">
                            {report.displayName || report.name}
                          </div>
                          <div className="text-sm text-white truncate max-w-md">
                            {report.name}
                          </div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ArrowRight className="w-4 h-4" />
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

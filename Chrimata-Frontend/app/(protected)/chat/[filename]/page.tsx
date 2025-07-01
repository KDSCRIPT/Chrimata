"use client";

import type React from "react";
import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { useRouter, useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import {
  Zap,
  Send,
  User,
  Bot,
  Loader2,
  FileText,
  Download,
  Star,
  CheckCircle,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useAuth } from "@clerk/nextjs";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface FeedbackData {
  rating: number;
  helpful_sections: string[];
  improvement_suggestions: string;
}

const removeFileExtension = (filename: string): string =>
  filename.replace(/\.[^/.]+$/, "");

// Custom Mermaid component
const MermaidDiagram: React.FC<{ chart: string }> = ({ chart }) => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const renderMermaid = async () => {
      if (typeof window !== "undefined" && elementRef.current) {
        try {
          // Check if mermaid is already loaded
          if (!(window as any).mermaid) {
            // Load Mermaid from CDN
            const script = document.createElement("script");
            script.src =
              "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
            script.onload = () => {
              const mermaid = (window as any).mermaid;
              if (mermaid && !isLoaded) {
                mermaid.initialize({
                  startOnLoad: false,
                  theme: "default",
                  securityLevel: "loose",
                });
                setIsLoaded(true);
                renderDiagram(mermaid);
              }
            };
            document.head.appendChild(script);
          } else {
            const mermaid = (window as any).mermaid;
            if (!isLoaded) {
              mermaid.initialize({
                startOnLoad: false,
                theme: "default",
                securityLevel: "loose",
              });
              setIsLoaded(true);
            }
            renderDiagram(mermaid);
          }
        } catch (error) {
          console.error("Error loading Mermaid:", error);
          showFallback();
        }
      }
    };

    const renderDiagram = async (mermaid: any) => {
      if (elementRef.current) {
        try {
          // Clear previous content
          elementRef.current.innerHTML = "";

          // Generate unique ID
          const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

          // Render the diagram
          const { svg } = await mermaid.render(id, chart);
          elementRef.current.innerHTML = svg;
        } catch (error) {
          console.error("Error rendering Mermaid diagram:", error);
          showFallback();
        }
      }
    };

    const showFallback = () => {
      if (elementRef.current) {
        elementRef.current.innerHTML = `<pre style="background: #f5f5f5; padding: 1rem; border-radius: 4px; overflow-x: auto; border: 1px solid #ddd;"><code>${chart}</code></pre>`;
      }
    };

    renderMermaid();
  }, [chart, isLoaded]);

  return <div ref={elementRef} className="mermaid-diagram my-4" />;
};

// Custom components for ReactMarkdown
const MarkdownComponents = {
  code: ({ node, inline, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || "");
    const language = match ? match[1] : "";

    if (language === "mermaid" && !inline) {
      return <MermaidDiagram chart={String(children).replace(/\n$/, "")} />;
    }

    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

export default function ChatReportView() {
  const router = useRouter();
  const { filename } = useParams();
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [reportContent, setReportContent] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackData>({
    rating: 0,
    helpful_sections: [],
    improvement_suggestions: "",
  });
  const [isDownloading, setIsDownloading] = useState(false);
  const { getToken } = useAuth();

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

  useEffect(() => {
    const fetchData = async () => {
      setIsLoadingData(true);
      const authToken = await getToken();
      if (!authToken) {
        console.error("No Clerk token found.");
        setIsLoadingData(false);
        return;
      }
      try {
        const filenameWithoutExt = removeFileExtension(filename as string);

        const chatRes = await axios.get(
          `https://chrimata.onrender.com/api/chat-history/${filenameWithoutExt}`,
          {
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }
        );
        setChatHistory(chatRes.data || []);

        const freshToken = await getToken();
        const reportRes = await axios.get(
          `https://chrimata.onrender.com/api/report-content/${filenameWithoutExt}`,
          {
            headers: {
              Authorization: `Bearer ${freshToken}`,
            },
          }
        );
        setReportContent(reportRes.data.content);
      } catch (err) {
        console.error("Error fetching chat or report:", err);
      } finally {
        setIsLoadingData(false);
      }
    };

    fetchData();
  }, [filename, getToken]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const sendMessage = async () => {
    if (!question.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: question,
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const authToken = await getToken();
      if (!authToken) {
        console.error("No Clerk token found.");
        setLoading(false);
        return;
      }
      const filenameWithoutExt = removeFileExtension(filename as string);
      const res = await axios.post(
        `https://chrimata.onrender.com/api/ask-chatbot/${filenameWithoutExt}`,
        { question },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: res.data.answer,
      };

      setChatHistory((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "Sorry, I encountered an error processing your question. Please try again.",
      };
      setChatHistory((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const downloadReport = async () => {
    setIsDownloading(true);
    try {
      const authToken = await getToken();
      if (!authToken) {
        console.error("No Clerk token found.");
        return;
      }

      const filenameWithoutExt = removeFileExtension(filename as string);
      const response = await axios.get(
        `https://chrimata.onrender.com/api/download-report/${filenameWithoutExt}`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          responseType: "blob",
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;

      const reportName = formatReportName(filename as string).replace(
        /[^a-zA-Z0-9]/g,
        "_"
      );
      link.setAttribute("download", `${reportName}.md`);

      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error downloading report:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  const submitFeedback = async () => {
    try {
      const authToken = await getToken();
      if (!authToken) {
        console.error("No Clerk token found.");
        return;
      }

      const filenameWithoutExt = removeFileExtension(filename as string);
      await axios.post(
        `https://chrimata.onrender.com/api/generate-prompt/${filenameWithoutExt}`,
        feedback,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
    } catch (err: any) {
      if (axios.isAxiosError(err) && err.response?.status === 400) {
        alert("You've already submitted feedback for this report.");
      } else {
        console.error("Error submitting feedback:", err);
      }
    }
  };

  const toggleHelpfulSection = (section: string) => {
    setFeedback((prev) => ({
      ...prev,
      helpful_sections: prev.helpful_sections.includes(section)
        ? prev.helpful_sections.filter((s) => s !== section)
        : [...prev.helpful_sections, section],
    }));
  };

  const reportSections = [
    "Executive Summary",
    "Business Profile",
    "Recommended AI Workflows",
    "ROI Analysis",
    "Implementation Roadmap",
    "Technology Stack",
    "Risk Mitigation",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-5 h-5 text-blue-600" />
          <h1 className="text-2xl font-bold truncate">
            {formatReportName(filename as string)}
          </h1>
          {showFeedback && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              Feedback Submitted
            </Badge>
          )}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={isDownloading}
              onClick={() => downloadReport()}
            >
              {isDownloading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
              Download
            </Button>

            {!showFeedback && (
              <Button
                variant="outline"
                size="sm"
                disabled={isDownloading}
                onClick={() => setShowFeedback(true)}
              >
                Give Feedback
              </Button>
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
          {/* Chat Section */}
          <Card className="border-0 shadow-xl flex flex-col h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                AI Assistant
              </CardTitle>
              <p className="text-sm text-gray-600">
                Ask questions about this workflow report
              </p>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0">
              <div className="flex-1 px-6 py-4 overflow-y-auto">
                <div className="space-y-4 pb-4">
                  {isLoadingData ? (
                    <div className="flex justify-center items-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    </div>
                  ) : chatHistory.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">
                      <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>
                        Start a conversation by asking about this workflow
                        report!
                      </p>
                      <p className="text-sm mt-2">
                        Try asking: "How should I prioritize these workflows?"
                      </p>
                    </div>
                  ) : (
                    chatHistory.map((message, index) => (
                      <div
                        key={index}
                        className={`flex gap-3 ${
                          message.role === "user"
                            ? "justify-end"
                            : "justify-start"
                        }`}
                      >
                        <div
                          className={`flex gap-3 max-w-[80%] ${
                            message.role === "user"
                              ? "flex-row-reverse"
                              : "flex-row"
                          }`}
                        >
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                              message.role === "user"
                                ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                                : "bg-gray-800 text-white"
                            }`}
                          >
                            {message.role === "user" ? (
                              <User className="w-4 h-4" />
                            ) : (
                              <Bot className="w-4 h-4" />
                            )}
                          </div>
                          <div
                            className={`rounded-lg px-4 py-2 ${
                              message.role === "user"
                                ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                                : "bg-gray-800 text-white"
                            }`}
                          >
                            <div className="prose prose-sm prose-invert max-w-none">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                rehypePlugins={[rehypeRaw]}
                                components={MarkdownComponents}
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  {loading && (
                    <div className="flex gap-3 justify-start">
                      <div className="w-8 h-8 rounded-full bg-gray-800 text-white flex items-center justify-center">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div className="bg-gray-800 rounded-lg px-4 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-white" />
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              </div>

              <Separator />

              {/* Chat Input */}
              <div className="p-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask a question about this workflow report..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={loading || !question.trim()}
                    size="sm"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Report Section */}
          <Card className="border-0 shadow-xl h-full">
            <CardHeader>
              <CardTitle>Workflow Report</CardTitle>
              <p className="text-sm text-gray-600">
                Personalized AI workflow recommendations
              </p>
            </CardHeader>
            <CardContent className="p-0">
              <div className="h-[calc(100vh-240px)] overflow-y-auto">
                <div className="p-6">
                  {isLoadingData ? (
                    <div className="flex justify-center items-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw]}
                        components={MarkdownComponents}
                      >
                        {reportContent || "No report content available."}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-500" />
                Report Feedback
              </CardTitle>
              <p className="text-sm text-gray-600">
                Help us improve our AI workflow recommendations
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Rating */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Overall Rating
                </label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() =>
                        setFeedback((prev) => ({ ...prev, rating: star }))
                      }
                      className={`p-1 ${
                        star <= feedback.rating
                          ? "text-yellow-500"
                          : "text-gray-300"
                      }`}
                    >
                      <Star className="w-6 h-6 fill-current" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Helpful Sections */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Which sections were most helpful?
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {reportSections.map((section) => (
                    <button
                      key={section}
                      onClick={() => toggleHelpfulSection(section)}
                      className={`p-2 text-sm rounded-md border text-left ${
                        feedback.helpful_sections.includes(section)
                          ? "bg-blue-50 border-blue-200 text-blue-700"
                          : "bg-gray-50 border-gray-200 text-gray-700"
                      }`}
                    >
                      {section}
                    </button>
                  ))}
                </div>
              </div>

              {/* Improvement Suggestions */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Suggestions for Improvement
                </label>
                <Textarea
                  placeholder="How could we make this report more useful for your business?"
                  value={feedback.improvement_suggestions}
                  onChange={(e) =>
                    setFeedback((prev) => ({
                      ...prev,
                      improvement_suggestions: e.target.value,
                    }))
                  }
                  rows={3}
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setShowFeedback(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={submitFeedback}
                  disabled={feedback.rating === 0}
                >
                  Submit Feedback
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

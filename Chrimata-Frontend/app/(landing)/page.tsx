import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import "./../../styles/globals.css";
import {
  ArrowRight,
  Users,
  Zap,
  Target,
  MessageSquare,
  Star,
} from "lucide-react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Chrimata
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              href="#features"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Features
            </Link>
            <Link
              href="#use-cases"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Use Cases
            </Link>
            <Link
              href="#testimonials"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Testimonials
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button>Home</Button>
            </Link>
            <Link href="/dashboard">
              <Button>My Dashboard</Button>
            </Link>
            <SignedOut>
              <SignInButton mode="modal" />
              <SignUpButton mode="modal" />
            </SignedOut>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <Badge className="mb-6 bg-blue-100 text-blue-700 hover:bg-blue-100">
            AI-Powered Workflow Discovery
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent leading-tight">
            Transform Your Business with Intelligent Workflow Automation
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Discover personalized AI workflows tailored to your business needs.
            Get actionable insights, model recommendations, and implementation
            strategies in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/workflow-form">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3"
              >
                Start Discovery <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Button size="lg" className="px-8 py-3">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to discover, implement, and optimize AI
              workflows for your business
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Smart Analysis</h3>
                <p className="text-gray-600">
                  AI-powered analysis of your business context, challenges, and
                  goals to identify the most impactful automation opportunities.
                </p>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                  <Zap className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Custom Workflows</h3>
                <p className="text-gray-600">
                  Receive personalized workflow recommendations with specific AI
                  models, tools, and implementation strategies.
                </p>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                  <MessageSquare className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Interactive Chat</h3>
                <p className="text-gray-600">
                  Ask follow-up questions and get detailed explanations about
                  your workflow recommendations through our AI chat.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="use-cases" className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Use Cases</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how businesses across industries are transforming their
              operations
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Customer Support",
                description:
                  "Automate ticket routing, response generation, and sentiment analysis",
                icon: Users,
                color: "blue",
              },
              {
                title: "Sales & Marketing",
                description:
                  "Lead scoring, content generation, and campaign optimization",
                icon: Target,
                color: "purple",
              },
              {
                title: "Operations",
                description:
                  "Process automation, quality control, and predictive maintenance",
                icon: Zap,
                color: "green",
              },
              {
                title: "HR & Recruitment",
                description:
                  "Resume screening, interview scheduling, and employee onboarding",
                icon: Users,
                color: "orange",
              },
              {
                title: "Finance",
                description:
                  "Invoice processing, fraud detection, and financial reporting",
                icon: Target,
                color: "red",
              },
              {
                title: "Product Development",
                description:
                  "User feedback analysis, feature prioritization, and testing automation",
                icon: Zap,
                color: "indigo",
              },
            ].map((useCase, index) => (
              <Card
                key={index}
                className="border-0 shadow-md hover:shadow-lg transition-shadow"
              >
                <CardContent className="p-6">
                  <div
                    className={`w-10 h-10 bg-${useCase.color}-100 rounded-lg flex items-center justify-center mb-4`}
                  >
                    <useCase.icon
                      className={`w-5 h-5 text-${useCase.color}-600`}
                    />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">
                    {useCase.title}
                  </h3>
                  <p className="text-gray-600 text-sm">{useCase.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">What Our Users Say</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Join thousands of businesses already transforming their workflows
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Chen",
                role: "Operations Director",
                company: "TechCorp",
                content:
                  "Chrimata helped us identify automation opportunities we never considered. We've reduced manual work by 60% in just 3 months.",
                rating: 5,
              },
              {
                name: "Michael Rodriguez",
                role: "CEO",
                company: "StartupXYZ",
                content:
                  "The personalized recommendations were spot-on. The implementation guidance made it easy for our small team to get started with AI.",
                rating: 5,
              },
              {
                name: "Emily Johnson",
                role: "Head of Customer Success",
                company: "ServicePro",
                content:
                  "The chat feature is incredibly helpful for understanding the 'why' behind each recommendation. It's like having an AI consultant on demand.",
                rating: 5,
              },
            ].map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="p-8">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star
                        key={i}
                        className="w-5 h-5 text-yellow-400 fill-current"
                      />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-6 italic">
                    "{testimonial.content}"
                  </p>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-gray-500">
                      {testimonial.role} at {testimonial.company}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Start your AI workflow discovery journey today and unlock your
            business potential
          </p>
          <Link href="/workflow-form">
            <Button size="lg">
              {/* className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3" */}
              Get Started Now <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white ">
        {/* py-12 px-4 */}
        <div className="container mx-auto">
          {/* <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Chrimata</span>
              </div>
              <p className="text-gray-400">
                Transforming businesses through intelligent workflow automation.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Use Cases
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white transition-colors">
                    Privacy
                  </Link>
                </li>
              </ul>
            </div>
          </div> */}
          <div className="border-t border-gray-800 p-8 text-center text-gray-400">
            <p>&copy; 2025 Chrimata. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

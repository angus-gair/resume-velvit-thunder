import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, FileText, Upload, Settings, Eye, Download, Sparkles } from "lucide-react"

export default function LandingPage() {
  const steps = [
    {
      icon: Upload,
      title: "Upload Job Description",
      description: "Upload the job posting and select an AI model to extract key requirements",
      color: "text-blue-600",
    },
    {
      icon: FileText,
      title: "Add Source Documents",
      description: "Upload your CV, cover letters, and portfolio documents",
      color: "text-green-600",
    },
    {
      icon: Settings,
      title: "Configure Generation",
      description: "Choose AI model, template, language style, and preferences",
      color: "text-purple-600",
    },
    {
      icon: Sparkles,
      title: "Generate Resume",
      description: "AI creates your tailored resume based on job requirements",
      color: "text-orange-600",
    },
    {
      icon: Eye,
      title: "Review & Edit",
      description: "Preview and make final adjustments to your resume",
      color: "text-red-600",
    },
    {
      icon: Download,
      title: "Export",
      description: "Download your resume as HTML or PDF",
      color: "text-indigo-600",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">ResumeAI</h1>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <Link href="#features" className="text-gray-600 hover:text-gray-900">
                Features
              </Link>
              <Link href="#how-it-works" className="text-gray-600 hover:text-gray-900">
                How it Works
              </Link>
              <Button variant="outline">Sign In</Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">Create the Perfect Resume for Any Job</h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Our AI-powered platform analyzes job descriptions and tailors your resume to match exactly what employers
            are looking for. Stand out from the crowd with personalized, professional resumes.
          </p>
          <Link href="/create">
            <Button size="lg" className="text-lg px-8 py-4">
              Start Creating Your Resume
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our streamlined 6-step process ensures you get a perfectly tailored resume every time
            </p>
          </div>

          {/* Workflow Visualization */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {steps.map((step, index) => {
              const Icon = step.icon
              return (
                <Card key={index} className="relative overflow-hidden group hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg bg-gray-100 ${step.color}`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-500">Step {index + 1}</span>
                        {index < steps.length - 1 && <ArrowRight className="h-4 w-4 text-gray-300 hidden lg:block" />}
                      </div>
                    </div>
                    <CardTitle className="text-lg">{step.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600">{step.description}</CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* CTA */}
          <div className="text-center">
            <Link href="/create">
              <Button size="lg" variant="outline" className="text-lg px-8 py-4">
                Try It Now - It's Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Why Choose ResumeAI?</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <Sparkles className="h-8 w-8 text-blue-600 mb-2" />
                <CardTitle>AI-Powered Matching</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Advanced AI analyzes job descriptions and optimizes your resume for maximum impact.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Settings className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Fully Customizable</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Choose from multiple templates, languages, and styling options to match your preferences.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Download className="h-8 w-8 text-purple-600 mb-2" />
                <CardTitle>Multiple Export Formats</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Download your resume as HTML for web use or PDF for traditional applications.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="h-6 w-6" />
                <span className="text-xl font-bold">ResumeAI</span>
              </div>
              <p className="text-gray-400">Create perfect resumes with AI assistance.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Templates
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Pricing
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Privacy
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="#" className="hover:text-white">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-white">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 ResumeAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

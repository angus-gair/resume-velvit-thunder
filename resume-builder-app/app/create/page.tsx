"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, ArrowRight } from "lucide-react"
import Link from "next/link"

// Step Components
import JobDescriptionStep from "@/components/steps/job-description-step"
import SourceDocumentsStep from "@/components/steps/source-documents-step"
import ConfigurationStep from "@/components/steps/configuration-step"
import GenerationStep from "@/components/steps/generation-step"
import ReviewStep from "@/components/steps/review-step"
import ExportStep from "@/components/steps/export-step"

// Types
interface ResumeData {
  jobDescription?: File
  selectedModel?: string
  sourceDocuments: File[]
  generationConfig: {
    aiModel?: string
    template?: string
    language?: string
    wordLimit?: number
    emphasis?: string[]
  }
  generatedResume?: string
  finalResume?: string
}

const steps = [
  { id: 1, title: "Job Description", component: JobDescriptionStep },
  { id: 2, title: "Source Documents", component: SourceDocumentsStep },
  { id: 3, title: "Configuration", component: ConfigurationStep },
  { id: 4, title: "Generation", component: GenerationStep },
  { id: 5, title: "Review & Edit", component: ReviewStep },
  { id: 6, title: "Export", component: ExportStep },
]

export default function CreateResumePage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [resumeData, setResumeData] = useState<ResumeData>({
    sourceDocuments: [],
    generationConfig: {},
  })

  const progress = (currentStep / steps.length) * 100
  const CurrentStepComponent = steps[currentStep - 1].component

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const updateResumeData = (data: Partial<ResumeData>) => {
    setResumeData((prev) => ({ ...prev, ...data }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <ArrowLeft className="h-5 w-5" />
              <span className="font-medium">Back to Home</span>
            </Link>
            <h1 className="text-xl font-semibold">Create Your Resume</h1>
            <div className="w-24" /> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>
                Step {currentStep} of {steps.length}
              </span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Step Indicators */}
          <div className="flex justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    index + 1 <= currentStep ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {index + 1}
                </div>
                <span className="text-xs text-gray-600 mt-1 text-center max-w-20">{step.title}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <CurrentStepComponent data={resumeData} onUpdate={updateResumeData} onNext={handleNext} />
        </div>
      </main>

      {/* Navigation Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between max-w-4xl mx-auto">
            <Button variant="outline" onClick={handlePrevious} disabled={currentStep === 1}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <Button onClick={handleNext} disabled={currentStep === steps.length}>
              {currentStep === steps.length ? "Complete" : "Next"}
              {currentStep < steps.length && <ArrowRight className="ml-2 h-4 w-4" />}
            </Button>
          </div>
        </div>
      </footer>
    </div>
  )
}

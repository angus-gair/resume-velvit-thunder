"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Sparkles, CheckCircle, Clock, FileText } from "lucide-react"

interface GenerationStepProps {
  data: any
  onUpdate: (data: any) => void
  onNext: () => void
}

export default function GenerationStep({ data, onUpdate, onNext }: GenerationStepProps) {
  const [generationStatus, setGenerationStatus] = useState<"idle" | "generating" | "complete">("idle")
  const [progress, setProgress] = useState(0)
  const [currentTask, setCurrentTask] = useState("")
  const [generatedResume, setGeneratedResume] = useState("")

  const generationTasks = [
    "Analyzing job requirements...",
    "Processing source documents...",
    "Extracting relevant experience...",
    "Matching skills to requirements...",
    "Generating resume content...",
    "Applying template formatting...",
    "Finalizing resume...",
  ]

  const startGeneration = async () => {
    setGenerationStatus("generating")
    setProgress(0)

    // Simulate AI generation process
    for (let i = 0; i < generationTasks.length; i++) {
      setCurrentTask(generationTasks[i])
      setProgress(((i + 1) / generationTasks.length) * 100)

      // Simulate processing time
      await new Promise((resolve) => setTimeout(resolve, 1500))
    }

    // Mock generated resume content
    const mockResume = `
# John Doe
**Software Engineer**

📧 john.doe@email.com | 📱 (555) 123-4567 | 🔗 linkedin.com/in/johndoe

## Professional Summary
Experienced Software Engineer with 5+ years of expertise in React, TypeScript, and Node.js. Proven track record of delivering scalable web applications and leading cross-functional teams. Passionate about creating user-centric solutions and driving technical innovation.

## Technical Skills
- **Frontend:** React, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS
- **Backend:** Node.js, Express, Python, RESTful APIs
- **Databases:** PostgreSQL, MongoDB, Redis
- **Cloud & DevOps:** AWS, Docker, CI/CD, Git
- **Tools:** VS Code, Figma, Jira, Slack

## Professional Experience

### Senior Software Engineer | TechCorp Inc. | 2021 - Present
- Led development of customer-facing web application serving 100K+ users
- Implemented React-based frontend with TypeScript, improving code maintainability by 40%
- Designed and built RESTful APIs using Node.js and Express
- Collaborated with UX team to enhance user experience, resulting in 25% increase in user engagement
- Mentored 3 junior developers and conducted code reviews

### Software Engineer | StartupXYZ | 2019 - 2021
- Developed full-stack web applications using React and Node.js
- Integrated third-party APIs and payment systems
- Optimized database queries, reducing response time by 30%
- Participated in agile development process and sprint planning

## Education
**Bachelor of Science in Computer Science**
University of Technology | 2015 - 2019

## Certifications
- AWS Certified Developer Associate (2022)
- React Developer Certification (2021)
    `

    setGeneratedResume(mockResume)
    onUpdate({ generatedResume: mockResume })
    setGenerationStatus("complete")
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Your Resume</h2>
        <p className="text-gray-600">
          AI is creating your tailored resume based on the job requirements and your documents
        </p>
      </div>

      {/* Generation Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {generationStatus === "idle" && <Sparkles className="h-5 w-5 text-blue-600" />}
            {generationStatus === "generating" && <Clock className="h-5 w-5 text-orange-600 animate-spin" />}
            {generationStatus === "complete" && <CheckCircle className="h-5 w-5 text-green-600" />}
            <span>
              {generationStatus === "idle" && "Ready to Generate"}
              {generationStatus === "generating" && "Generating Resume..."}
              {generationStatus === "complete" && "Generation Complete"}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {generationStatus === "idle" && (
            <div className="text-center space-y-4">
              <p className="text-gray-600">Click the button below to start generating your tailored resume</p>
              <Button onClick={startGeneration} size="lg" className="w-full">
                <Sparkles className="mr-2 h-5 w-5" />
                Generate Resume
              </Button>
            </div>
          )}

          {generationStatus === "generating" && (
            <div className="space-y-4">
              <Progress value={progress} className="h-3" />
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{currentTask}</span>
                <span className="font-medium">{Math.round(progress)}%</span>
              </div>
            </div>
          )}

          {generationStatus === "complete" && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">Resume generated successfully!</span>
              </div>
              <p className="text-gray-600">
                Your resume has been created and is ready for review. You can preview and edit it in the next step.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configuration Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Generation Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p>
                <strong>AI Model:</strong> {data.generationConfig?.aiModel || "Not selected"}
              </p>
              <p>
                <strong>Template:</strong> {data.generationConfig?.template || "Not selected"}
              </p>
              <p>
                <strong>Language:</strong> {data.generationConfig?.language || "Not selected"}
              </p>
            </div>
            <div>
              <p>
                <strong>Source Documents:</strong> {data.sourceDocuments?.length || 0} files
              </p>
              <p>
                <strong>Word Limit:</strong> {data.generationConfig?.wordLimit || "No limit"}
              </p>
              <p>
                <strong>Emphasis Areas:</strong> {data.generationConfig?.emphasis?.length || 0} selected
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Generated Resume Preview */}
      {generationStatus === "complete" && generatedResume && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Generated Resume Preview</span>
            </CardTitle>
            <CardDescription>
              Here's a preview of your generated resume. You can review and edit it in the next step.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm font-mono">{generatedResume}</pre>
            </div>
            <Button onClick={onNext} className="w-full mt-4" size="lg">
              Review & Edit Resume
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

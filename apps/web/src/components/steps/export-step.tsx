"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, FileText, Globe, Share2, CheckCircle, Copy } from "lucide-react"

interface ExportStepProps {
  data: any
  onUpdate: (data: any) => void
  onNext: () => void
}

export default function ExportStep({ data, onUpdate, onNext }: ExportStepProps) {
  const [downloadStatus, setDownloadStatus] = useState<{ [key: string]: "idle" | "downloading" | "complete" }>({})
  const [shareableLink, setShareableLink] = useState("")

  const handleDownload = async (format: "html" | "pdf") => {
    setDownloadStatus((prev) => ({ ...prev, [format]: "downloading" }))

    // Simulate download process
    setTimeout(() => {
      setDownloadStatus((prev) => ({ ...prev, [format]: "complete" }))

      // Create and trigger download
      const content =
        format === "html"
          ? `<!DOCTYPE html><html><head><title>Resume</title></head><body><pre>${data.finalResume || data.generatedResume}</pre></body></html>`
          : data.finalResume || data.generatedResume

      const blob = new Blob([content], { type: format === "html" ? "text/html" : "application/pdf" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `resume.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }, 2000)
  }

  const generateShareableLink = () => {
    const mockLink = "https://resumeai.com/share/abc123def456"
    setShareableLink(mockLink)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const exportOptions = [
    {
      format: "html",
      title: "HTML Format",
      description: "Perfect for online portfolios and web applications",
      icon: Globe,
      features: ["Interactive elements", "Web-optimized", "Easy to customize", "SEO-friendly"],
    },
    {
      format: "pdf",
      title: "PDF Format",
      description: "Standard format for job applications and printing",
      icon: FileText,
      features: ["Print-ready", "Universal compatibility", "Professional appearance", "ATS-friendly"],
    },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Export Your Resume</h2>
        <p className="text-gray-600">Download your tailored resume in your preferred format</p>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {exportOptions.map((option) => {
          const Icon = option.icon
          const status = downloadStatus[option.format] || "idle"

          return (
            <Card key={option.format} className="relative">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Icon className="h-5 w-5" />
                  <span>{option.title}</span>
                </CardTitle>
                <CardDescription>{option.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-1">
                  {option.features.map((feature, index) => (
                    <li key={index} className="flex items-center space-x-2 text-sm">
                      <div className="w-1.5 h-1.5 bg-green-600 rounded-full" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => handleDownload(option.format as "html" | "pdf")}
                  disabled={status === "downloading"}
                  className="w-full"
                  variant={status === "complete" ? "outline" : "default"}
                >
                  {status === "idle" && (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Download {option.format.toUpperCase()}
                    </>
                  )}
                  {status === "downloading" && (
                    <>
                      <Download className="mr-2 h-4 w-4 animate-bounce" />
                      Downloading...
                    </>
                  )}
                  {status === "complete" && (
                    <>
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Downloaded
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Shareable Link */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Share2 className="h-5 w-5" />
            <span>Share Your Resume</span>
          </CardTitle>
          <CardDescription>Generate a shareable link to your resume for easy distribution</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!shareableLink ? (
            <Button onClick={generateShareableLink} variant="outline" className="w-full">
              <Share2 className="mr-2 h-4 w-4" />
              Generate Shareable Link
            </Button>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                <input
                  type="text"
                  value={shareableLink}
                  readOnly
                  className="flex-1 bg-transparent border-none outline-none text-sm"
                />
                <Button size="sm" variant="outline" onClick={() => copyToClipboard(shareableLink)}>
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500">
                This link will be active for 30 days and can be accessed without login
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Resume Summary */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-800">Resume Creation Complete!</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-green-700">Your tailored resume has been successfully created and is ready for use.</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="font-medium text-green-800">Template Used</p>
                <p className="text-green-600">{data.generationConfig?.template || "Modern"}</p>
              </div>
              <div>
                <p className="font-medium text-green-800">AI Model</p>
                <p className="text-green-600">{data.generationConfig?.aiModel || "GPT-4"}</p>
              </div>
              <div>
                <p className="font-medium text-green-800">Language</p>
                <p className="text-green-600">{data.generationConfig?.language || "English (US)"}</p>
              </div>
              <div>
                <p className="font-medium text-green-800">Documents Used</p>
                <p className="text-green-600">{data.sourceDocuments?.length || 0} files</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              <Badge variant="secondary">ATS Optimized</Badge>
              <Badge variant="secondary">Job-Tailored</Badge>
              <Badge variant="secondary">Professional Format</Badge>
              <Badge variant="secondary">Ready to Submit</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle>What's Next?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                1
              </div>
              <div>
                <p className="font-medium">Review and customize</p>
                <p className="text-sm text-gray-600">Make any final adjustments to match your personal style</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                2
              </div>
              <div>
                <p className="font-medium">Submit applications</p>
                <p className="text-sm text-gray-600">Use your tailored resume for job applications</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                3
              </div>
              <div>
                <p className="font-medium">Create more versions</p>
                <p className="text-sm text-gray-600">Generate different resumes for different job types</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Final Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button size="lg" variant="outline" asChild>
          <a href="/">Create Another Resume</a>
        </Button>
        <Button size="lg" asChild>
          <a href="/dashboard">Go to Dashboard</a>
        </Button>
      </div>
    </div>
  )
}

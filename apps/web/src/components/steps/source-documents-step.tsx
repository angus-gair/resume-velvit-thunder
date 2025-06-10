"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X } from "lucide-react"

interface SourceDocumentsStepProps {
  data: any
  onUpdate: (data: any) => void
  onNext: () => void
}

export default function SourceDocumentsStep({ data, onUpdate, onNext }: SourceDocumentsStepProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>(data.sourceDocuments || [])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    const newFiles = [...uploadedFiles, ...files]
    setUploadedFiles(newFiles)
    onUpdate({ sourceDocuments: newFiles })
  }

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index)
    setUploadedFiles(newFiles)
    onUpdate({ sourceDocuments: newFiles })
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split(".").pop()?.toLowerCase()
    return <FileText className="h-5 w-5 text-blue-600" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Source Documents</h2>
        <p className="text-gray-600">
          Upload your existing CV, cover letters, portfolios, and other relevant documents
        </p>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Add Documents</CardTitle>
          <CardDescription>
            Upload documents that contain information about your experience, skills, and achievements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <div className="space-y-2">
              <p className="text-lg font-medium">Drop files here or click to browse</p>
              <p className="text-sm text-gray-500">Supported formats: PDF, DOC, DOCX, TXT • Maximum 10MB per file</p>
            </div>
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileUpload}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Documents ({uploadedFiles.length})</CardTitle>
            <CardDescription>These documents will be used to generate your tailored resume</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getFileIcon(file.name)}
                    <div>
                      <p className="font-medium text-sm">{file.name}</p>
                      <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Document Types Suggestion */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Document Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Essential Documents</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Current CV/Resume</li>
                <li>• Cover Letters</li>
                <li>• LinkedIn Profile Export</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Additional Documents</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Portfolio Descriptions</li>
                <li>• Project Summaries</li>
                <li>• Achievement Lists</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-center">
        <Button onClick={onNext} disabled={uploadedFiles.length === 0} size="lg">
          Continue to Configuration
          {uploadedFiles.length === 0 && <span className="ml-2 text-xs">(Upload at least one document)</span>}
        </Button>
      </div>
    </div>
  )
}

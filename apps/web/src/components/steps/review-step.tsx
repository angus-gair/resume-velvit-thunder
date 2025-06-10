"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Eye, Edit, Save, RefreshCw } from "lucide-react"

interface ReviewStepProps {
  data: any
  onUpdate: (data: any) => void
  onNext: () => void
}

export default function ReviewStep({ data, onUpdate, onNext }: ReviewStepProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedResume, setEditedResume] = useState(data.generatedResume || "")
  const [feedback, setFeedback] = useState("")
  const [isRegenerating, setIsRegenerating] = useState(false)

  const handleSave = () => {
    onUpdate({ finalResume: editedResume })
    setIsEditing(false)
  }

  const handleRegenerate = async () => {
    setIsRegenerating(true)
    // Simulate regeneration with feedback
    setTimeout(() => {
      const updatedResume = editedResume + "\n\n<!-- Updated based on feedback -->"
      setEditedResume(updatedResume)
      onUpdate({ finalResume: updatedResume })
      setIsRegenerating(false)
      setFeedback("")
    }, 3000)
  }

  const resumeSections = [
    { id: "header", title: "Header & Contact", content: "John Doe\nSoftware Engineer\n📧 john.doe@email.com" },
    { id: "summary", title: "Professional Summary", content: "Experienced Software Engineer with 5+ years..." },
    { id: "skills", title: "Technical Skills", content: "Frontend: React, TypeScript, JavaScript..." },
    { id: "experience", title: "Professional Experience", content: "Senior Software Engineer | TechCorp Inc..." },
    { id: "education", title: "Education", content: "Bachelor of Science in Computer Science..." },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Review & Edit Your Resume</h2>
        <p className="text-gray-600">Review the generated resume and make any necessary adjustments</p>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Button variant={isEditing ? "default" : "outline"} onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? <Save className="mr-2 h-4 w-4" /> : <Edit className="mr-2 h-4 w-4" />}
          {isEditing ? "Save Changes" : "Edit Resume"}
        </Button>
        <Button variant="outline">
          <Eye className="mr-2 h-4 w-4" />
          Preview
        </Button>
      </div>

      {/* Resume Content */}
      <Tabs defaultValue="full" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="full">Full Resume</TabsTrigger>
          <TabsTrigger value="sections">By Sections</TabsTrigger>
        </TabsList>

        <TabsContent value="full" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Complete Resume</CardTitle>
              <CardDescription>
                {isEditing ? "Edit your resume content directly" : "Review your complete resume"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <div className="space-y-4">
                  <Textarea
                    value={editedResume}
                    onChange={(e) => setEditedResume(e.target.value)}
                    className="min-h-[500px] font-mono text-sm"
                    placeholder="Edit your resume content here..."
                  />
                  <div className="flex space-x-2">
                    <Button onClick={handleSave}>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </Button>
                    <Button variant="outline" onClick={() => setIsEditing(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-white border rounded-lg p-6 max-h-[500px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm">{editedResume}</pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sections" className="space-y-4">
          {resumeSections.map((section) => (
            <Card key={section.id}>
              <CardHeader>
                <CardTitle className="text-lg">{section.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">{section.content}</pre>
                </div>
                <Button variant="outline" size="sm" className="mt-2">
                  <Edit className="mr-2 h-3 w-3" />
                  Edit Section
                </Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>

      {/* Feedback and Regeneration */}
      <Card>
        <CardHeader>
          <CardTitle>Provide Feedback</CardTitle>
          <CardDescription>Share specific feedback to regenerate parts of your resume</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="e.g., 'Make the professional summary more concise' or 'Add more emphasis on leadership experience'"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            className="min-h-[100px]"
          />
          <Button onClick={handleRegenerate} disabled={!feedback.trim() || isRegenerating} variant="outline">
            {isRegenerating ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Regenerating...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Regenerate with Feedback
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Resume Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Resume Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">487</p>
              <p className="text-sm text-gray-600">Total Words</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">15</p>
              <p className="text-sm text-gray-600">Key Skills</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">8</p>
              <p className="text-sm text-gray-600">Job Matches</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">92%</p>
              <p className="text-sm text-gray-600">ATS Score</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge variant="secondary">React</Badge>
            <Badge variant="secondary">TypeScript</Badge>
            <Badge variant="secondary">Node.js</Badge>
            <Badge variant="secondary">Leadership</Badge>
            <Badge variant="secondary">Problem Solving</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-center">
        <Button onClick={onNext} size="lg">
          Proceed to Export
        </Button>
      </div>
    </div>
  )
}

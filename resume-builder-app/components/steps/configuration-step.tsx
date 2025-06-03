"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface ConfigurationStepProps {
  data: any
  onUpdate: (data: any) => void
  onNext: () => void
}

export default function ConfigurationStep({ data, onUpdate, onNext }: ConfigurationStepProps) {
  const [config, setConfig] = useState(data.generationConfig || {})

  const aiModels = [
    { value: "gpt-4", label: "GPT-4 (Recommended)", description: "Best quality, slower generation" },
    { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo", description: "Good quality, faster generation" },
    { value: "claude-3", label: "Claude 3", description: "Excellent for professional writing" },
    { value: "gemini-pro", label: "Gemini Pro", description: "Great for technical roles" },
  ]

  const templates = [
    {
      id: "modern",
      name: "Modern Professional",
      preview: "/placeholder.svg?height=200&width=150&query=modern resume template",
    },
    {
      id: "classic",
      name: "Classic Traditional",
      preview: "/placeholder.svg?height=200&width=150&query=classic resume template",
    },
    {
      id: "creative",
      name: "Creative Design",
      preview: "/placeholder.svg?height=200&width=150&query=creative resume template",
    },
    {
      id: "minimal",
      name: "Minimal Clean",
      preview: "/placeholder.svg?height=200&width=150&query=minimal resume template",
    },
    {
      id: "executive",
      name: "Executive Level",
      preview: "/placeholder.svg?height=200&width=150&query=executive resume template",
    },
    { id: "tech", name: "Tech Focused", preview: "/placeholder.svg?height=200&width=150&query=tech resume template" },
  ]

  const languages = [
    { value: "en-us", label: "English (US)" },
    { value: "en-gb", label: "English (UK)" },
    { value: "en-au", label: "English (Australia)" },
    { value: "en-ca", label: "English (Canada)" },
  ]

  const emphasisOptions = [
    { id: "achievements", label: "Achievements & Results" },
    { id: "skills", label: "Technical Skills" },
    { id: "experience", label: "Work Experience" },
    { id: "education", label: "Education & Certifications" },
    { id: "leadership", label: "Leadership & Management" },
    { id: "projects", label: "Projects & Portfolio" },
  ]

  const updateConfig = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    onUpdate({ generationConfig: newConfig })
  }

  const toggleEmphasis = (emphasisId: string) => {
    const currentEmphasis = config.emphasis || []
    const newEmphasis = currentEmphasis.includes(emphasisId)
      ? currentEmphasis.filter((id: string) => id !== emphasisId)
      : [...currentEmphasis, emphasisId]
    updateConfig("emphasis", newEmphasis)
  }

  const isConfigComplete = config.aiModel && config.template && config.language

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Configure Resume Generation</h2>
        <p className="text-gray-600">Customize the AI model, template, and preferences for your resume</p>
      </div>

      {/* AI Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>AI Model Selection</CardTitle>
          <CardDescription>Choose the AI model that will generate your resume content</CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup value={config.aiModel} onValueChange={(value) => updateConfig("aiModel", value)}>
            <div className="space-y-3">
              {aiModels.map((model) => (
                <div key={model.value} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                  <RadioGroupItem value={model.value} id={model.value} className="mt-1" />
                  <div className="flex-1">
                    <Label htmlFor={model.value} className="font-medium cursor-pointer">
                      {model.label}
                    </Label>
                    <p className="text-sm text-gray-600 mt-1">{model.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Template Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Resume Template</CardTitle>
          <CardDescription>Select a template that matches your industry and personal style</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className={`border-2 rounded-lg p-3 cursor-pointer transition-all ${
                  config.template === template.id
                    ? "border-blue-600 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => updateConfig("template", template.id)}
              >
                <img
                  src={template.preview || "/placeholder.svg"}
                  alt={template.name}
                  className="w-full h-32 object-cover rounded mb-2"
                />
                <p className="text-sm font-medium text-center">{template.name}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Language and Style */}
      <Card>
        <CardHeader>
          <CardTitle>Language & Style</CardTitle>
          <CardDescription>Set language preferences and content constraints</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="language">Language Style</Label>
            <Select value={config.language} onValueChange={(value) => updateConfig("language", value)}>
              <SelectTrigger className="mt-2">
                <SelectValue placeholder="Select language style" />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="word-limit">Word Count Limit (Optional)</Label>
            <Input
              id="word-limit"
              type="number"
              placeholder="e.g., 500"
              value={config.wordLimit || ""}
              onChange={(e) => updateConfig("wordLimit", Number.parseInt(e.target.value) || undefined)}
              className="mt-2"
            />
            <p className="text-xs text-gray-500 mt-1">Leave empty for no limit</p>
          </div>
        </CardContent>
      </Card>

      {/* Content Emphasis */}
      <Card>
        <CardHeader>
          <CardTitle>Content Emphasis</CardTitle>
          <CardDescription>Select areas to emphasize in your resume (choose 2-4 options)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {emphasisOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={(config.emphasis || []).includes(option.id)}
                  onCheckedChange={() => toggleEmphasis(option.id)}
                />
                <Label htmlFor={option.id} className="cursor-pointer">
                  {option.label}
                </Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Summary */}
      {isConfigComplete && (
        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-800">Configuration Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p>
                <strong>AI Model:</strong> {aiModels.find((m) => m.value === config.aiModel)?.label}
              </p>
              <p>
                <strong>Template:</strong> {templates.find((t) => t.id === config.template)?.name}
              </p>
              <p>
                <strong>Language:</strong> {languages.find((l) => l.value === config.language)?.label}
              </p>
              {config.wordLimit && (
                <p>
                  <strong>Word Limit:</strong> {config.wordLimit} words
                </p>
              )}
              {config.emphasis?.length > 0 && (
                <p>
                  <strong>Emphasis:</strong>{" "}
                  {config.emphasis.map((id: string) => emphasisOptions.find((opt) => opt.id === id)?.label).join(", ")}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-center">
        <Button onClick={onNext} disabled={!isConfigComplete} size="lg">
          Start Resume Generation
        </Button>
      </div>
    </div>
  )
}

## Introduction

You are an AI assistant tasked with creating a Python backend script for Step 4 of a 6-step resume generation workflow. This step is called "Generation" and represents the core of the resume creation process where AI analyzes job requirements and candidate documents to produce a tailored resume.

Your goal is to create a script (`04-resume-generation.py`) that orchestrates AI-powered resume generation by:
1. Retrieving all necessary data from previous steps (job description, documents, configuration)
2. Using AI to analyze and match candidate qualifications with job requirements
3. Generating tailored resume content through structured AI prompts
4. Applying the content to an HTML template
5. Saving the generated resume to the database

The key principle is that **the AI should handle all complex analysis and content generation** through well-structured prompts, rather than implementing complex matching algorithms in code. The script should focus on orchestration, data flow, and API management.

## Context from the UI

The frontend for Step 4 shows:
- **Progress**: 67% Complete (Step 4 of 6)
- **Title**: "Generate Your Resume"
- **Description**: "AI is creating your tailored resume based on the job requirements and your documents"
- **Action**: A "Generate Resume" button to initiate the process
- **Configuration Display**: Shows the selected AI model, template, language, source documents count, word limit, and emphasis areas

## Database Schema Context

Your script will interact with these database tables:
- `sessions`: Tracks workflow progress (current_step should be 3)
- `job_descriptions`: Contains analyzed job posting from Step 1
- `uploaded_documents`: Contains user's CV, cover letters, etc. from Step 2
- `generation_config`: Contains AI model selection and preferences from Step 3
- `generated_resumes`: Where you'll save the generated resume

## Core Implementation Requirements

### 1. Data Retrieval Phase

Create a method to gather all necessary data:
```python
def gather_generation_data(self, session_id: str) -> dict:
    """Retrieve all data needed for resume generation."""
    # Get job description with parsed requirements
    # Get all uploaded documents
    # Get configuration settings
    # Return organized data structure
```

### 2. AI Analysis Prompts

Implement separate AI prompts for different analysis tasks:

#### Prompt 1: Skills and Experience Extraction
Create a prompt that asks the AI to:
- Extract all skills, experiences, and achievements from uploaded documents
- Categorize them (technical skills, soft skills, achievements, etc.)
- Identify measurable results and impact
- Return structured JSON

#### Prompt 2: Job Requirements Matching
Create a prompt that asks the AI to:
- Analyze job requirements against candidate profile
- Score relevance of each experience/skill to the job
- Identify gaps and strengths
- Prioritize content based on job requirements
- Return match analysis with scores

#### Prompt 3: Content Generation
Create a prompt that asks the AI to:
- Generate tailored resume content based on:
  - Job requirements
  - Candidate profile
  - Configuration (language style, focus areas, word limit)
  - Template structure
- Create sections: summary, experience, skills, education
- Optimize for ATS keywords
- Ensure professional tone and consistency

#### Prompt 4: ATS Optimization
Create a prompt that asks the AI to:
- Review generated content for ATS compatibility
- Ensure keyword density is appropriate
- Verify all required skills are mentioned
- Suggest improvements if needed

### 3. Template Integration

Load and populate the HTML template:
```python
def apply_template(self, generated_content: dict, template_path: str) -> str:
    """Apply generated content to HTML template."""
    # Load template from file
    # Replace placeholders with generated content
    # Handle missing sections gracefully
    # Return complete HTML
```

### 4. Quality Scoring

Implement scoring based on AI analysis:
```python
def calculate_scores(self, match_analysis: dict, ats_analysis: dict) -> tuple:
    """Calculate match and ATS scores."""
    # Extract scores from AI analysis
    # Normalize to 0-100 range
    # Return (match_score, ats_score)
```

### 5. Error Handling

Handle these specific scenarios:
- Missing job description
- No uploaded documents
- API rate limits
- Invalid API keys
- Template parsing errors
- AI response parsing errors

## AI Model Integration

### For OpenAI (GPT-4, GPT-3.5 Turbo)
```python
import openai

def call_openai_api(self, prompt: str, model: str) -> str:
    """Call OpenAI API with structured prompt."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional resume writer with expertise in ATS optimization."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content
```

### For Anthropic (Claude models)
```python
import anthropic

def call_anthropic_api(self, prompt: str, model: str) -> str:
    """Call Anthropic API with structured prompt."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    
    return response.content[0].text
```

### For Open Source (Placeholder)
```python
def call_opensource_api(self, prompt: str, model: str) -> str:
    """Placeholder for open source model integration."""
    # Could integrate with Ollama, HuggingFace, etc.
    raise NotImplementedError("Open source model integration pending")
```

## Structured Prompt Templates

### Skills Extraction Prompt Template
```
Analyze the following documents and extract all relevant information for a resume:

Documents:
{documents_content}

Please extract and categorize:
1. All technical skills with proficiency levels
2. Soft skills demonstrated
3. Work experiences with:
   - Company, role, dates
   - Key responsibilities
   - Measurable achievements (include numbers/percentages)
4. Education and certifications
5. Notable projects with outcomes

Return as JSON in this structure:
{
  "technical_skills": [...],
  "soft_skills": [...],
  "experiences": [...],
  "education": [...],
  "projects": [...],
  "achievements": [...]
}
```

### Job Matching Prompt Template
```
Compare the candidate profile with the job requirements:

Job Requirements:
{job_requirements}

Candidate Profile:
{candidate_profile}

Please analyze:
1. How well each experience matches the job requirements (score 0-100)
2. Which skills are most relevant to this role
3. Any gaps in requirements
4. Suggested emphasis areas

Focus Areas Selected: {focus_areas}

Return as JSON with match scores and recommendations.
```

### Content Generation Prompt Template
```
Generate a tailored resume based on this analysis:

Job Title: {job_title}
Company: {company}
Match Analysis: {match_analysis}
Language Style: {language_style}
Word Limit: {word_limit}
Focus Areas: {focus_areas}

Generate the following sections:
1. Professional Summary (2-3 sentences, highlighting best matches)
2. Work Experience (prioritized by relevance, include metrics)
3. Skills (categorized, ATS-optimized)
4. Education
5. Additional sections as appropriate

Ensure:
- Keywords from job description are naturally incorporated
- Tone matches the selected language style
- Content emphasizes the selected focus areas
- Total word count stays within limit if specified
```

## Command-Line Interface

```python
def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-powered resume (Step 4)"
    )
    
    parser.add_argument('session_id', nargs='?', help='Session ID from previous steps')
    parser.add_argument('--preview', action='store_true', help='Preview without saving')
    parser.add_argument('--force-regenerate', action='store_true', help='Regenerate even if exists')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--test', action='store_true', help='Run with test data')
    
    args = parser.parse_args()
```

## Output Format

```json
{
  "status": "success",
  "message": "Resume generated successfully",
  "resume": {
    "id": 1,
    "session_id": "session_abc123",
    "version": 1,
    "match_score": 85.5,
    "ats_score": 92.0,
    "word_count": 687,
    "sections": {
      "summary": "Generated professional summary...",
      "experience": "Generated experience section...",
      "skills": "Generated skills section...",
      "education": "Generated education section..."
    },
    "html_content": "<!DOCTYPE html>...",
    "generation_time": 4.2,
    "model_used": "gpt-4",
    "api_calls_made": 4,
    "tokens_used": 3500
  }
}
```

## Testing Strategy

### Test Data Setup
1. Use existing job analysis from `applications/job_analysis_20250602_171634.md`
2. Use sample documents from `data/sample_docs/`
3. Create test configuration with `03-configuration.py --test`
4. Use HTML template from `data/sample_docs/resume-template.html`

### Test Scenarios
```python
# Test 1: Basic generation with all data
python 04-resume-generation.py --test

# Test 2: Preview mode
python 04-resume-generation.py session_abc123 --preview

# Test 3: Debug mode with detailed output
python 04-resume-generation.py session_abc123 --debug

# Test 4: Force regeneration
python 04-resume-generation.py session_abc123 --force-regenerate
```

## Implementation Best Practices

1. **AI Prompt Management**
   - Store prompts as templates with clear placeholders
   - Version your prompts for consistency
   - Log all AI interactions for debugging

2. **Performance Optimization**
   - Cache AI responses during development
   - Implement exponential backoff for retries
   - Monitor token usage to optimize costs

3. **Error Recovery**
   - Save partial progress to allow resumption
   - Provide clear error messages
   - Implement fallback strategies

4. **Security**
   - Never log API keys
   - Sanitize all content for HTML injection
   - Validate all inputs

5. **Maintainability**
   - Separate AI provider implementations
   - Use configuration for prompt templates
   - Document all AI response formats

## Key Success Factors

1. **Let AI Do the Heavy Lifting**: Don't implement complex matching algorithms—use AI prompts
2. **Structured Prompts**: Use clear, structured prompts with expected output formats
3. **Multiple Specialized Prompts**: Break down the task into focused AI calls
4. **Robust Error Handling**: Handle API failures gracefully
5. **Quality Validation**: Always validate AI responses before using them

Your implementation should create a robust, AI-powered resume generation system that produces high-quality, tailored resumes while maintaining the flexibility to work with different AI providers and adapt to various job requirements.
```

This comprehensive prompt:
1. Starts with a clear introduction explaining the AI's purpose
2. Provides context from the UI showing what Step 4 looks like
3. Emphasizes using AI for complex analysis through multiple specialized prompts
4. Includes specific prompt templates for different tasks
5. Covers all technical requirements while focusing on AI orchestration
6. Provides detailed implementation guidance and best practices

The key principle throughout is that the script should orchestrate AI calls rather than implement complex logic locally, making the system more maintainable and leveraging AI's capabilities for analysis and content generation.

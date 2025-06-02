# Prompt for 03-configuration.py

You are tasked with creating a backend script that handles the configuration step (Step 3) of a resume generation application. This script manages AI model selection, template choices, language preferences, and content emphasis settings. Follow these instructions carefully:

## 1. Configuration Components

Based on the frontend interface, implement the following configuration sections:

### AI Model Selection
Handle the following AI models with their characteristics:
- **GPT-4** (Recommended): Best quality, slower generation
- **GPT-3.5 Turbo**: Good quality, faster generation  
- **Claude 3.5 Sonnet**: Latest Anthropic model, excellent for professional writing
- **Claude 3 Opus**: Most capable Anthropic model, best for complex resumes
- **Claude 3 Haiku**: Fast Anthropic model, good for quick iterations
- **Gemini Pro**: Great for technical roles
- **Open Source Model** (Placeholder): Local LLM option for privacy-conscious users

### Model Sync Mode
For applicable models, provide sync/async options:
- **Sync Mode**: Sequential processing, immediate results
- **Async Mode**: Parallel processing, better for batch operations
- Default to sync mode for single resume generation

### Resume Template Selection
Support these template options:
- **Modern Professional**: Clean, contemporary design
- **Classic Traditional**: Conservative, formal layout
- **Creative Design**: Visually appealing, creative fields
- **Minimal Clean**: Simple, distraction-free format
- **Executive Level**: Senior position focused
- **Tech Focused**: Technical role optimized

### Language & Style Configuration
- **Language Style**: Dropdown selection (Professional, Conversational, Technical, Creative)
- **Word Count Limit**: Optional numeric input (leave empty for no limit)

### Content Emphasis Areas
Multi-select checkboxes for focus areas:
- Achievements & Results
- Work Experience  
- Leadership & Management
- Technical Skills
- Education & Certifications
- Projects & Portfolio

## 2. Database Integration

The script must integrate with the existing SQLite database using the `generation_config` table:

```sql
CREATE TABLE generation_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    ai_model TEXT DEFAULT 'gpt-4',
    template_name TEXT DEFAULT 'professional',
    language_style TEXT DEFAULT 'professional',
    focus_areas JSON,
    custom_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
)
```

## 3. Environment Variable Integration

The script must:
- Access environment variables from .env file using python-dotenv
- Support API keys for multiple providers:
  - ANTHROPIC_API_KEY for Claude models
  - OPENAI_API_KEY for GPT models
  - GOOGLE_API_KEY for Gemini
  - PERPLEXITY_API_KEY (optional)
- Fall back to environment variables if not provided in arguments
- Validate API key availability for selected model

## 4. Core Functionality Requirements

### Configuration Collection
- Implement a function to collect configuration settings from command-line arguments or interactive prompts
- Validate all input parameters
- Provide sensible defaults for optional settings
- Store sync mode preference in custom_instructions JSON field

### Database Operations
- Save configuration to the `generation_config` table
- Update session step to 3 upon successful configuration
- Handle existing configurations (update vs create new)
- Retrieve session data from previous steps

### Validation Logic
- Ensure selected AI model is supported
- Validate API key exists for selected model provider
- Validate template name against available templates
- Check that focus areas are valid options
- Validate word count limit (if provided)
- Verify sync mode compatibility with selected model

### Error Handling
- Handle database connection errors
- Validate session existence
- Provide clear error messages for invalid inputs
- Check API key availability for selected models

## 5. Script Interface

The script should support both command-line and interactive modes:

### Command-line Arguments
```bash
python 03-configuration.py <session_id> [options]
```

**Required:**
- `session_id`: The session ID from previous steps

**Optional:**
- `--ai-model`: AI model selection (gpt-4, gpt-3.5-turbo, claude-3.5-sonnet, claude-3-opus, claude-3-haiku, gemini-pro, open-source)
- `--sync-mode`: Enable sync mode for applicable models (default: True)
- `--template`: Template name (modern-professional, classic-traditional, creative-design, minimal-clean, executive-level, tech-focused)
- `--language-style`: Language style (professional, conversational, technical, creative)
- `--word-limit`: Word count limit (integer)
- `--focus-areas`: Comma-separated focus areas
- `--custom-instructions`: Additional custom instructions
- `--interactive`: Run in interactive mode
- `--test`: Run with test data

### Interactive Mode
If no options provided or `--interactive` flag used:
- Present user-friendly prompts for each configuration option
- Show available choices for each selection
- Display which models require API keys
- Allow users to skip optional settings
- Confirm final configuration before saving

## 6. Output Format

The script should output a JSON response with the following structure:

```json
{
  "status": "success" | "error",
  "message": "Description of the result or error",
  "configuration": {
    "session_id": "session_id",
    "ai_model": "selected_model",
    "sync_mode": true | false,
    "template_name": "selected_template", 
    "language_style": "selected_style",
    "word_limit": null | integer,
    "focus_areas": ["area1", "area2", ...],
    "custom_instructions": {
      "sync_mode": true | false,
      "additional_instructions": "text" | null
    },
    "config_id": integer
  }
}
```

## 7. Integration Requirements

### Database Utilities
- Use the existing `DatabaseManager` class from `database_utils.py`
- Follow the established database connection patterns
- Implement proper error handling and transaction management

### Session Management
- Verify session exists before proceeding
- Update session step and timestamp
- Handle session state validation
- Retrieve previous step data for context

### Validation Rules
- AI Model: Must be one of the supported models
- API Key: Must exist for selected model provider
- Template: Must be one of the available templates  
- Language Style: Must be valid style option
- Focus Areas: Must be from the predefined list
- Word Limit: Must be positive integer if provided
- Sync Mode: Only available for certain models

## 8. Model-Specific Configuration

### Claude Models
```python
CLAUDE_MODELS = {
    'claude-3.5-sonnet': {
        'name': 'Claude 3.5 Sonnet',
        'provider': 'anthropic',
        'supports_sync': True,
        'description': 'Latest model, best balance of speed and quality'
    },
    'claude-3-opus': {
        'name': 'Claude 3 Opus',
        'provider': 'anthropic', 
        'supports_sync': True,
        'description': 'Most capable model, best for complex resumes'
    },
    'claude-3-haiku': {
        'name': 'Claude 3 Haiku',
        'provider': 'anthropic',
        'supports_sync': True,
        'description': 'Fastest model, good for quick iterations'
    }
}
```

### Open Source Placeholder
```python
'open-source': {
    'name': 'Open Source Model',
    'provider': 'local',
    'supports_sync': True,
    'description': 'Local LLM (requires separate setup)',
    'note': 'Placeholder for future implementation'
}
```

## 9. Additional Features

### Configuration Validation
- Check API key availability before saving
- Validate model-template compatibility
- Warn about sync mode limitations
- Provide recommendations based on job type

### Default Handling
- Use GPT-4 as default if no model specified
- Default to sync mode for better user experience
- Set professional language style as default
- Auto-select focus areas based on job description

### Environment Check
- Verify required environment variables
- Display available models based on API keys
- Provide setup instructions for missing keys
- Support .env file loading

## 10. Testing Support

Include a test mode that:
- Uses sample configuration data
- Tests with mock API keys
- Validates all model options
- Tests sync/async mode switching
- Provides example usage scenarios

Your final output should be a complete Python script that implements all these functionalities with clear comments explaining key parts of the code. The script should be robust, user-friendly, and integrate seamlessly with the existing resume generation workflow while maintaining access to environment variables and supporting the enhanced model options requested.

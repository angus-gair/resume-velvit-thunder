# Configuration Component (Step 3) - Resume Generation

## Overview
The configuration component (`03-configuration.py`) handles the third step in the resume generation workflow. It allows users to configure AI model selection, resume templates, language styles, and content emphasis areas.

## Features

### AI Model Support
- **GPT Models**: GPT-4 (recommended), GPT-3.5 Turbo
- **Claude Models**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Gemini Pro**: For technical roles
- **Open Source**: Placeholder for local LLM implementations

### Sync Mode
- Available for all supported models
- Enables sequential processing for immediate results
- Default enabled for better user experience

### Resume Templates
- Modern Professional - Clean, contemporary design
- Classic Traditional - Conservative, formal layout
- Creative Design - Visually appealing, creative fields
- Minimal Clean - Simple, distraction-free format
- Executive Level - Senior position focused
- Tech Focused - Technical role optimized

**Note**: Currently all templates use the same base template file (`templates/base_template.html`). The template selection is preserved for future expansion when unique templates are developed for each style.

### Language Styles
- Professional - Formal business language
- Conversational - Friendly and approachable
- Technical - Industry-specific terminology
- Creative - Expressive and unique

### Content Emphasis Areas
- Achievements & Results
- Work Experience
- Leadership & Management
- Technical Skills
- Education & Certifications
- Projects & Portfolio

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with your API keys:
```env
# For GPT models
OPENAI_API_KEY=your-openai-api-key

# For Claude models
ANTHROPIC_API_KEY=your-anthropic-api-key

# For Gemini
GOOGLE_API_KEY=your-google-api-key

# Optional
PERPLEXITY_API_KEY=your-perplexity-api-key
```

## Usage

### Test Mode
```bash
python 03-configuration.py --test
```

### Interactive Mode
```bash
python 03-configuration.py session_abc123 --interactive
```

### Command-Line Mode
```bash
python 03-configuration.py session_abc123 \
  --ai-model claude-3.5-sonnet \
  --sync-mode \
  --template modern-professional \
  --language-style professional \
  --word-limit 500 \
  --focus-areas achievements_results,technical_skills \
  --custom-instructions "Focus on leadership experience"
```

## Command-Line Arguments

| Argument | Description | Options/Type |
|----------|-------------|--------------|
| `session_id` | Session ID from document upload (required) | string |
| `--ai-model` | AI model for generation | gpt-4, gpt-3.5-turbo, claude-3.5-sonnet, claude-3-opus, claude-3-haiku, gemini-pro, open-source |
| `--sync-mode` | Enable sync mode | flag (default: True) |
| `--template` | Resume template | modern-professional, classic-traditional, creative-design, minimal-clean, executive-level, tech-focused |
| `--language-style` | Language style | professional, conversational, technical, creative |
| `--word-limit` | Word count limit | integer (optional) |
| `--focus-areas` | Comma-separated focus areas | See focus areas list above |
| `--custom-instructions` | Additional instructions | string (optional) |
| `--interactive` | Run in interactive mode | flag |
| `--test` | Run with test data | flag |

## Output Format

The script outputs JSON with the configuration details:

```json
{
  "status": "success",
  "message": "Configuration saved successfully",
  "configuration": {
    "session_id": "session_5d4600df7970",
    "ai_model": "claude-3.5-sonnet",
    "sync_mode": true,
    "template_name": "modern-professional",
    "language_style": "professional",
    "word_limit": null,
    "focus_areas": ["achievements_results", "technical_skills"],
    "custom_instructions": {
      "sync_mode": true,
      "template_file": "templates/base_template.html",
      "additional_instructions": "Focus on leadership experience"
    },
    "config_id": 2
  }
}
```

## Database Integration

The configuration is saved to the `generation_config` table:
- Links to session from previous steps
- Stores all configuration options
- Updates session step to 3
- Maintains configuration history

## API Key Management

The script automatically:
- Loads API keys from environment variables
- Validates key availability for selected models
- Shows only available models based on API keys
- Provides clear error messages for missing keys

## Error Handling

The script handles:
- Invalid session IDs
- Missing API keys
- Invalid configuration options
- Database connection issues
- Session state validation

## Integration with Workflow

1. **Prerequisites**: Complete Step 2 (document upload) first
2. **Input**: Uses session ID from previous step
3. **Output**: Configuration ID for Step 4 (generation)
4. **Next Step**: Resume generation using saved configuration

## Troubleshooting

### No Models Available
- Ensure API keys are set in environment or `.env` file
- Check key format and validity
- Use `--test` mode with open-source model

### Session Not Found
- Verify session ID from Step 2
- Ensure Step 2 completed successfully
- Check database connectivity

### Configuration Not Saving
- Verify database file exists
- Check write permissions
- Review error messages for specifics

## Development Notes

### Adding New Models
1. Add model definition to `AI_MODELS` dictionary
2. Include provider and API key information
3. Set `supports_sync` flag appropriately
4. Update documentation

### Customizing Templates
1. Add new template to `TEMPLATES` dictionary
2. Provide descriptive name and purpose
3. Update frontend integration accordingly
4. When unique templates are available:
   - Update `TEMPLATE_FILES` mapping to point to specific template files
   - Each template can have its own HTML/CSS design
   - Template files should be placed in the `templates/` directory

### Extending Focus Areas
1. Add to `FOCUS_AREAS` list
2. Update `FOCUS_AREA_NAMES` mapping
3. Ensure database compatibility 
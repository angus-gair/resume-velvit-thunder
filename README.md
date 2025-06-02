# Claude Job Analysis Tool

A production-ready Python script that analyzes job postings using Claude AI to extract key information, clean formatting, and identify required skills and experience. Enhanced with MCP (Model Context Protocol) servers for advanced capabilities.

## Features

- 🤖 Uses Claude AI (Anthropic) for intelligent job posting analysis
- 📝 Extracts and formats job requirements, skills, and qualifications
- 🔒 Secure API key handling via environment variables
- 📁 Configurable output directory and file naming
- 🎯 Command-line interface with multiple options
- 📊 Comprehensive error handling and logging
- 🌍 Support for multiple file encodings
- 🔌 **MCP Server Integration** for enhanced AI capabilities

## MCP Servers Included

- **Memory** - Persistent memory storage across sessions
- **Sequential Thinking** - Advanced reasoning and problem-solving
- **TaskMaster AI** - Project task management and planning
- **Perplexity Ask** - Web search and research capabilities
- **Memory Bank** - Project-specific memory management
- **Context7** - Library documentation and code examples
- **Puppeteer** - Web automation and scraping
- **Playwright** - Advanced web automation

## Prerequisites

- Python 3.7 or higher
- Node.js 16 or higher (for MCP servers)
- Anthropic API key (get one at https://console.anthropic.com)
- Optional: Additional API keys for enhanced MCP functionality

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd resume-velvit-thunder
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MCP servers:
```powershell
.\setup-mcp.ps1
```

4. Configure your API keys (see Configuration section below)

## Configuration

### Method 1: Environment Variables (Recommended)

Copy the example environment file and configure your API keys:
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
# Core API Keys for Job Analysis
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Job Analysis Configuration
JOB_ANALYSIS_OUTPUT_DIR=./applications
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# MCP Server API Keys (optional but recommended)
OPENAI_API_KEY=your-openai-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
MISTRAL_API_KEY=your-mistral-api-key-here
```

### Method 2: Direct Environment Variables

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Method 3: Configuration File

Create a `config.json` file:
```json
{
    "api_key": "your-anthropic-api-key-here",
    "output_dir": "./applications",
    "model": "claude-3-5-sonnet-20241022"
}
```

### MCP Configuration

The MCP servers are configured in `mcp-config.json`. To use them with Claude Desktop:

1. Copy the absolute path to `mcp-config.json`
2. Add it to your Claude Desktop settings under "Developer" → "MCP Servers"
3. Restart Claude Desktop

## Usage

### Basic Usage

Analyze a job posting file:
```bash
python 01-job-description-analysis.py job_posting.txt
```

Or use the helper scripts:
```powershell
# PowerShell
.\analyze-job.ps1

# Windows Command Prompt  
analyze-job.bat paste.txt
```

### Advanced Usage

```bash
# Specify output directory
python 01-job-description-analysis.py job_posting.txt -o ./my-applications

# Use a configuration file
python 01-job-description-analysis.py job_posting.txt --config config.json

# Override API key from command line
python 01-job-description-analysis.py job_posting.txt -k "your-api-key"

# Use a different Claude model
python 01-job-description-analysis.py job_posting.txt -m "claude-3-opus-20240229"

# Enable verbose logging
python 01-job-description-analysis.py job_posting.txt --verbose
```

### Command-line Options

- `job_file` (required): Path to the job posting text file
- `-o, --output`: Output directory (default: ./applications)
- `-c, --config`: Path to configuration file
- `-k, --api-key`: Anthropic API key (overrides environment)
- `-m, --model`: Claude model to use
- `-v, --verbose`: Enable verbose logging

## MCP Server Setup

### Quick Setup

Run the setup script to configure MCP servers:
```powershell
.\setup-mcp.ps1
```

### Manual Setup

1. Create MCP data directories:
```bash
mkdir -p mcp-data/memory-bank
echo '{}' > mcp-data/memory.json
```

2. Install Node.js dependencies (optional pre-installation):
```bash
npx -y @modelcontextprotocol/server-memory
npx -y task-master-ai
# ... other servers
```

3. Configure Claude Desktop with `mcp-config.json`

### Available MCP Servers

| Server | Purpose | API Key Required |
|--------|---------|------------------|
| memory | Persistent memory storage | No |
| sequential-thinking | Advanced reasoning | No |
| taskmaster-ai | Task management | Anthropic, OpenAI, etc. |
| perplexity-ask | Web search | Perplexity |
| memory-bank | Project memory | No |
| context7 | Library docs | No |
| puppeteer | Web automation | No |
| playwright | Advanced web automation | No |

## Output

The tool generates timestamped markdown files containing:

1. **Cleaned Job Posting**: A formatted version of the job posting with:
   - Clear section headers
   - Removed HTML/formatting clutter
   - Organized structure

2. **Skills and Experience**: Extracted requirements including:
   - Technical skills
   - Soft skills
   - Experience requirements
   - Educational requirements
   - Technologies and tools

Output files are named: `job_analysis_[job_title]_[timestamp].md`

## Example Output Structure

```markdown
<cleaned_job_posting>
# Business Analyst

**Company:** Example Corp
**Location:** Sydney, NSW
**Type:** Full-time

## Job Description
[Cleaned job description...]

## Responsibilities
- [Responsibility 1]
- [Responsibility 2]
...
</cleaned_job_posting>

<skills_and_experience>
## Required Skills

### Technical Skills
- Business analysis methodologies
- Requirements gathering
- UX collaboration
...

### Experience Requirements
- 3+ years as Business Analyst
- Experience with web services
...
</skills_and_experience>
```

## Error Handling

The script includes comprehensive error handling for:
- Missing or invalid API keys
- File not found errors
- Encoding issues
- API rate limits
- Network connectivity issues
- MCP server connection issues

## Security Best Practices

1. **Never commit API keys** to version control
2. Use environment variables for sensitive data
3. Add `.env` to your `.gitignore` file
4. Rotate API keys regularly
5. Use the least privileged API keys
6. **Secure MCP Configuration**: API keys in `mcp-config.json` use environment variable references

## Troubleshooting

### Unicode Decode Error
The script automatically tries multiple encodings (UTF-8, Latin-1, CP1252) to handle various file formats.

### API Key Not Found
Ensure your API key is properly set in one of the supported methods (environment variable, config file, or command line).

### Rate Limiting
If you encounter rate limits, wait a few moments before retrying. Consider upgrading your Anthropic plan for higher limits.

### MCP Server Issues
- Ensure Node.js is installed: `node --version`
- Check MCP data directories exist: `./mcp-data/`
- Verify environment variables are set
- Restart Claude Desktop after MCP configuration changes

### Node.js Not Found
Install Node.js from https://nodejs.org/ (version 16 or higher recommended)

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines. Use `black` for formatting:
```bash
black 01-job-description-analysis.py
```

### MCP Development
- MCP servers are configured in `mcp-config.json`
- Data is stored in `./mcp-data/`
- Logs are available in Claude Desktop's developer console

## Project Structure

```
resume-velvit-thunder/
├── 01-job-description-analysis.py  # Main analysis script
├── mcp-config.json                 # MCP server configuration
├── env.example                     # Environment variables template
├── config.example.json             # Configuration file template
├── setup-mcp.ps1                   # MCP setup script
├── analyze-job.ps1                 # PowerShell helper script
├── analyze-job.bat                 # Windows batch helper script
├── requirements.txt                # Python dependencies
├── mcp-data/                       # MCP server data
│   ├── memory.json                 # Memory server data
│   └── memory-bank/                # Memory bank data
├── applications/                   # Analysis output directory
└── README.md                       # This file
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review closed issues on GitHub
3. Open a new issue with detailed information

## Changelog

### v2.0.0 (2024-01-xx)
- Added MCP server integration
- Enhanced AI capabilities with multiple servers
- Improved security with environment variable references
- Added automated setup scripts

### v1.0.0 (2024-01-xx)
- Initial production release
- Secure API key handling
- Comprehensive error handling
- Command-line interface
- Configurable options 
# Cursor MCP Configuration

This directory contains configuration for Cursor's Model Context Protocol (MCP) servers.

## Setup Instructions

1. **Copy the template file:**
   ```bash
   cp mcp.json.template mcp.json
   ```

2. **Add your API keys:**
   Edit `mcp.json` and replace the placeholder values with your actual API keys:
   - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key
   - `PERPLEXITY_API_KEY`: Your Perplexity API key  
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_API_KEY`: Your Google API key
   - Other API keys as needed

3. **Security Note:**
   - The `mcp.json` file is automatically ignored by git (see `.gitignore`)
   - Never commit actual API keys to version control
   - Keep your API keys secure and rotate them regularly

## Available MCP Servers

- **task-master-ai**: AI-powered task management and project planning

## Troubleshooting

If you encounter issues:
1. Verify your API keys are valid and have sufficient credits
2. Check that the MCP server packages are installed
3. Restart Cursor after making configuration changes

## Template File

The `mcp.json.template` file contains the structure with placeholder values. Use this as a reference for the expected format. 
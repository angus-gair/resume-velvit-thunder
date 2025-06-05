#!/usr/bin/env python3
"""
Claude Job Analysis Script
Analyzes job postings using Claude AI to extract key information and requirements.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Please run: pip install anthropic")
    sys.exit(1)


# Configure logging
def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


class JobAnalyzer:
    """
    A class to analyze job postings using the Claude AI API.
    
    This class provides methods to send job postings to the Claude AI API and extract
    structured information such as required skills, experience, and qualifications.
    
    Example:
        >>> from pathlib import Path
        >>> analyzer = JobAnalyzer(api_key="your-api-key")
        >>> with open("job_posting.txt") as f:
        ...     job_content = f.read()
        >>> analysis = analyzer.analyze_job_posting(job_content)
        >>> print(analysis)  # Prints the analyzed job posting
    
    Attributes:
        client (anthropic.Anthropic): The Anthropic API client
        model (str): The Claude model to use for analysis
        logger (logging.Logger): Logger instance for the class
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> None:
        """
        Initialize the JobAnalyzer with API credentials and model selection.
        
        Args:
            api_key: Anthropic API key for authentication. Can be obtained from
                    https://console.anthropic.com/settings/keys
            model: Name of the Claude model to use for analysis. Defaults to
                  "claude-3-5-sonnet-20241022". Other options include:
                  - "claude-3-opus-20240229" (most capable)
                  - "claude-3-sonnet-20240229" (balanced)
                  - "claude-3-haiku-20240307" (fastest)
        
        Raises:
            anthropic.AuthenticationError: If the API key is invalid
            ValueError: If the API key is empty or None
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized JobAnalyzer with model: {model}")
    
    def analyze_job_posting(self, job_content: str) -> str:
        """
        Analyze a job posting and extract structured information using Claude AI.
        
        This method sends the job posting to the Claude API and returns the analyzed
        content including a cleaned version of the posting and extracted requirements.
        
        Args:
            job_content: The raw job posting text to analyze. Should be a string
                       containing the complete job description and requirements.
        
        Returns:
            str: A string containing the analysis results in the following format:
                <cleaned_job_posting>
                [Formatted job posting in Markdown]
                </cleaned_job_posting>
                
                <skills_and_experience>
                [Extracted skills, experience, and requirements in Markdown]
                </skills_and_experience>
        
        Raises:
            anthropic.APIError: If there's an error with the Claude API request
            ValueError: If the job_content is empty or too long (>100,000 characters)
            Exception: For any other unexpected errors during processing
            
        Example:
            >>> analyzer = JobAnalyzer(api_key="your-api-key")
            >>> with open("job_posting.txt") as f:
            ...     job_text = f.read()
            >>> result = analyzer.analyze_job_posting(job_text)
            >>> print(result)  # Prints the analyzed content
        """
        if not job_content or not job_content.strip():
            raise ValueError("Job content cannot be empty")
            
        if len(job_content) > 100000:  # Prevent sending excessively large content
            raise ValueError("Job content exceeds maximum allowed length (100,000 characters)")
            
        self.logger.debug(f"Analyzing job posting ({len(job_content)} characters)")
        prompt = self._create_prompt(job_content)
        
        try:
            self.logger.info("Sending request to Claude API...")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more deterministic output
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not message.content or not message.content[0].text:
                raise ValueError("Empty response received from Claude API")
                
            self.logger.debug("Successfully received analysis from Claude API")
            return message.content[0].text
            
        except anthropic.APIError as e:
            self.logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during job analysis: {e}")
            raise
    
    def _create_prompt(self, job_content: str) -> str:
        """
        Create a detailed prompt for Claude to analyze a job posting.
        
        This internal method constructs the system and user prompts that guide Claude
        in analyzing the job posting. The prompt is designed to extract structured
        information while maintaining the original content's meaning.
        
        Args:
            job_content: The raw job posting text to be analyzed
            
        Returns:
            str: A formatted prompt string for the Claude API
            
        Note:
            The prompt is specifically crafted to work with Claude's capabilities
            and follows best practices for instruction-following models.
        """
        # Escape any XML/HTML-like tags in the job content to prevent prompt injection
        job_content = job_content.replace("<", "&lt;").replace(">", "&gt;")
        
        return f"""
You are an AI assistant tasked with analyzing a job posting and extracting key information. Your goal is to provide a clean version of the job posting and a list of required skills and experience. Here's the job posting:

<job_posting>
{job_content}
</job_posting>

First, clean and format the job posting:
1. Remove any HTML clutter or unnecessary formatting.
2. Organize the content into clear sections (e.g., Job Title, Company, Job Description, Requirements, etc.).
3. Format the cleaned job posting in Markdown (.md) format.

Next, analyze the job posting to extract the following information:
1. Required skills (both technical and soft skills)
2. Required experience (years of experience, specific industry experience, etc.)
3. Educational requirements
4. Any other notable qualifications or preferences mentioned
5. Required technologies and tools

Format this information as a list in Markdown (.md) format, organizing it into clear categories.

Your final output should consist of two parts, each wrapped in specific XML tags:

<cleaned_job_posting>
[Insert the cleaned and formatted job posting in Markdown here]
</cleaned_job_posting>

<skills_and_experience>
[Insert the list of skills, experience, and other requirements in Markdown here]
</skills_and_experience>

Ensure that your final output contains only these two sections with their respective content. Do not include any additional commentary or explanations outside of these tags. Use British English.
"""


def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Load configuration from file or environment.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Configuration dictionary
    """
    config = {
        "api_key": os.environ.get("ANTHROPIC_API_KEY"),
        "output_dir": os.environ.get("JOB_ANALYSIS_OUTPUT_DIR", "./applications"),
        "model": os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    }
    
    # Load from config file if provided
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    return config


def validate_config(config: dict) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not config.get("api_key"):
        raise ValueError(
            "No API key found. Please set ANTHROPIC_API_KEY environment variable "
            "or provide it in a config file."
        )
    
    if not config["api_key"].startswith("sk-ant-"):
        raise ValueError("Invalid API key format. Should start with 'sk-ant-'")


def read_job_posting(file_path: Path) -> str:
    """
    Read job posting from file.
    
    Args:
        file_path: Path to the job posting file
        
    Returns:
        Job posting content
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Job posting file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if not content:
            raise ValueError("Job posting file is empty")
            
        return content
    except UnicodeDecodeError:
        # Try with different encodings
        for encoding in ['latin-1', 'cp1252']:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read().strip()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Unable to read file with any supported encoding")


def save_analysis(content: str, output_dir: Path, job_title: Optional[str] = None) -> Path:
    """
    Save analysis results to file.
    
    Args:
        content: Analysis content to save
        output_dir: Directory to save output
        job_title: Optional job title for filename
        
    Returns:
        Path to saved file
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if job_title:
        # Clean job title for filename
        clean_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_')[:50]  # Limit length
        filename = f"job_analysis_{clean_title}_{timestamp}.md"
    else:
        filename = f"job_analysis_{timestamp}.md"
    
    output_path = output_dir / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def extract_job_title(content: str) -> Optional[str]:
    """Try to extract job title from the job posting."""
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line) < 100:  # Likely a title
            return line
    return None


def main():
    """Main function to run the job analysis."""
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze job postings using Claude AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s job_posting.txt
  %(prog)s job_posting.txt -o ./output
  %(prog)s job_posting.txt --config config.json
  %(prog)s job_posting.txt --verbose
        """
    )
    parser.add_argument("job_file", help="Path to job posting file")
    parser.add_argument("-o", "--output", help="Output directory (default: ./applications)")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-k", "--api-key", help="Anthropic API key (overrides environment)")
    parser.add_argument("-m", "--model", help="Claude model to use")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    try:
        # Load configuration
        config_path = Path(args.config) if args.config else None
        config = load_config(config_path)
        
        # Override with command line arguments
        if args.api_key:
            config["api_key"] = args.api_key
        if args.output:
            config["output_dir"] = args.output
        if args.model:
            config["model"] = args.model
        
        # Validate configuration
        validate_config(config)
        
        # Read job posting
        job_file = Path(args.job_file)
        logger.info(f"Reading job posting from: {job_file}")
        job_content = read_job_posting(job_file)
        logger.debug(f"Read {len(job_content)} characters")
        
        # Extract job title if possible
        job_title = extract_job_title(job_content)
        if job_title:
            logger.info(f"Detected job title: {job_title}")
        
        # Initialize analyzer
        analyzer = JobAnalyzer(config["api_key"], config["model"])
        
        # Analyze job posting
        print("\n🚀 Analyzing job posting...")
        analysis = analyzer.analyze_job_posting(job_content)
        
        # Save results
        output_dir = Path(config["output_dir"])
        print("\n💾 Saving analysis results...")
        output_path = save_analysis(analysis, output_dir, job_title)
        
        # Print success message
        print("\n" + "✓" * 70)
        print(f"✅ ANALYSIS COMPLETE!")
        print(f"📄 Results saved to: {output_path.absolute()}")
        print(f"📊 Response length: {len(analysis):,} characters")
        print("✓" * 70)
        
        # Print preview
        print("\n📋 PREVIEW OF SAVED CONTENT:")
        print("=" * 70)
        preview = analysis[:500] + ('...' if len(analysis) > 500 else '')
        print(preview)
        print("=" * 70)
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)
    except anthropic.APIError as e:
        logger.error(f"❌ API error: {e}")
        print("\nPlease check your API key and internet connection.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 
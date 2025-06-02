#!/usr/bin/env python3
"""
Configuration Script for Resume Generation (Step 3)
This script handles AI model selection, template choices, language preferences,
and content emphasis settings for resume generation.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import database utilities
try:
    from database_utils import DatabaseManager
except ImportError:
    print("Error: database_utils.py not found. Please ensure it's in the same directory.")
    sys.exit(1)

# Import environment variable support
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")


class ConfigurationManager:
    """Manages configuration settings for resume generation."""
    
    # Model definitions with enhanced Claude support
    AI_MODELS = {
        'gpt-4': {
            'name': 'GPT-4',
            'provider': 'openai',
            'supports_sync': True,
            'description': 'Best quality, slower generation (Recommended)',
            'env_key': 'OPENAI_API_KEY'
        },
        'gpt-3.5-turbo': {
            'name': 'GPT-3.5 Turbo',
            'provider': 'openai',
            'supports_sync': True,
            'description': 'Good quality, faster generation',
            'env_key': 'OPENAI_API_KEY'
        },
        'claude-3.5-sonnet': {
            'name': 'Claude 3.5 Sonnet',
            'provider': 'anthropic',
            'supports_sync': True,
            'description': 'Latest Anthropic model, excellent for professional writing',
            'env_key': 'ANTHROPIC_API_KEY'
        },
        'claude-3-opus': {
            'name': 'Claude 3 Opus',
            'provider': 'anthropic',
            'supports_sync': True,
            'description': 'Most capable Anthropic model, best for complex resumes',
            'env_key': 'ANTHROPIC_API_KEY'
        },
        'claude-3-haiku': {
            'name': 'Claude 3 Haiku',
            'provider': 'anthropic',
            'supports_sync': True,
            'description': 'Fast Anthropic model, good for quick iterations',
            'env_key': 'ANTHROPIC_API_KEY'
        },
        'gemini-pro': {
            'name': 'Gemini Pro',
            'provider': 'google',
            'supports_sync': False,
            'description': 'Great for technical roles',
            'env_key': 'GOOGLE_API_KEY'
        },
        'open-source': {
            'name': 'Open Source Model',
            'provider': 'local',
            'supports_sync': True,
            'description': 'Local LLM (requires separate setup)',
            'note': 'Placeholder for future implementation',
            'env_key': None
        }
    }
    
    # Template options
    TEMPLATES = {
        'modern-professional': 'Modern Professional - Clean, contemporary design',
        'classic-traditional': 'Classic Traditional - Conservative, formal layout',
        'creative-design': 'Creative Design - Visually appealing, creative fields',
        'minimal-clean': 'Minimal Clean - Simple, distraction-free format',
        'executive-level': 'Executive Level - Senior position focused',
        'tech-focused': 'Tech Focused - Technical role optimized'
    }
    
    # Template file mapping - currently all templates use the same file
    # This will be updated when more templates are available
    TEMPLATE_FILES = {
        'modern-professional': 'templates/base_template.html',
        'classic-traditional': 'templates/base_template.html',
        'creative-design': 'templates/base_template.html',
        'minimal-clean': 'templates/base_template.html',
        'executive-level': 'templates/base_template.html',
        'tech-focused': 'templates/base_template.html'
    }
    
    # Language styles
    LANGUAGE_STYLES = {
        'professional': 'Professional - Formal business language',
        'conversational': 'Conversational - Friendly and approachable',
        'technical': 'Technical - Industry-specific terminology',
        'creative': 'Creative - Expressive and unique'
    }
    
    # Focus areas
    FOCUS_AREAS = [
        'achievements_results',
        'work_experience',
        'leadership_management',
        'technical_skills',
        'education_certifications',
        'projects_portfolio'
    ]
    
    FOCUS_AREA_NAMES = {
        'achievements_results': 'Achievements & Results',
        'work_experience': 'Work Experience',
        'leadership_management': 'Leadership & Management',
        'technical_skills': 'Technical Skills',
        'education_certifications': 'Education & Certifications',
        'projects_portfolio': 'Projects & Portfolio'
    }
    
    def __init__(self, db_path: str = "data/resume_app.db"):
        """Initialize the configuration manager."""
        self.db = DatabaseManager(db_path)
        
    def check_api_key_availability(self, model_key: str) -> bool:
        """Check if API key is available for the selected model."""
        model_info = self.AI_MODELS.get(model_key)
        if not model_info:
            return False
            
        env_key = model_info.get('env_key')
        if not env_key:
            # Local models don't need API keys
            return model_key == 'open-source'
            
        # Check environment variable
        api_key = os.getenv(env_key)
        return bool(api_key and api_key.strip())
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get models that have available API keys."""
        available = {}
        for key, model in self.AI_MODELS.items():
            if self.check_api_key_availability(key):
                available[key] = model
        return available
    
    def validate_session(self, session_id: str) -> bool:
        """Validate that the session exists and is at the correct step."""
        try:
            session_data = self.db.get_session_data(session_id)
            if not session_data or not session_data.get('session'):
                return False
                
            session = session_data['session']
            # Check if session is active and at step 2 or higher
            return session.get('status') == 'active' and session.get('current_step', 0) >= 2
        except Exception:
            return False
    
    def save_configuration(self, session_id: str, config: Dict[str, Any]) -> int:
        """Save configuration to database."""
        # Get the template file path
        template_file = self.TEMPLATE_FILES.get(config.get('template', 'modern-professional'))
        
        # Prepare custom instructions with sync mode and template file
        custom_instructions = {
            'sync_mode': config.get('sync_mode', True),
            'template_file': template_file,
            'additional_instructions': config.get('custom_instructions')
        }
        
        # Save to database
        config_id = self.db.save_generation_config(
            session_id=session_id,
            ai_model=config.get('ai_model', 'gpt-4'),
            template_name=config.get('template', 'modern-professional'),
            language_style=config.get('language_style', 'professional'),
            focus_areas=config.get('focus_areas', []),
            custom_instructions=json.dumps(custom_instructions)
        )
        
        # Update session step to 3
        self.db.update_session_step(session_id, 3)
        
        return config_id
    
    def interactive_configuration(self, session_id: str) -> Dict[str, Any]:
        """Run interactive configuration mode."""
        print("\n🔧 Resume Generation Configuration")
        print("=" * 50)
        
        config = {}
        
        # Model selection
        print("\n📊 AI Model Selection")
        available_models = self.get_available_models()
        
        if not available_models:
            print("\n⚠️  No AI models available. Please set API keys in your environment.")
            print("Required environment variables:")
            for key, model in self.AI_MODELS.items():
                if model.get('env_key'):
                    print(f"  - {model['env_key']} for {model['name']}")
            return None
        
        print("\nAvailable models:")
        model_keys = list(available_models.keys())
        for i, key in enumerate(model_keys, 1):
            model = available_models[key]
            print(f"{i}. {model['name']} - {model['description']}")
        
        while True:
            try:
                choice = input(f"\nSelect model (1-{len(model_keys)}) [1]: ").strip() or "1"
                idx = int(choice) - 1
                if 0 <= idx < len(model_keys):
                    config['ai_model'] = model_keys[idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Sync mode selection
        selected_model = self.AI_MODELS[config['ai_model']]
        if selected_model['supports_sync']:
            print(f"\n🔄 Sync Mode (supported by {selected_model['name']})")
            sync_choice = input("Enable sync mode? (Y/n) [Y]: ").strip().lower()
            config['sync_mode'] = sync_choice != 'n'
        else:
            config['sync_mode'] = False
            print(f"\n📝 Note: {selected_model['name']} doesn't support sync mode.")
        
        # Template selection
        print("\n🎨 Resume Template Selection")
        print("📝 Note: Currently all templates use the same base design. More templates coming soon!")
        template_keys = list(self.TEMPLATES.keys())
        for i, key in enumerate(template_keys, 1):
            print(f"{i}. {self.TEMPLATES[key]}")
        
        while True:
            try:
                choice = input(f"\nSelect template (1-{len(template_keys)}) [1]: ").strip() or "1"
                idx = int(choice) - 1
                if 0 <= idx < len(template_keys):
                    config['template'] = template_keys[idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Language style
        print("\n✍️  Language Style")
        style_keys = list(self.LANGUAGE_STYLES.keys())
        for i, key in enumerate(style_keys, 1):
            print(f"{i}. {self.LANGUAGE_STYLES[key]}")
        
        while True:
            try:
                choice = input(f"\nSelect style (1-{len(style_keys)}) [1]: ").strip() or "1"
                idx = int(choice) - 1
                if 0 <= idx < len(style_keys):
                    config['language_style'] = style_keys[idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Word limit
        print("\n📏 Word Count Limit")
        word_limit = input("Enter word limit (press Enter for no limit): ").strip()
        if word_limit:
            try:
                config['word_limit'] = int(word_limit)
            except ValueError:
                print("Invalid number. No word limit will be set.")
                config['word_limit'] = None
        else:
            config['word_limit'] = None
        
        # Focus areas
        print("\n🎯 Content Emphasis Areas")
        print("Select areas to emphasize (comma-separated numbers):")
        for i, area in enumerate(self.FOCUS_AREAS, 1):
            print(f"{i}. {self.FOCUS_AREA_NAMES[area]}")
        
        focus_input = input("\nSelect focus areas (e.g., 1,2,4) [1,2]: ").strip() or "1,2"
        try:
            indices = [int(x.strip()) - 1 for x in focus_input.split(',')]
            config['focus_areas'] = [self.FOCUS_AREAS[i] for i in indices if 0 <= i < len(self.FOCUS_AREAS)]
        except (ValueError, IndexError):
            print("Invalid selection. Using default focus areas.")
            config['focus_areas'] = ['achievements_results', 'work_experience']
        
        # Custom instructions
        print("\n💡 Additional Instructions (optional)")
        config['custom_instructions'] = input("Enter any custom instructions: ").strip() or None
        
        # Confirmation
        print("\n📋 Configuration Summary:")
        print(f"  Model: {self.AI_MODELS[config['ai_model']]['name']}")
        print(f"  Sync Mode: {'Enabled' if config.get('sync_mode') else 'Disabled'}")
        print(f"  Template: {config['template']}")
        print(f"  Language: {config['language_style']}")
        print(f"  Word Limit: {config.get('word_limit', 'None')}")
        print(f"  Focus Areas: {', '.join([self.FOCUS_AREA_NAMES[a] for a in config['focus_areas']])}")
        
        confirm = input("\nSave this configuration? (Y/n) [Y]: ").strip().lower()
        if confirm == 'n':
            print("Configuration cancelled.")
            return None
        
        return config


def main():
    """Main function to handle configuration."""
    parser = argparse.ArgumentParser(
        description="Configure resume generation settings (Step 3)"
    )
    
    # Positional argument
    parser.add_argument('session_id', nargs='?', help='Session ID from previous steps')
    
    # Optional arguments
    parser.add_argument('--ai-model', choices=list(ConfigurationManager.AI_MODELS.keys()),
                       help='AI model for generation')
    parser.add_argument('--sync-mode', action='store_true', default=True,
                       help='Enable sync mode for applicable models')
    parser.add_argument('--template', choices=list(ConfigurationManager.TEMPLATES.keys()),
                       help='Resume template')
    parser.add_argument('--language-style', choices=list(ConfigurationManager.LANGUAGE_STYLES.keys()),
                       help='Language style')
    parser.add_argument('--word-limit', type=int, help='Word count limit')
    parser.add_argument('--focus-areas', help='Comma-separated focus areas')
    parser.add_argument('--custom-instructions', help='Additional custom instructions')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--test', action='store_true', help='Run with test data')
    
    args = parser.parse_args()
    
    # Initialize configuration manager
    config_mgr = ConfigurationManager()
    
    # Handle test mode
    if args.test:
        print("🧪 Running in test mode")
        # Create a test session
        test_session_id = config_mgr.db.create_session({'source': 'test_config'})
        # Update to step 2 to simulate previous step completion
        config_mgr.db.update_session_step(test_session_id, 2)
        
        # Use test configuration
        test_config = {
            'ai_model': 'gpt-4' if config_mgr.check_api_key_availability('gpt-4') else 'open-source',
            'sync_mode': True,
            'template': 'modern-professional',
            'language_style': 'professional',
            'word_limit': None,
            'focus_areas': ['achievements_results', 'work_experience'],
            'custom_instructions': 'Test configuration'
        }
        
        session_id = test_session_id
        config = test_config
        print(f"Created test session: {session_id}")
        
    else:
        # Validate session ID
        if not args.session_id:
            print("Error: session_id is required (or use --test for test mode)")
            parser.print_help()
            sys.exit(1)
        
        session_id = args.session_id
        
        # Validate session
        if not config_mgr.validate_session(session_id):
            print(f"Error: Invalid session ID or session not ready for configuration.")
            print("Please ensure you've completed step 2 (document upload) first.")
            sys.exit(1)
        
        # Determine configuration mode
        if args.interactive or not any([args.ai_model, args.template, args.language_style]):
            # Interactive mode
            config = config_mgr.interactive_configuration(session_id)
            if not config:
                sys.exit(1)
        else:
            # Command-line mode
            config = {
                'ai_model': args.ai_model or 'gpt-4',
                'sync_mode': args.sync_mode,
                'template': args.template or 'modern-professional',
                'language_style': args.language_style or 'professional',
                'word_limit': args.word_limit,
                'focus_areas': args.focus_areas.split(',') if args.focus_areas else ['achievements_results', 'work_experience'],
                'custom_instructions': args.custom_instructions
            }
            
            # Validate API key for selected model
            if not config_mgr.check_api_key_availability(config['ai_model']):
                model_info = ConfigurationManager.AI_MODELS[config['ai_model']]
                print(f"Error: API key not found for {model_info['name']}")
                if model_info.get('env_key'):
                    print(f"Please set {model_info['env_key']} in your environment.")
                sys.exit(1)
    
    try:
        # Save configuration
        config_id = config_mgr.save_configuration(session_id, config)
        
        # Prepare output
        output = {
            'status': 'success',
            'message': 'Configuration saved successfully',
            'configuration': {
                'session_id': session_id,
                'ai_model': config['ai_model'],
                'sync_mode': config.get('sync_mode', True),
                'template_name': config['template'],
                'language_style': config['language_style'],
                'word_limit': config.get('word_limit'),
                'focus_areas': config['focus_areas'],
                'custom_instructions': {
                    'sync_mode': config.get('sync_mode', True),
                    'template_file': config_mgr.TEMPLATE_FILES.get(config['template']),
                    'additional_instructions': config.get('custom_instructions')
                },
                'config_id': config_id
            }
        }
        
        print("\n✅ Configuration saved successfully!")
        print(f"\n📊 Results:")
        print(json.dumps(output, indent=2))
        
        print(f"\n📌 Session ID: {session_id}")
        print(f"📌 Configuration ID: {config_id}")
        print("\n💡 Next step: Run the resume generation script with this session ID")
        
    except Exception as e:
        output = {
            'status': 'error',
            'message': f'Error saving configuration: {str(e)}',
            'configuration': None
        }
        print(f"\n❌ Error: {str(e)}")
        print(json.dumps(output, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main() 
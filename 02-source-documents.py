#!/usr/bin/env python3
"""
Source Documents Handler - Backend Script
This script handles document collection and loading for the resume creation process.
It focuses solely on collecting and preparing documents for future analysis.
Now integrated with SQLite database for persistence.
"""

import os
import sys
import json
from pathlib import Path
import PyPDF2
from docx import Document

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database utilities
from database_utils import DatabaseManager

class SourceDocumentHandler:
    """Handles collection and loading of source documents for resume generation."""
    
    def __init__(self, session_id=None):
        # Define supported file formats
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt', '.json', '.md']
        self.max_file_size = 10 * 1024 * 1024  # 10MB in bytes
        
        # Initialize database manager
        self.db = DatabaseManager()
        
        # Session management
        self.session_id = session_id
        
    def collect_documents(self, directory_path):
        """
        Collect documents from a specified directory.
        
        Args:
            directory_path (str): Path to the directory containing documents
            
        Returns:
            list: List of valid file paths
        """
        collected_files = []
        
        try:
            # Convert to Path object for easier handling
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Invalid directory path: {directory_path}")
            
            # Iterate through files in directory
            for file_path in path.iterdir():
                if file_path.is_file():
                    # Check if file format is supported
                    if file_path.suffix.lower() in self.supported_formats:
                        # Validate the file
                        if self.validate_file(file_path):
                            collected_files.append(str(file_path))
                            
        except Exception as e:
            print(f"Error collecting documents: {str(e)}")
            
        return collected_files
    
    def validate_file(self, file_path):
        """
        Validate that a file is not empty and is readable.
        
        Args:
            file_path (Path): Path object of the file to validate
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            # Check if file exists
            if not file_path.exists():
                return False
                
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                print(f"File is empty: {file_path.name}")
                return False
                
            if file_size > self.max_file_size:
                print(f"File exceeds maximum size (10MB): {file_path.name}")
                return False
                
            # Try to open the file to ensure it's readable
            with open(file_path, 'rb') as f:
                # Read first few bytes to ensure file is accessible
                f.read(1)
                
            return True
            
        except Exception as e:
            print(f"File validation error for {file_path.name}: {str(e)}")
            return False
    
    def load_document(self, file_path):
        """
        Load the contents of a document based on its format.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            dict: Document information including filename, content, and type
        """
        path = Path(file_path)
        file_extension = path.suffix.lower()
        content = ""
        
        try:
            if file_extension == '.pdf':
                content = self._load_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                content = self._load_word(file_path)
            elif file_extension == '.txt':
                content = self._load_text(file_path)
            elif file_extension == '.json':
                content = self._load_json(file_path)
            elif file_extension == '.md':
                content = self._load_markdown(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            return {
                "filename": path.name,
                "content": content,
                "type": file_extension[1:],  # Remove the dot
                "file_size": path.stat().st_size
            }
            
        except Exception as e:
            print(f"Error loading document {path.name}: {str(e)}")
            return None
    
    def _load_pdf(self, file_path):
        """Load content from a PDF file."""
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text() + "\n"
        return content.strip()
    
    def _load_word(self, file_path):
        """Load content from a Word document."""
        doc = Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text)
        return "\n".join(content)
    
    def _load_text(self, file_path):
        """Load content from a text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _load_json(self, file_path):
        """Load content from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert JSON to string representation
            return json.dumps(data, indent=2)
    
    def _load_markdown(self, file_path):
        """Load content from a Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def determine_document_type(self, filename, content):
        """
        Determine the type of document based on filename and content.
        
        Args:
            filename (str): Name of the file
            content (str): Content of the file
            
        Returns:
            str: Document type (resume, cover_letter, portfolio, etc.)
        """
        filename_lower = filename.lower()
        content_lower = content.lower()[:1000]  # Check first 1000 chars
        
        # Check filename patterns
        if any(word in filename_lower for word in ['resume', 'cv', 'curriculum']):
            return 'resume'
        elif any(word in filename_lower for word in ['cover', 'letter']):
            return 'cover_letter'
        elif 'portfolio' in filename_lower:
            return 'portfolio'
        elif 'linkedin' in filename_lower:
            return 'linkedin_profile'
        
        # Check content patterns
        if any(phrase in content_lower for phrase in ['work experience', 'education', 'skills', 'professional experience']):
            return 'resume'
        elif any(phrase in content_lower for phrase in ['dear hiring', 'dear recruiter', 'i am writing']):
            return 'cover_letter'
        
        return 'other'
    
    def process_documents(self, directory_path, session_id=None):
        """
        Main function to collect and load all documents from a directory.
        
        Args:
            directory_path (str): Path to the directory containing documents
            session_id (str): Optional session ID. If not provided, creates new session
            
        Returns:
            dict: JSON object with status, message, documents, and session_id
        """
        result = {
            "status": "error",
            "message": "",
            "documents": [],
            "session_id": None
        }
        
        try:
            # Create or use existing session
            if session_id:
                self.session_id = session_id
            else:
                self.session_id = self.db.create_session({
                    "source": "standalone_script",
                    "directory": str(directory_path)
                })
            
            result["session_id"] = self.session_id
            
            # Update session to step 2
            self.db.update_session_step(self.session_id, 2)
            
            # Collect valid documents
            file_paths = self.collect_documents(directory_path)
            
            if not file_paths:
                result["message"] = "No valid documents found in the specified directory"
                return result
            
            # Load each document
            for file_path in file_paths:
                doc_data = self.load_document(file_path)
                if doc_data:
                    # Determine document type
                    doc_type = self.determine_document_type(
                        doc_data['filename'], 
                        doc_data['content']
                    )
                    
                    # Save to database
                    doc_id = self.db.save_uploaded_document(
                        session_id=self.session_id,
                        filename=doc_data['filename'],
                        content=doc_data['content'],
                        file_type=doc_data['type'],
                        file_size=doc_data['file_size'],
                        document_type=doc_type
                    )
                    
                    # Add to result
                    doc_data['id'] = doc_id
                    doc_data['document_type'] = doc_type
                    result["documents"].append(doc_data)
            
            if result["documents"]:
                result["status"] = "success"
                result["message"] = f"Successfully loaded {len(result['documents'])} document(s)"
            else:
                result["message"] = "No documents could be loaded successfully"
                
        except Exception as e:
            result["message"] = f"Error processing documents: {str(e)}"
            
        return result


def main():
    """Main function to demonstrate usage."""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Process source documents for resume generation'
    )
    parser.add_argument(
        'directory',
        nargs='?',  # Make directory optional
        help='Path to directory containing documents'
    )
    parser.add_argument(
        '--session-id',
        help='Existing session ID to use (optional)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run with test data directory'
    )
    
    args = parser.parse_args()
    
    # Use test directory if specified
    if args.test:
        # Create test directory with sample files
        test_dir = Path("data/test_documents")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a sample text file
        sample_resume = test_dir / "sample_resume.txt"
        sample_resume.write_text("""
John Doe
Software Engineer

WORK EXPERIENCE
Senior Software Engineer at Tech Corp (2020-Present)
- Developed scalable web applications
- Led team of 5 developers

EDUCATION
BS Computer Science, University XYZ (2016)

SKILLS
Python, JavaScript, SQL, Docker
        """)
        
        # Create a sample cover letter
        sample_cover = test_dir / "cover_letter.txt"
        sample_cover.write_text("""
Dear Hiring Manager,

I am writing to express my interest in the Software Engineer position at your company.
With 5 years of experience in web development, I believe I would be a great fit.

Best regards,
John Doe
        """)
        
        directory_path = str(test_dir)
        print(f"📁 Using test directory: {directory_path}")
    else:
        if not args.directory:
            parser.error("directory is required unless --test is specified")
        directory_path = args.directory
    
    # Create handler instance
    handler = SourceDocumentHandler()
    
    # Process documents
    print(f"\n🔍 Processing documents from: {directory_path}")
    result = handler.process_documents(directory_path, args.session_id)
    
    # Output result as JSON
    print("\n📊 Results:")
    print(json.dumps(result, indent=2))
    
    # If successful, show database summary
    if result["status"] == "success" and result["session_id"]:
        print(f"\n✅ Documents saved to database")
        print(f"📌 Session ID: {result['session_id']}")
        print(f"\n💡 To view session data, run:")
        print(f"   python -c \"from database_utils import get_session_data; import json; print(json.dumps(get_session_data('{result['session_id']}'), indent=2))\"")


if __name__ == "__main__":
    main() 
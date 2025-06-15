import os
import re
import csv
from typing import Dict, Any
import PyPDF2

class ContentProcessor:
    def __init__(self):
        self.supported_formats = ['.txt', '.pdf', '.csv']
    
    def process_content(self, content_source: str, source_type: str = 'text') -> Dict[str, Any]:
        try:
            if source_type == 'file':
                return self._process_file(content_source)
            elif source_type == 'text':
                return self._process_text(content_source)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'metadata': {}
            }
    
    def _process_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        if file_extension == '.txt':
            content = self._read_text_file(file_path)
        elif file_extension == '.pdf':
            content = self._read_pdf_file(file_path)
        elif file_extension == '.csv':
            content = self._read_csv_file(file_path)
        
        cleaned_content = self._clean_content(content)
        
        return {
            'success': True,
            'content': cleaned_content,
            'metadata': {
                'source_type': 'file',
                'file_path': file_path,
                'file_format': file_extension,
                'word_count': len(cleaned_content.split()),
                'char_count': len(cleaned_content)
            }
        }
    
    def _process_text(self, raw_text: str) -> Dict[str, Any]:
        cleaned_content = self._clean_content(raw_text)
        
        return {
            'success': True,
            'content': cleaned_content,
            'metadata': {
                'source_type': 'text',
                'word_count': len(cleaned_content.split()),
                'char_count': len(cleaned_content)
            }
        }
    
    def _read_text_file(self, file_path: str) -> str:
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        
        raise UnicodeDecodeError("Could not decode file with any supported encoding")
    
    def _read_pdf_file(self, file_path: str) -> str:
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text() + "\n"
        return content
    
    def _read_csv_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if not rows:
                return ""
            content = "\n".join([" ".join(row) for row in rows])
            return content
    
    def _clean_content(self, content: str) -> str:
        if not content:
            return ""
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', ' ', content)
        content = re.sub(r' +', ' ', content)
        return content.strip()
    
    def get_content_sections(self, content: str, max_section_length: int = 2000) -> list:
        if len(content) <= max_section_length:
            return [content]
        
        sections = []
        words = content.split()
        current_section = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1
            if current_length + word_length > max_section_length and current_section:
                sections.append(' '.join(current_section))
                current_section = [word]
                current_length = word_length
            else:
                current_section.append(word)
                current_length += word_length
        
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections
    
    def validate_content(self, content: str, min_words: int = 50) -> Dict[str, Any]:
        word_count = len(content.split())
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'suggestions': []
        }
        
        if word_count < min_words:
            validation_result['is_valid'] = False
            validation_result['warnings'].append(f"Content too short ({word_count} words). Minimum {min_words} words required.")
            validation_result['suggestions'].append("Add more detailed content for better flashcard generation.")
        
        if len(content.strip()) == 0:
            validation_result['is_valid'] = False
            validation_result['warnings'].append("Content is empty.")
        
        educational_keywords = ['define', 'explain', 'concept', 'theory', 'principle', 'method', 'process', 'example']
        has_educational_content = any(keyword in content.lower() for keyword in educational_keywords)
        
        if not has_educational_content:
            validation_result['suggestions'].append("Content might benefit from more educational structure (definitions, explanations, examples).")
        
        return validation_result
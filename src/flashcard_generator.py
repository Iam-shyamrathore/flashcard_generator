import os
import json
import csv
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.content_processor import ContentProcessor
from src.llm_integration import GeminiFlashcardGenerator

class Flashcard:
    def __init__(self, id: str, question: str, answer: str, difficulty: str, topic: str, subject: str):
        self.id = id
        self.question = question
        self.answer = answer
        self.difficulty = difficulty
        self.topic = topic
        self.subject = subject
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'difficulty': self.difficulty,
            'topic': self.topic,
            'subject': self.subject
        }

class FlashcardSet:
    def __init__(self, name: str, subject: str, description: str):
        self.name = name
        self.subject = subject
        self.description = description
        self.flashcards: List[Flashcard] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_flashcard(self, flashcard: Dict[str, str]) -> None:
        card = Flashcard(
            id=flashcard.get('id', str(uuid.uuid4())[:8]),
            question=flashcard['question'],
            answer=flashcard['answer'],
            difficulty=flashcard.get('difficulty', 'Medium'),
            topic=flashcard.get('topic', ''),
            subject=flashcard.get('subject', self.subject)
        )
        self.flashcards.append(card)
    
    def add_flashcards(self, flashcards: List[Dict[str, str]]) -> None:
        for flashcard in flashcards:
            self.add_flashcard(flashcard)
    
    def get_flashcards_by_difficulty(self, difficulty: str) -> List[Flashcard]:
        return [card for card in self.flashcards if card.difficulty.lower() == difficulty.lower()]
    
    def get_flashcards_by_topic(self, topic: str) -> List[Flashcard]:
        return [card for card in self.flashcards if topic.lower() in card.topic.lower()]
    
    def get_statistics(self) -> Dict[str, Any]:
        difficulty_counts = {}
        topics = set()
        
        for card in self.flashcards:
            difficulty_counts[card.difficulty] = difficulty_counts.get(card.difficulty, 0) + 1
            if card.topic:
                topics.add(card.topic)
        
        return {
            'total_cards': len(self.flashcards),
            'difficulties': difficulty_counts,
            'topics': list(topics),
            'subjects': list(set(card.subject for card in self.flashcards))
        }

class FlashcardGenerator:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.content_processor = ContentProcessor()
        self.llm_generator = GeminiFlashcardGenerator(api_key=gemini_api_key)
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def generate_from_file(self, file_path: str, subject: str = "General",
                          min_cards: int = 10, max_cards: int = 15,
                          set_name: str = "Flashcard Set",
                          description: str = "Generated flashcard set") -> Dict[str, Any]:
        content_result = self.content_processor.process_content(file_path, source_type='file')
        if not content_result['success']:
            return {
                'success': False,
                'error': f"Content processing failed: {content_result['error']}",
                'flashcard_set': None
            }
        return self._generate_flashcards_from_content(
            content=content_result['content'],
            subject=subject,
            min_cards=min_cards,
            max_cards=max_cards,
            set_name=set_name,
            description=description,
            source=file_path
        )
    
    def generate_from_text(self, text_content: str, subject: str = "General",
                          min_cards: int = 10, max_cards: int = 15,
                          set_name: str = "Flashcard Set",
                          description: str = "Generated flashcard set") -> Dict[str, Any]:
        content_result = self.content_processor.process_content(text_content, source_type='text')
        if not content_result['success']:
            return {
                'success': False,
                'error': f"Content processing failed: {content_result['error']}",
                'flashcard_set': None
            }
        return self._generate_flashcards_from_content(
            content=content_result['content'],
            subject=subject,
            min_cards=min_cards,
            max_cards=max_cards,
            set_name=set_name,
            description=description,
            source="Text Input"
        )
    
    def _generate_flashcards_from_content(self, content: str, subject: str,
                                        min_cards: int, max_cards: int,
                                        set_name: str, description: str,
                                        source: str) -> Dict[str, Any]:
        validation = self.content_processor.validate_content(content)
        if not validation['is_valid']:
            return {
                'success': False,
                'error': f"Content validation failed: {validation['warnings']}",
                'flashcard_set': None
            }
        
        sections = self.content_processor.get_content_sections(content, max_section_length=2000)
        llm_result = self.llm_generator.generate_flashcards(
            content=content,
            subject=subject,
            min_cards=min_cards,
            max_cards=max_cards
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': f"LLM generation failed: {llm_result['error']}",
                'flashcard_set': None
            }
        
        flashcards = llm_result['flashcards']
        for card in flashcards:
            card['subject'] = subject
        
        flashcard_set = FlashcardSet(
            name=set_name,
            subject=subject,
            description=description
        )
        flashcard_set.add_flashcards(flashcards)
        flashcard_set.metadata = {
            'source': source,
            'generation_method': 'llm',
            'content_sections': len(sections),
            'original_content_length': len(content)
        }
        
        return {
            'success': True,
            'flashcard_set': flashcard_set,
            'statistics': flashcard_set.get_statistics()
        }
    
    def export_flashcards(self, flashcard_set: FlashcardSet, export_format: str = 'csv') -> Dict[str, Any]:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{flashcard_set.subject.replace(' ', '_')}_{timestamp}.{export_format}"
        filepath = os.path.join(self.export_dir, filename)
        
        if export_format == 'csv':
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Question', 'Answer', 'Difficulty', 'Topic', 'Subject'])
                for card in flashcard_set.flashcards:
                    writer.writerow([
                        card.id,
                        card.question,
                        card.answer,
                        card.difficulty,
                        card.topic,
                        card.subject
                    ])
        elif export_format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'name': flashcard_set.name,
                    'subject': flashcard_set.subject,
                    'description': flashcard_set.description,
                    'metadata': flashcard_set.metadata,
                    'flashcards': [card.to_dict() for card in flashcard_set.flashcards]
                }, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        return {
            'success': True,
            'filepath': filepath,
            'format': export_format,
            'total_exported': len(flashcard_set.flashcards)
        }
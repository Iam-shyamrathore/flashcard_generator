import os
import json
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiFlashcardGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        )
    
    def generate_flashcards(self, content: str, subject: str = "General", 
                          min_cards: int = 10, max_cards: int = 15) -> Dict[str, Any]:
        prompt = self._create_flashcard_prompt(content, subject, min_cards, max_cards)
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        flashcards = self._parse_flashcard_response(response.text)
        return {
            'success': True,
            'flashcards': flashcards,
            'metadata': {
                'subject': subject,
                'total_cards': len(flashcards),
                'source_content_length': len(content),
                'model_used': 'gemini-2.0-flash-lite'
            }
        }
    
    def _create_flashcard_prompt(self, content: str, subject: str, 
                               min_cards: int, max_cards: int) -> str:
        return f"""
You are an expert educational content creator specializing in {subject}. Your task is to create high-quality flashcards from the provided educational content.

INSTRUCTIONS:
1. Generate between {min_cards} and {max_cards} flashcards
2. Each flashcard should have a clear, concise question and a complete, accurate answer
3. Focus on key concepts, definitions, processes, and important facts
4. Make questions specific and answers self-contained
5. Vary question types (definitions, explanations, examples, comparisons)
6. Ensure answers are factually correct and educationally valuable

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
```json
{{
  "flashcards": [
    {{
      "id": 1,
      "question": "What is [concept]?",
      "answer": "Complete answer explaining the concept clearly.",
      "difficulty": "Easy|Medium|Hard",
      "topic": "Specific topic area"
    }},
    {{
      "id": 2,
      "question": "How does [process] work?",
      "answer": "Step-by-step explanation of the process.",
      "difficulty": "Easy|Medium|Hard",
      "topic": "Specific topic area"
    }}
  ]
}}
```

EDUCATIONAL CONTENT TO PROCESS:
{content}

Generate the flashcards now in the exact JSON format specified above:
"""
    
    def _parse_flashcard_response(self, response_text: str) -> List[Dict[str, Any]]:
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text
        
        parsed_data = json.loads(json_str)
        if 'flashcards' in parsed_data:
            flashcards = parsed_data['flashcards']
        else:
            flashcards = parsed_data if isinstance(parsed_data, list) else []
        
        validated_flashcards = []
        for i, card in enumerate(flashcards):
            if self._validate_flashcard(card):
                validated_flashcards.append(self._clean_flashcard(card, i + 1))
        
        return validated_flashcards
    
    def _validate_flashcard(self, card: Dict[str, Any]) -> bool:
        required_fields = ['question', 'answer']
        return all(field in card and card[field].strip() for field in required_fields)
    
    def _clean_flashcard(self, card: Dict[str, Any], card_id: int) -> Dict[str, Any]:
        cleaned_card = {
            'id': card_id,
            'question': card['question'].strip(),
            'answer': card['answer'].strip(),
            'difficulty': card.get('difficulty', 'Medium').strip(),
            'topic': card.get('topic', '').strip()
        }
        if not cleaned_card['question'].endswith(('?', ':', '.')):
            cleaned_card['question'] += '?'
        return cleaned_card
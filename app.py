import sys
import os
from flask import Flask, jsonify, send_from_directory, request, send_file
from src.flashcard_generator import FlashcardGenerator, FlashcardSet
from io import StringIO, BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

app = Flask(__name__)
generator = FlashcardGenerator()
current_flashcard_set = None

@app.route('/')
def serve_index():
    index_path = os.path.abspath(os.path.join('.', 'index.html'))
    if not os.path.exists(index_path):
        return jsonify({'error': f'index.html not found at {index_path}'}), 404
    return send_from_directory('.', 'index.html')

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    global current_flashcard_set
    if not current_flashcard_set:
        return jsonify({'error': 'No flashcards generated. Please upload content first.'}), 400

    flashcards = [
        {
            'question': card.question,
            'answer': card.answer,
            'difficulty': card.difficulty,
            'topic': card.topic,
            'subject': card.subject
        }
        for card in current_flashcard_set.flashcards
    ]
    return jsonify(flashcards)  

@app.route('/api/flashcards/filter', methods=['POST'])
def filter_flashcards():
    global current_flashcard_set
    if not current_flashcard_set:
        return jsonify({'error': 'No flashcards available. Generate flashcards first.'}), 400

    data = request.get_json()
    difficulty = data.get('difficulty')
    topic = data.get('topic')

    filtered_flashcards = current_flashcard_set.flashcards
    if difficulty:
        filtered_flashcards = current_flashcard_set.get_flashcards_by_difficulty(difficulty)
    if topic:
        filtered_flashcards = [card for card in filtered_flashcards if topic.lower() in card.topic.lower()]

    flashcards = [
        {
            'question': card.question,
            'answer': card.answer,
            'difficulty': card.difficulty,
            'topic': card.topic,
            'subject': card.subject
        }
        for card in filtered_flashcards
    ]
    return jsonify(flashcards)

@app.route('/api/upload', methods=['POST'])
def upload_content():
    global current_flashcard_set
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        result = generator.generate_from_file(
            file_path=file_path,
            subject=request.form.get('subject', 'General'),
            min_cards=5,
            max_cards=10,
            set_name=f"{request.form.get('subject', 'General')} Flashcards",
            description="Flashcards generated from uploaded file"
        )

        os.remove(file_path)
    else:
        text_content = request.form.get('text_content', '')
        if not text_content:
            return jsonify({'error': 'No text content provided'}), 400

        result = generator.generate_from_text(
            text_content=text_content,
            subject=request.form.get('subject', 'General'),
            min_cards=5,
            max_cards=10,
            set_name=f"{request.form.get('subject', 'General')} Flashcards",
            description="Flashcards generated from text input"
        )

    if result['success']:
        current_flashcard_set = result['flashcard_set']
        flashcards = [
            {
                'question': card.question,
                'answer': card.answer,
                'difficulty': card.difficulty,
                'topic': card.topic,
                'subject': card.subject
            }
            for card in current_flashcard_set.flashcards
        ]
        return jsonify(flashcards)
    return jsonify({'error': result['error']}), 500

@app.route('/api/export/<format>', methods=['GET'])
def export_flashcards(format):
    global current_flashcard_set
    if not current_flashcard_set:
        return jsonify({'error': 'No flashcards available to export'}), 400

    if format not in ['json', 'csv']:
        return jsonify({'error': f'Unsupported export format: {format}'}), 400

    export_result = generator.export_flashcards(current_flashcard_set, export_format=format)
    if export_result['success']:
        return send_file(
            export_result['filepath'],
            as_attachment=True,
            download_name=os.path.basename(export_result['filepath'])
        )
    return jsonify({'error': export_result['error']}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=False, port=5000)
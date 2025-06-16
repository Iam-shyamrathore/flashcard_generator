# Flashcard Generator

A web application that generates flashcards from educational content using the Gemini API. It supports `.txt`, `.pdf`, and `.csv` file formats, allowing users to upload content, filter flashcards, and export them as JSON or CSV.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/flashcard-generator.git
   cd flashcard-generator
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set the Gemini API Key**:
   - Obtain a Gemini API key from Google.
   - Set the `GEMINI_API_KEY` environment variable:
     ```bash
     export GEMINI_API_KEY=your-api-key  # On Windows: set GEMINI_API_KEY=your-api-key
     ```
   - Alternatively, create a `.env` file in the project root with:
     ```
     GEMINI_API_KEY=your-api-key
     ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser to access the app.

## Usage

- **Generate Flashcards**:
  - Use the web interface to upload a `.txt`, `.pdf`, or `.csv` file, or enter text directly.
  - Specify a subject (optional) and click "Generate Flashcards".
- **Filter Flashcards**:
  - Filter by difficulty (Easy, Medium, Hard) or topic using the filter section.
- **Navigate Flashcards**:
  - Flip cards to see answers, and use the Previous/Next buttons to cycle through flashcards.
- **Export Flashcards**:
  - Export flashcards as JSON or CSV using the export buttons.

By default, the app loads flashcards from `data/geography_qa.csv` (Geography flashcards).

## Code Examples

### Example CSV File Structure

The app supports `.csv` files for generating flashcards. Below is the structure of the default `geography_qa.csv` file, which contains question-answer pairs with difficulty and topic metadata:

```csv
Question,Answer,Difficulty,Topic
"What is the capital of France?","The capital of France is Paris.","Easy","European Geography"
"Which river is the longest in the world?","The Nile River is the longest in the world, stretching over 6,650 kilometers.","Medium","Rivers"
"What is the smallest continent by land area?","Australia is the smallest continent by land area.","Easy","Continents"
"Which desert is the largest in the world?","The Sahara Desert is the largest hot desert, covering about 9.2 million square kilometers.","Medium","Deserts"
"What is the highest mountain in the world?","Mount Everest, located in the Himalayas, is the highest mountain at 8,848 meters.","Hard","Mountains"
```

You can create your own CSV files following this structure and place them in the `data` directory.

### Sample API Call

You can fetch flashcards programmatically using the `/api/flashcards` endpoint. Here’s an example using `curl`:

```bash
curl http://localhost:5000/api/flashcards
```

This will return a JSON array of flashcards, such as:

```json
[
    {
        "question": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "difficulty": "Easy",
        "topic": "European Geography",
        "subject": "Geography"
    },
    {
        "question": "Which river is the longest in the world?",
        "answer": "The Nile River is the longest in the world, stretching over 6,650 kilometers.",
        "difficulty": "Medium",
        "topic": "Rivers",
        "subject": "Geography"
    }
]
```

## Features

- Upload text or files (`.txt`, `.pdf`, `.csv`) to generate flashcards.
- Filter flashcards by difficulty and topic.
- Export flashcards as JSON or CSV.
- Interactive UI with flip animation for flashcards.

## Project Structure

```
flashcard_generator/
├── app.py               # Flask backend
├── index.html           # Frontend UI
├── data/                # Default data files (e.g., geography_qa.csv)
├── src/                 # Core logic
│   ├── content_processor.py
│   ├── llm_integration.py
│   └── flashcard_generator.py
├── uploads/             # Temporary directory for uploaded files
├── exports/             # Directory for exported flashcards
└── requirements.txt     # Dependencies
```

## Dependencies

- Flask
- PyPDF2
- google-generativeai
- python-dotenv

See `requirements.txt` for the full list.

## Notes

- The application requires a Gemini API key to generate flashcards. Ensure the `GEMINI_API_KEY` environment variable is set.
- The default dataset (`geography_qa.csv`) contains geography flashcards. You can replace it with your own dataset in the `data` directory and update `app.py` accordingly.

## ScreenShots
![image](https://github.com/user-attachments/assets/f4f05afd-7a83-49d9-b513-7a9fc31cf590)

![image](https://github.com/user-attachments/assets/20244c02-163d-42f4-ba2d-67da20ad097e)

![image](https://github.com/user-attachments/assets/2cfbf5f5-7985-4368-90f8-2ece16ef7925)



## License

This project is licensed under the MIT License. See the LICENSE file for details.

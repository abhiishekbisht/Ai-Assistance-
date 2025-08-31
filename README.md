# AI Assistant Web App

A modern, professional AI assistant web application built with Flask, MySQL, and Gemini API. The app provides four main functions: answering questions, summarizing text, generating creative content, and providing advice. Authentication is removed for simplicity and privacy.

## Features
- **Answer Questions:** Get factual answers to your queries.
- **Summarize Text:** Summarize articles or documents.
- **Generate Creative Content:** Create stories, poems, or essays.
- **Provide Advice:** Get helpful advice and tips.
- Clean, symmetrical, and responsive UI.
- All database configuration via `.env` variables.
- No authentication required.

## Project Structure
```
app.py
requirements.txt
.env.example
scripts/
    database_setup.sql
static/
    style.css
    script.js
templates/
    base.html
    index.html
    chat.html
    history.html
    select_style.html
```

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ai-chatbot
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in your MySQL and Gemini API credentials.
4. **Set up the database:**
   - Run the SQL script in `scripts/database_setup.sql` to create necessary tables.
5. **Run the app:**
   ```bash
   python app.py
   ```
6. **Access the app:**
   - Open your browser and go to `http://localhost:5000`

## Environment Variables
- `DB_HOST`: MySQL host
- `DB_USER`: MySQL username
- `DB_PASS`: MySQL password
- `DB_NAME`: MySQL database name
- `GEMINI_API_KEY`: Gemini API key

## Customization
- Edit `static/style.css` for UI changes.
- Update prompt instructions in `app.py` for AI response formatting.

## License
MIT

## Credits
- Built by Datalynx, powered by Gemini API.
# Ai-Assistance-Project-
# Ai-Assistance-

from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
import os
import google.generativeai as genai

app = Flask(__name__)

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# Database configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASS"),
    'database': os.getenv("DB_NAME")
}
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def init_database():
    """Initialize database and create tables"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS ai_assistant")
        cursor.execute("USE ai_assistant")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                function_type VARCHAR(50) NOT NULL,
                prompt_style INT DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INT DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT,
                rating ENUM('helpful', 'not_helpful') NOT NULL,
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INT DEFAULT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")

class AIAssistant:
    """AI Assistant with different functions using Google Gemini API"""
    
    @staticmethod
    def call_gemini_api(prompt, system_message="You are a helpful AI assistant."):
        """Make API call to Gemini models using google-generativeai SDK"""
        if not GEMINI_API_KEY:
            return "⚠️ API key not configured. Please set GEMINI_API_KEY in your environment."

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_message)
            response = model.generate_content(prompt)

            if hasattr(response, 'text') and response.text:
                return response.text

            # Fallback: extract from candidates/parts
            if getattr(response, 'candidates', None):
                for candidate in response.candidates:
                    parts = getattr(getattr(candidate, 'content', None), 'parts', [])
                    if parts:
                        texts = [getattr(part, 'text', '') for part in parts if getattr(part, 'text', '')]
                        if texts:
                            return "\n".join(texts)

            return "AI returned an unexpected response."

        except Exception as e:
            return f"An error occurred communicating with Gemini: {str(e)}"
    
    @staticmethod
    def answer_question(question, prompt_style=0):
        """Answer factual questions with different prompt styles"""
        prompts = [
            "You are a knowledgeable AI assistant. Your primary goal is to provide a direct, accurate, and concise answer to the user's question.Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are an expert educator. Your task is to not only answer the user's question but to explain the concept in a clear, educational manner. Use analogies, examples, and break down complex topics into easy-to-understand components.Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a university-level research analyst. Provide an expert-level, comprehensive analysis of the user's query. Your response must be well-structured, citing multiple perspectives or contrasting theories where applicable. Assume the user requires a nuanced, in-depth explanation.Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please answer this question thoroughly: {question}"
        return AIAssistant.call_gemini_api(prompt, system_message)
    
    @staticmethod
    def summarize_text(text, prompt_style=0):
        """Summarize given text using AI"""
        if len(text.strip()) < 50:
            return "The text provided is too short to summarize effectively. Please provide a longer text for summarization."
        
        prompts = [
            "You are an expert at text summarization. Create concise, accurate summaries that capture the main points. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a professional editor. Summarize the text by identifying key themes, main arguments, and essential details. Focus on clarity and brevity. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a content analyst. Provide a structured summary with bullet points covering main ideas, supporting details, and conclusions. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please summarize the following text, highlighting the key points:\n\n{text}"
        return AIAssistant.call_gemini_api(prompt, system_message)
    
    @staticmethod
    def generate_creative_content(prompt, prompt_style=0):
        """Generate creative content based on prompts"""
        prompts = [
            "You are a creative writing assistant. Generate engaging, original content based on user prompts. Be creative and imaginative. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a master storyteller. Create compelling narratives with vivid descriptions, emotional depth, and memorable characters. Focus on storytelling techniques. Do not use any emojis in your response and no *, ** symbols and ***bold*** or markdown formatting.",
            "You are an innovative content creator. Generate unique, thought-provoking content that challenges conventional thinking. Be bold and original. Do not use any emojis in your response and no *, ** symbols and ***bold*** or markdown formatting."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        api_prompt = f"Create creative content based on this prompt: {prompt}"
        return AIAssistant.call_gemini_api(api_prompt, system_message)
    
    @staticmethod
    def provide_advice(topic, prompt_style=0):
        """Provide advice on various topics"""
        prompts = [
            "You are a wise advisor. Provide practical, actionable advice on various topics. Be supportive and constructive. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a life coach. Give motivational advice with step-by-step action plans. Focus on personal growth and positive change. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a professional consultant. Provide strategic advice with evidence-based recommendations and potential outcomes. Be analytical and thorough. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please provide helpful advice about: {topic}"
        return AIAssistant.call_gemini_api(prompt, system_message)
    
    @staticmethod
    def analyze_text(text, prompt_style=0):
        """Analyze and critique text content"""
        if len(text.strip()) < 30:
            return "The text provided is too short to analyze effectively. Please provide a longer text for analysis."
        
        prompts = [
            "You are a literary critic. Analyze the text for themes, style, structure, and effectiveness. Provide constructive feedback and insights. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a content strategist. Evaluate the text for clarity, impact, and audience engagement. Suggest improvements and identify strengths. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a communication expert. Analyze the text for tone, messaging, and effectiveness. Focus on how well it achieves its intended purpose. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please analyze the following text:\n\n{text}"
        return AIAssistant.call_gemini_api(prompt, system_message)
    
    @staticmethod
    def solve_problem(problem, prompt_style=0):
        """Solve problems and provide solutions"""
        prompts = [
            "You are a problem-solving expert. Break down complex problems into manageable steps and provide clear, practical solutions. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a strategic thinker. Analyze problems from multiple angles and provide innovative solutions with pros and cons. Focus on long-term effectiveness. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a troubleshooting specialist. Identify root causes of problems and provide systematic solutions with implementation steps. Be methodical and thorough. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please help solve this problem: {problem}"
        return AIAssistant.call_gemini_api(prompt, system_message)
    
    @staticmethod
    def explain_concept(concept, prompt_style=0):
        """Explain complex concepts in simple terms"""
        prompts = [
            "You are an expert educator. Explain complex concepts in simple, easy-to-understand terms. Use analogies and examples to make difficult ideas accessible. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a science communicator. Break down complex concepts using clear language and relatable examples. Focus on making abstract ideas concrete and understandable. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response.",
            "You are a knowledge translator. Take complex concepts and explain them as if to someone with no background in the subject. Use everyday language and practical examples. Do not use any emojis, *, **, ***bold***, or markdown formatting in your response."
        ]
        
        system_message = prompts[prompt_style % len(prompts)]
        prompt = f"Please explain this concept in simple terms: {concept}"
        return AIAssistant.call_gemini_api(prompt, system_message)

@app.route('/')
def index():
    """Main page with function selection"""
    return render_template('index.html')

@app.route('/function/<function_type>')
def select_function(function_type):
    """Page to select prompt style for a specific function"""
    functions = {
        'question': {'name': 'Answer Questions', 'icon': '📚', 'description': 'Get factual answers to your questions'},
        'summarize': {'name': 'Summarize Text', 'icon': '📝', 'description': 'Summarize articles, documents, or any text content'},
        'creative': {'name': 'Generate Creative Content', 'icon': '✨', 'description': 'Create stories, poems, essays, or creative content'},
        'advice': {'name': 'Provide Advice', 'icon': '💡', 'description': 'Get helpful advice and tips on various topics'},
    }
    
    if function_type not in functions:
        return redirect(url_for('index'))
    
    return render_template('select_style.html', function_type=function_type, function_info=functions[function_type])

@app.route('/chat/<function_type>/<int:prompt_style>')
def chat_page(function_type, prompt_style):
    """Chat page for specific function and prompt style"""
    functions = {
        'question': {'name': 'Answer Questions', 'icon': '📚'},
        'summarize': {'name': 'Summarize Text', 'icon': '📝'},
        'creative': {'name': 'Generate Creative Content', 'icon': '✨'},
        'advice': {'name': 'Provide Advice', 'icon': '💡'},
    }
    
    if function_type not in functions:
        return redirect(url_for('index'))
    
    prompt_styles = [
        {'name': 'Standard', 'description': 'Balanced, professional responses'},
        {'name': 'Detailed', 'description': 'In-depth, educational approach'},
        {'name': 'Advanced', 'description': 'Expert-level, comprehensive analysis'}
    ]
    
    return render_template('chat.html', 
                         function_type=function_type, 
                         function_info=functions[function_type],
                         prompt_style=prompt_style,
                         prompt_style_info=prompt_styles[prompt_style])

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    data = request.json
    user_input = data.get('message', '')
    function_type = data.get('function', 'question')
    prompt_style = data.get('prompt_style', 0)
    
    if not user_input.strip():
        return jsonify({
            'response': 'Please enter a message.',
            'conversation_id': None,
            'function_type': function_type
        })
    
    # Process based on function type
    assistant = AIAssistant()
    
    try:
        if function_type == 'question':
            response = assistant.answer_question(user_input, prompt_style)
        elif function_type == 'summarize':
            response = assistant.summarize_text(user_input, prompt_style)
        elif function_type == 'creative':
            response = assistant.generate_creative_content(user_input, prompt_style)
        elif function_type == 'advice':
            response = assistant.provide_advice(user_input, prompt_style)
        elif function_type == 'analyze':
            response = assistant.analyze_text(user_input, prompt_style)
        elif function_type == 'solve':
            response = assistant.solve_problem(user_input, prompt_style)
        elif function_type == 'explain':
            response = assistant.explain_concept(user_input, prompt_style)
        else:
            response = "I'm not sure how to help with that. Please select a specific function."
        
    except Exception as e:
        response = f"An error occurred while processing your request: {str(e)}"
    
    # Save to database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO conversations (user_input, ai_response, function_type, prompt_style)
                VALUES (%s, %s, %s, %s)
            """, (user_input, response, function_type, prompt_style))
            connection.commit()
            conversation_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            return jsonify({
                'response': response,
                'conversation_id': conversation_id,
                'function_type': function_type
            })
        except Exception as e:
            return jsonify({
                'response': response,
                'conversation_id': None,
                'function_type': function_type,
                'db_error': str(e)
            })
    
    return jsonify({'response': response, 'conversation_id': None})

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission"""
    data = request.json
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO feedback (conversation_id, rating, comment)
            VALUES (%s, %s, %s)
        """, (conversation_id, rating, comment))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'status': 'success', 'message': 'Thank you for your feedback!'})
    
    return jsonify({'status': 'error', 'message': 'Failed to save feedback'})

@app.route('/history')
def history():
    connection = get_db_connection()
    conversations = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT c.id, c.user_input, c.ai_response, c.function_type, c.prompt_style, c.timestamp, f.rating, f.comment
            FROM conversations c
            LEFT JOIN feedback f ON c.id = f.conversation_id
            ORDER BY c.timestamp DESC
            LIMIT 50;
        """)
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'user_input': row[1],
                'ai_response': row[2],
                'function_type': row[3],
                'prompt_style': row[4],
                'timestamp': row[5],
                'feedback_rating': row[6],
                'feedback_comment': row[7]
            })
        cursor.close()
        connection.close()
    return render_template('history.html', conversations=conversations)

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5002)

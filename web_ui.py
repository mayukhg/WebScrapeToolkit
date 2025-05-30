"""
Web UI for AI-Powered Web Scraping Chatbot

This module provides a Flask-based web interface for the chatbot,
making it accessible through a browser with a clean, modern interface.
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from chatbot import WebScrapingChatbot
from models import db
from database_service import DatabaseService
import uuid


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Store chatbot instances per session
chatbot_instances = {}

# Create database tables
with app.app_context():
    db.create_all()


def get_chatbot(session_id, ai_provider="gemini"):
    """Get or create chatbot instance for session"""
    if session_id not in chatbot_instances:
        chatbot_instances[session_id] = WebScrapingChatbot(ai_provider=ai_provider)
    return chatbot_instances[session_id]


@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        ai_provider = data.get('ai_provider', 'gemini')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session'}), 400
        
        # Create a new chatbot instance if AI provider changed
        session_key = f"{session_id}_{ai_provider}"
        if session_key not in chatbot_instances:
            # Clean up old instance if it exists
            old_instances = [k for k in chatbot_instances.keys() if k.startswith(session_id)]
            for old_key in old_instances:
                chatbot_instances[old_key].close()
                del chatbot_instances[old_key]
            
            chatbot_instances[session_key] = WebScrapingChatbot(ai_provider=ai_provider)
        
        chatbot = chatbot_instances[session_key]
        response = chatbot.process_message(message)
        
        return jsonify({
            'response': response,
            'session_stats': chatbot.session_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Clear current session"""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in chatbot_instances:
            chatbot_instances[session_id].close()
            del chatbot_instances[session_id]
        
        session.pop('session_id', None)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        'ai_available': bool(os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')),
        'active_sessions': len(chatbot_instances)
    })


# Create templates directory and files
import os
os.makedirs('templates', exist_ok=True)

# Create the HTML template
chat_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Web Scraping Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            width: 900px;
            height: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.8;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }
        
        .message.user {
            align-items: flex-end;
        }
        
        .message.assistant {
            align-items: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            white-space: pre-wrap;
            line-height: 1.4;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            border: 1px solid #e0e0e0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .chat-input input:focus {
            border-color: #007bff;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        
        .chat-input button:hover {
            background: #0056b3;
        }
        
        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .status-bar {
            padding: 10px 20px;
            background: #f1f3f4;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .loading {
            opacity: 0.6;
        }
        
        .error {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .welcome-message {
            text-align: center;
            color: #666;
            padding: 40px 20px;
            font-style: italic;
        }
        
        .clear-button {
            background: #6c757d;
            font-size: 12px;
            padding: 8px 16px;
        }
        
        .clear-button:hover {
            background: #545b62;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 AI Web Scraping Assistant</h1>
            <p>Intelligent web scraping with natural language commands</p>
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="welcome-message">
                <p>Welcome! I can help you scrape websites and analyze content.</p>
                <p>Try: "Scrape https://example.com" or "help" for commands</p>
            </div>
        </div>
        
        <div class="status-bar">
            <span id="status">Ready</span>
            <button class="clear-button" onclick="clearSession()">Clear Session</button>
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Ask me to scrape a website or analyze content..." 
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendButton">Send</button>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const status = document.getElementById('status');
        
        let isLoading = false;
        
        // Check initial status
        checkStatus();
        
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.ai_available) {
                        status.textContent = 'AI features available';
                    } else {
                        status.textContent = 'Basic features only (API key needed for AI)';
                    }
                })
                .catch(() => {
                    status.textContent = 'Connection error';
                });
        }
        
        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Remove welcome message if it exists
            const welcome = messagesContainer.querySelector('.welcome-message');
            if (welcome) {
                welcome.remove();
            }
            
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function addError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = `Error: ${message}`;
            messagesContainer.appendChild(errorDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function setLoading(loading) {
            isLoading = loading;
            sendButton.disabled = loading;
            messageInput.disabled = loading;
            
            if (loading) {
                status.textContent = 'Processing...';
                messagesContainer.classList.add('loading');
            } else {
                messagesContainer.classList.remove('loading');
                checkStatus();
            }
        }
        
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isLoading) return;
            
            addMessage(message, true);
            messageInput.value = '';
            setLoading(true);
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                setLoading(false);
                
                if (data.error) {
                    addError(data.error);
                } else {
                    addMessage(data.response);
                    
                    // Update status with session stats
                    if (data.session_stats) {
                        const stats = data.session_stats;
                        status.textContent = `Pages scraped: ${stats.pages_scraped} | Links: ${stats.total_links_found}`;
                    }
                }
            })
            .catch(error => {
                setLoading(false);
                addError('Network error. Please try again.');
                console.error('Error:', error);
            });
        }
        
        function clearSession() {
            if (confirm('Clear the current session? This will reset all scraped data.')) {
                fetch('/api/clear', { method: 'POST' })
                    .then(() => {
                        messagesContainer.innerHTML = `
                            <div class="welcome-message">
                                <p>Session cleared! Ready to start fresh.</p>
                                <p>Try: "Scrape https://example.com" or "help" for commands</p>
                            </div>
                        `;
                        checkStatus();
                    })
                    .catch(error => {
                        addError('Failed to clear session');
                    });
            }
        }
        
        // Focus input on load
        messageInput.focus();
    </script>
</body>
</html>'''

# Write the template file
with open('templates/chat.html', 'w') as f:
    f.write(chat_template)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
// Global variables
let currentFunctionType = null;
let currentInteractionId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to function cards
    const functionCards = document.querySelectorAll('.function-card');
    functionCards.forEach(card => {
        card.addEventListener('click', function() {
            selectFunction(this.dataset.function);
        });
    });

    // Load initial statistics
    loadStats();
});

// Function selection handler
function selectFunction(functionType) {
    currentFunctionType = functionType;
    const functionInfo = getFunctionInfo(functionType);
    
    // Update the chat interface
    document.getElementById('currentFunction').textContent = functionInfo.name;
    document.getElementById('chatInterface').style.display = 'block';
    
    // Hide function selection
    document.querySelector('.function-selection').style.display = 'none';
    
    // Clear chat messages
    document.getElementById('chatMessages').innerHTML = '';
    
    // Add welcome message
    addMessage('assistant', `Welcome to ${functionInfo.name}! How can I help you today?`);
}

// Get function information
function getFunctionInfo(functionType) {
    const functions = {
        'question': { name: 'Answer Questions', description: 'Get factual answers to your questions' },
        'summarize': { name: 'Text Summarization', description: 'Summarize articles, documents, or any text content' },
        'generate': { name: 'Creative Content Generation', description: 'Generate stories, poems, essays, or creative content' },
        'advice': { name: 'Advice & Tips', description: 'Get helpful advice and tips on various topics' }
    };
    return functions[functionType];
}

// Send message function
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    userInput.value = '';
    
    // Get selected prompt style
    const promptSelect = document.getElementById(`prompt-${currentFunctionType}`);
    const promptIndex = promptSelect ? parseInt(promptSelect.value) : 0;
    
    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            function_type: currentFunctionType,
            query: message,
            prompt_index: promptIndex
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage('assistant', `Error: ${data.error}`);
        } else {
            addMessage('assistant', data.response);
            currentInteractionId = data.interaction_id;
            
            // Show feedback section
            document.getElementById('feedbackSection').style.display = 'block';
        }
    })
    .catch(error => {
        addMessage('assistant', `Error: ${error.message}`);
    });
}

// Add message to chat
function addMessage(sender, content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const name = sender === 'user' ? 'You' : 'AI Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <i class="${icon}"></i>
            <span class="message-sender">${name}</span>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${content}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Close chat function
function closeChat() {
    document.getElementById('chatInterface').style.display = 'none';
    document.querySelector('.function-selection').style.display = 'block';
    document.getElementById('feedbackSection').style.display = 'none';
    currentFunctionType = null;
    currentInteractionId = null;
}

// Submit feedback
function submitFeedback(feedback) {
    if (!currentInteractionId) return;
    
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            interaction_id: currentInteractionId,
            feedback: feedback
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Show comment input for negative feedback
            if (feedback === 'no') {
                document.getElementById('feedbackComment').style.display = 'block';
            } else {
                // Hide feedback section for positive feedback
                document.getElementById('feedbackSection').style.display = 'none';
                addMessage('assistant', 'Thank you for your feedback! 😊');
            }
            
            // Reload stats
            loadStats();
        }
    })
    .catch(error => {
        console.error('Error submitting feedback:', error);
    });
}

// Submit comment
function submitComment() {
    const comment = document.getElementById('commentInput').value.trim();
    
    if (!comment || !currentInteractionId) return;
    
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            interaction_id: currentInteractionId,
            feedback: 'no',
            comment: comment
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('feedbackSection').style.display = 'none';
            addMessage('assistant', 'Thank you for your detailed feedback! We\'ll use it to improve.');
            loadStats();
        }
    })
    .catch(error => {
        console.error('Error submitting comment:', error);
    });
}

// Load statistics
function loadStats() {
    fetch('/feedback-stats')
    .then(response => response.json())
    .then(data => {
        document.getElementById('totalInteractions').textContent = data.total_interactions;
        document.getElementById('positiveFeedback').textContent = data.positive_feedback;
        document.getElementById('negativeFeedback').textContent = data.negative_feedback;
        document.getElementById('feedbackRate').textContent = `${data.feedback_rate.toFixed(1)}%`;
    })
    .catch(error => {
        console.error('Error loading stats:', error);
    });
}

// Enter key support for textarea
document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

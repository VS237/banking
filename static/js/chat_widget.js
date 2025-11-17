// static/your_app/js/chat_widget.js
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure the page is fully loaded
    setTimeout(initializeChatWidget, 1000);
});

function initializeChatWidget() {
    // Check if chat widget already exists
    if (document.getElementById('chat-widget-container')) {
        return;
    }

    // Create chat widget HTML
    const chatWidgetHTML = `
        <div class="chat-widget" id="chat-widget-container">
            <div class="chat-icon" id="chat-icon">
                <i class="fas fa-comment-dots"></i>
            </div>
            <div class="chat-window" id="chat-window">
                <div class="chat-header">
                    <h3>Chat with Us</h3>
                    <button class="close-chat" id="close-chat">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="message bot">
                        <div class="message-content">
                            Hello! How can I help you today?
                        </div>
                    </div>
                </div>
                <div class="typing-indicator" id="typing-indicator">
                    Bot is typing...
                </div>
                <div class="chat-input">
                    <div class="input-group">
                        <input type="text" id="chat-message" placeholder="Type your message...">
                        <button id="send-message">Send</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inject chat widget into the page
    document.body.insertAdjacentHTML('beforeend', chatWidgetHTML);

    // Initialize chat functionality
    setupChatFunctionality();
}

function setupChatFunctionality() {
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatMessages = document.getElementById('chat-messages');
    const chatMessage = document.getElementById('chat-message');
    const sendMessage = document.getElementById('send-message');
    const typingIndicator = document.getElementById('typing-indicator');

    if (!chatIcon || !chatWindow) return;

    // Toggle chat window
    chatIcon.addEventListener('click', function() {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            chatMessage.focus();
        }
    });

    closeChat.addEventListener('click', function() {
        chatWindow.classList.remove('active');
    });

    // Send message function
    async function sendChatMessage() {
        const message = chatMessage.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatMessage.value = '';

        // Show typing indicator
        typingIndicator.classList.add('active');
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'user_' + Date.now()
                })
            });

            const data = await response.json();

            // Hide typing indicator
            typingIndicator.classList.remove('active');

            if (data.success) {
                addMessage(data.response, 'bot');
            } else {
                addMessage('Sorry, there was an error. Please try again.', 'bot');
            }

        } catch (error) {
            typingIndicator.classList.remove('active');
            addMessage('Sorry, I cannot respond at the moment. Please try again later.', 'bot');
        }
    }

    // Add message to chat
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners
    sendMessage.addEventListener('click', sendChatMessage);
    chatMessage.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/** Chat interface functionality for local LLM application. */
document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatContainer = document.querySelector('.chat-container');
    const welcomeScreen = document.querySelector('.welcome-screen');
    const inputField = document.querySelector('.input-field');
    const sendButton = document.querySelector('.send-button');

    /** Scrolls the chat container to the bottom. */
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    /** Toggles the send button state based on input content. */
    function toggleSendButton() {
        if (inputField.value.trim() !== '') {
            sendButton.classList.add('active');
        } else {
            sendButton.classList.remove('active');
        }
    }

    /** Creates a message element to display in the chat.
     * @param {string} message - The message content
     * @param {string} sender - The sender type ('user' or 'assistant')
     * @returns {HTMLElement} - The message element */
    function createMessageElement(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = message;
        
        messageBubble.appendChild(messageContent);
        messageDiv.appendChild(messageBubble);
        
        // Add model info if it's assistant response
        if (sender === 'assistant') {
            const messageInfo = document.createElement('div');
            messageInfo.className = 'message-info';
            
            const messageModel = document.createElement('div');
            messageModel.className = 'message-model';
            messageModel.innerHTML = '<span class="model-name">Chompers</span>';
            
            messageInfo.appendChild(messageModel);
            messageDiv.appendChild(messageInfo);
        }
        
        return messageDiv;
    }

    /** Shows typing indicator in chat. */
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const typingBubble = document.createElement('div');
        typingBubble.className = 'message-bubble';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-animation';
        typingContent.innerHTML = '<span></span><span></span><span></span>';
        
        typingBubble.appendChild(typingContent);
        typingDiv.appendChild(typingBubble);
        
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
    }

    /** Removes typing indicator from chat. */
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /** Sends message to the backend and handles the response. */
    function sendMessage() {
        const message = inputField.value.trim();
        
        if (message === '') return;
        
        // Show chat container and hide welcome screen if first message
        if (chatContainer.style.display === 'none') {
            chatContainer.style.display = 'flex';
            welcomeScreen.style.display = 'none';
        }
        
        // Add user message to chat
        const userMessage = createMessageElement(message, 'user');
        chatContainer.appendChild(userMessage);
        scrollToBottom();
        
        // Clear input field and reset height
        inputField.value = '';
        inputField.style.height = 'auto';
        toggleSendButton();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add assistant message to chat
            const assistantMessage = createMessageElement(data.message, 'assistant');
            
            // Update the model name if provided in response
            if (data.model) {
                const modelNameEl = assistantMessage.querySelector('.model-name');
                if (modelNameEl) {
                    modelNameEl.textContent = data.model;
                }
            }
            
            chatContainer.appendChild(assistantMessage);
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            
            // Show error message
            const errorMessage = createMessageElement('Sorry, there was an error processing your request. Please try again.', 'assistant');
            chatContainer.appendChild(errorMessage);
            scrollToBottom();
        });
    }

    // Event listeners
    inputField.addEventListener('input', toggleSendButton);
    
    sendButton.addEventListener('click', sendMessage);
    
    inputField.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // Initialize send button state
    toggleSendButton();
});
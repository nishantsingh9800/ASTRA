document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const messageContainer = document.getElementById('message-container');
    const clearBtn = document.getElementById('clear-btn');

    function scrollToBottom() {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        
        const content = document.createElement('div');
        content.className = 'content';
        content.textContent = text;
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        messageContainer.appendChild(msgDiv);
        scrollToBottom();
        return content;
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message astra typing';
        msgDiv.id = 'typing-indicator-msg';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        
        const content = document.createElement('div');
        content.className = 'content';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        for (let i=0; i<3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDiv.appendChild(dot);
        }
        
        content.appendChild(typingDiv);
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        messageContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typing-indicator-msg');
        if (el) el.remove();
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Add user message
        addMessage(text, 'user');
        chatInput.value = '';
        
        // 2. Add typing indicator
        addTypingIndicator();

        try {
            // 3. Send to Flask backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            // 4. Remove typing and show response
            removeTypingIndicator();
            if (data.response) {
                addMessage(data.response, 'astra');
            } else {
                addMessage("I'm sorry, I encountered an error processing that request.", 'astra');
            }
            
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage("Connection error. Is the ASTRA server running?", 'astra');
        }
    });

    clearBtn.addEventListener('click', () => {
        messageContainer.innerHTML = '';
        addMessage("Chat cleared. How can I assist you?", 'astra');
    });
});

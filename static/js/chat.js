// Add this to your existing chat.js file

const chatToggleBtn = document.getElementById('chat-toggle-btn');
const chatPanel = document.getElementById('chat-panel');
const chatCloseBtn = document.getElementById('chat-close-btn');
const chatPromptMessage = document.getElementById('chat-prompt-message');

// Toggle chat panel
chatToggleBtn.addEventListener('click', function() {
    chatPanel.classList.toggle('show');
    
    // Hide prompt message when chat is open
    if (chatPanel.classList.contains('show')) {
        chatPromptMessage.classList.add('hidden');
    } else {
        chatPromptMessage.classList.remove('hidden');
    }
});

// Close chat panel
chatCloseBtn.addEventListener('click', function() {
    chatPanel.classList.remove('show');
    chatPromptMessage.classList.remove('hidden');
});

// Close chat when clicking outside
document.addEventListener('click', function(event) {
    const isClickInsideChat = chatPanel.contains(event.target);
    const isClickOnToggle = chatToggleBtn.contains(event.target);
    
    if (!isClickInsideChat && !isClickOnToggle && chatPanel.classList.contains('show')) {
        chatPanel.classList.remove('show');
        chatPromptMessage.classList.remove('hidden');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // --- GSAP Animations ---
    gsap.registerPlugin(ScrollTrigger);

    // Staggered reveal for bento grid items
    gsap.utils.toArray('.gsap-reveal').forEach((elem, i) => {
        gsap.fromTo(elem, 
            { opacity: 0, y: 40 }, 
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: elem,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                }
            }
        );
    });

    // --- DOM Element References ---
    const chatWidget = {
        toggleBtn: document.getElementById('chat-toggle-btn'),
        panel: document.getElementById('chat-panel'),
        closeBtn: document.getElementById('chat-close-btn'),
        body: document.getElementById('chat-body'),
        form: document.getElementById('chat-form'),
        input: document.getElementById('chat-input'),
        suggestionChipsContainer: document.getElementById('suggestion-chips'),
        exportBtn: document.getElementById('export-chat-btn'),
    };

    const chatHistory = [];
    let isChatOpen = false;

    // --- Core Functions ---

    /**
     * Saves the current chat history to localStorage.
     */
    const saveChatHistory = () => {
        const maxMessages = 50;
        if (chatHistory.length > maxMessages) {
            chatHistory.splice(0, chatHistory.length - maxMessages);
        }
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    };

    /**
     * Loads chat history from localStorage and renders it.
     */
    const loadChatHistory = () => {
        const savedHistory = localStorage.getItem('chatHistory');
        chatHistory.length = 0; // Clear existing history
        if (savedHistory) {
            const parsedHistory = JSON.parse(savedHistory);
            chatHistory.push(...parsedHistory);
        }
        
        chatWidget.body.innerHTML = '';
        const greetingMessage = "Hi! I can help you learn about my skills, projects, or contact info.";
        if (!chatHistory.length || chatHistory[0].text !== greetingMessage) {
            chatHistory.unshift({ sender: 'agent', text: greetingMessage });
        }

        chatHistory.forEach(message => {
            addMessageToChat(message.sender, message.text, true); // Skip typing for history
        });
        
        // Scroll to bottom after loading history
        setTimeout(() => {
            chatWidget.body.scrollTop = chatWidget.body.scrollHeight;
        }, 100);
    };

    /**
     * Toggles the visibility of the chat panel with GSAP animations.
     */
    const toggleChatPanel = () => {
        isChatOpen = !isChatOpen;
        if (isChatOpen) {
            gsap.to(chatWidget.panel, { 
                display: 'flex',
                scale: 1, 
                opacity: 1,
                duration: 0.4, 
                ease: 'elastic.out(1, 0.75)' 
            });
            chatWidget.input.focus();
            renderSuggestionChips();
            // Ensure scroll to bottom when opening
            setTimeout(() => {
                chatWidget.body.scrollTop = chatWidget.body.scrollHeight;
            }, 100);
        } else {
            gsap.to(chatWidget.panel, { 
                scale: 0, 
                opacity: 0,
                duration: 0.2, 
                ease: 'power2.in',
                onComplete: () => { chatWidget.panel.style.display = 'none'; }
            });
        }
    };

    /**
     * Converts markdown to HTML in real-time during typing
     */
    const parseMarkdownRealtime = (text) => {
        // Basic markdown parsing for real-time display
        let html = text
            // Bold
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            // Code inline
            .replace(/`(.+?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        return html;
    };

    /**
     * Adds a message to the chat body UI.
     */
    const addMessageToChat = (sender, text, skipTyping = false) => {
        const messageId = `msg-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.id = messageId;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = sender === 'agent' ? 'A' : 'U';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (sender === 'user') {
            contentDiv.textContent = text;
        } else {
            // For agent messages, handle markdown
            if (skipTyping) {
                // Render markdown immediately for history
                if (typeof showdown !== 'undefined') {
                    const converter = new showdown.Converter();
                    contentDiv.innerHTML = converter.makeHtml(text);
                } else {
                    contentDiv.innerHTML = parseMarkdownRealtime(text);
                }
                contentDiv.classList.add('markdown');
            } else {
                // Will be filled by typing effect
                contentDiv.innerHTML = '';
            }
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatWidget.body.appendChild(messageDiv);
        
        setTimeout(() => {
            chatWidget.body.scrollTop = chatWidget.body.scrollHeight;
        }, 10);

        // Only add to history if it's a new message (not from history load)
        if (!skipTyping) {
            chatHistory.push({ sender, text });
            saveChatHistory();
        }

        // Start typing effect for new agent messages
        if (sender === 'agent' && !skipTyping) {
            typeAgentResponse(text, messageId);
        }

        return messageId;
    };

    const showTypingIndicator = () => {
        const messageId = `typing-${Date.now()}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message agent-message`;
        messageDiv.id = messageId;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = 'A';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatWidget.body.appendChild(messageDiv);

        setTimeout(() => {
            chatWidget.body.scrollTop = chatWidget.body.scrollHeight;
        }, 10);

        return messageId;
    };

    const removeTypingIndicator = (messageId) => {
        document.getElementById(messageId)?.remove();
    };

    const typeAgentResponse = (agentResponse, messageId) => {
        const messageDiv = document.getElementById(messageId);
        if (!messageDiv) return;
        
        const messageContent = messageDiv.querySelector('.message-content');
        if (!messageContent) return;

        messageContent.innerHTML = ''; // Clear any existing content
        
        let i = 0;
        const typingInterval = setInterval(() => {
            if (i < agentResponse.length) {
                i++;
                const currentText = agentResponse.substring(0, i);
                
                // Apply real-time markdown parsing
                messageContent.innerHTML = parseMarkdownRealtime(currentText);
                
                chatWidget.body.scrollTop = chatWidget.body.scrollHeight;
            } else {
                clearInterval(typingInterval);
                messageContent.classList.add('markdown');
                
                // Final render with full showdown if available
                if (typeof showdown !== 'undefined') {
                    const converter = new showdown.Converter();
                    messageContent.innerHTML = converter.makeHtml(agentResponse);
                }
            }
        }, 15); // Slightly faster typing speed
    };

    /**
     * Renders suggestion chips in the chat footer.
     */
    const renderSuggestionChips = () => {
        const suggestions = ["Projects", "Skills", "Contact"];
        chatWidget.suggestionChipsContainer.innerHTML = '';
        suggestions.forEach(text => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = text;
            chip.addEventListener('click', () => handleChipClick(text));
            chatWidget.suggestionChipsContainer.appendChild(chip);
        });
    };

    /**
     * Handles a click on a suggestion chip.
     */
    const handleChipClick = (text) => {
        const fullPrompts = {
            "Projects": "Show me your projects",
            "Skills": "What are your skills?",
            "Contact": "How can I contact you?"
        };
        chatWidget.input.value = fullPrompts[text] || text;
        chatWidget.form.dispatchEvent(new Event('submit'));
    };

    /**
     * Handles form submission to send a message to the agent.
     */
    const handleFormSubmit = async (e) => {
        e.preventDefault();
        const prompt = chatWidget.input.value.trim();
        if (!prompt) return;

        // Disable form to prevent multiple submissions
        chatWidget.input.disabled = true;
        chatWidget.form.querySelector('button').disabled = true;

        addMessageToChat('user', prompt);
        chatWidget.input.value = '';
        chatWidget.suggestionChipsContainer.innerHTML = '';

        const typingMessageId = showTypingIndicator();

        try {
            const response = await fetch('/api/agent/query/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ prompt }),
            });

            removeTypingIndicator(typingMessageId);

            if (response.headers.get('Content-Type')?.includes('text/calendar')) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'meeting.ics';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
                addMessageToChat('agent', "I've downloaded a meeting invite for you.");
                return;
            }

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            addMessageToChat('agent', data.text); // This will now trigger typing effect
            handleAgentAction(data.action, data.data);

        } catch (error) {
            console.error('Error querying agent:', error);
            removeTypingIndicator(typingMessageId);
            addMessageToChat('agent', "Sorry, something went wrong. Please try again.");
        } finally {
            // Re-enable form
            chatWidget.input.disabled = false;
            chatWidget.form.querySelector('button').disabled = false;
            chatWidget.input.focus();
            renderSuggestionChips();
        }
    };

    /**
     * Executes special actions returned by the agent.
     */
    const handleAgentAction = (action, data) => {
        if (!action) return;
        if (action === 'show_projects') {
            document.querySelector('.bento-item--projects')?.scrollIntoView({ behavior: 'smooth' });
        } else if (action === 'email' && data?.email) {
            window.location.href = `mailto:${data.email}`;
        }
    };

    /**
     * Exports the current chat conversation as a JSON file.
     */
    const exportChat = () => {
        if (chatHistory.length === 0) return;
        const blob = new Blob([JSON.stringify(chatHistory, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'chat-conversation.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    };

    /**
     * Helper function to get a cookie by name.
     */
    const getCookie = (name) => {
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
    };

    // --- Event Listeners ---
    chatWidget.toggleBtn.addEventListener('click', toggleChatPanel);
    chatWidget.closeBtn.addEventListener('click', toggleChatPanel);
    chatWidget.form.addEventListener('submit', handleFormSubmit);
    chatWidget.exportBtn.addEventListener('click', exportChat);

    // Initial state for chat panel
    gsap.set(chatWidget.panel, { scale: 0, opacity: 0, display: 'none' });

    // Load chat history on page load
    loadChatHistory();
});
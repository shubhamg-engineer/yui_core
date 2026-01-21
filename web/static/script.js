// Yui AI Companion - Frontend JavaScript
// Handles WebSocket communication, UI interactions, and real-time chat

let ws = null;
let userName = '';
let messageCount = 0;
let currentPersonality = 'yui';

// DOM Elements
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const userNameInput = document.getElementById('userName');
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const messageCountEl = document.getElementById('messageCount');
const connectionStatusEl = document.getElementById('connectionStatus');
const statusIndicator = document.getElementById('statusIndicator');
const clearBtn = document.getElementById('clearBtn');
const infoBtn = document.getElementById('infoBtn');
const personalityBtns = document.querySelectorAll('.personality-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if user name is saved
    const savedName = localStorage.getItem('yuiUserName');
    if (savedName) {
        userName = savedName;
        loginModal.style.display = 'none';
        connectWebSocket();
    }
});

// Login Form
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    userName = userNameInput.value.trim();

    if (userName) {
        localStorage.setItem('yuiUserName', userName);
        loginModal.style.display = 'none';
        connectWebSocket();
    }
});

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${encodeURIComponent(userName)}`;

    updateConnectionStatus('Connecting...', 'warning');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        updateConnectionStatus('Connected', 'success');
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('Error', 'error');
    };

    ws.onclose = () => {
        updateConnectionStatus('Disconnected', 'error');
        messageInput.disabled = true;
        sendBtn.disabled = true;

        // Attempt reconnect after 3 seconds
        setTimeout(() => {
            if (userName) {
                connectWebSocket();
            }
        }, 3000);
    };
}

// Handle incoming messages
function handleMessage(data) {
    const { type, content, personality, timestamp } = data;

    // Hide typing indicator
    typingIndicator.classList.remove('active');

    // Clear welcome message on first real message
    if (messageCount === 0 && type !== 'system') {
        chatMessages.innerHTML = '';
    }

    switch (type) {
        case 'system':
            addSystemMessage(content, timestamp);
            break;
        case 'assistant':
            addMessage(content, 'assistant', timestamp, personality);
            break;
        case 'user':
            addMessage(content, 'user', timestamp);
            break;
        case 'tool':
            addToolMessage(content, timestamp);
            break;
        case 'typing':
            typingIndicator.classList.add('active');
            break;
        case 'error':
            addSystemMessage(`❌ ${content}`, timestamp);
            break;
    }

    // Auto-scroll to bottom
    scrollToBottom();
}

// Add message to chat
function addMessage(content, role, timestamp, personality = null) {
    messageCount++;
    updateMessageCount();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : getPersonalityEmoji(personality);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = formatTime(timestamp);

    contentDiv.appendChild(bubble);
    contentDiv.appendChild(time);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
}

// Add system message
function addSystemMessage(content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;

    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
}

// Add tool result message
function addToolMessage(content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🔧';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Format tool content with line breaks
    bubble.innerHTML = content.replace(/\n/g, '<br>');

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = formatTime(timestamp);

    contentDiv.appendChild(bubble);
    contentDiv.appendChild(time);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
}

// Send message
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN) return;

    // Add user message to UI immediately
    const timestamp = new Date().toISOString();
    addMessage(message, 'user', timestamp);

    // Send to server
    ws.send(JSON.stringify({
        type: 'user',
        content: message
    }));

    // Clear input
    messageInput.value = '';
    messageInput.focus();
});

// Personality switching
personalityBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const personality = btn.dataset.personality;

        if (personality !== currentPersonality && ws && ws.readyState === WebSocket.OPEN) {
            // Send switch command
            ws.send(JSON.stringify({
                type: 'user',
                content: `/switch ${personality}`
            }));

            // Update UI
            personalityBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPersonality = personality;

            // Update header
            document.getElementById('chatTitle').textContent = `Chat with ${capitalize(personality)}`;
            document.getElementById('chatSubtitle').textContent = getPersonalityDescription(personality);
        }
    });
});

// Clear chat
clearBtn.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'user',
            content: '/clear'
        }));
    }
});

// Show info
infoBtn.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'user',
            content: '/info'
        }));
    }
});

// Helper functions
function updateConnectionStatus(status, type) {
    connectionStatusEl.textContent = status;

    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };

    statusIndicator.style.background = colors[type] || colors.warning;
}

function updateMessageCount() {
    messageCountEl.textContent = messageCount;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getPersonalityEmoji(personality) {
    const emojis = {
        yui: '🌙',
        friday: '💼',
        jarvis: '🎩'
    };
    return emojis[personality?.toLowerCase()] || '🌙';
}

function getPersonalityDescription(personality) {
    const descriptions = {
        yui: 'Emotionally intelligent AI companion',
        friday: 'Professional assistant mode',
        jarvis: 'Sophisticated AI butler'
    };
    return descriptions[personality.toLowerCase()] || 'AI Companion';
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Keyboard shortcuts
messageInput.addEventListener('keydown', (e) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Auto-resize textarea (if we convert input to textarea later)
function autoResize(element) {
    element.style.height = 'auto';
    element.style.height = element.scrollHeight + 'px';
}

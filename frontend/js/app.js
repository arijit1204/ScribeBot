/**
 * SCRIBE BOT JavaScript Web Client
 * Handles Async REST API calls, YouTube Player embeds, Markdown rendering, and live chat.
 * Authored by @Arijit Dutta
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const ytUrlInput = document.getElementById('ytUrlInput');
    const indexBtn = document.getElementById('indexBtn');
    const statusBadge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    const ytPlayer = document.getElementById('ytPlayer');
    const videoTitle = document.getElementById('videoTitle');
    const indexStatusTag = document.getElementById('indexStatusTag');
    const statusMessageAlert = document.getElementById('statusMessageAlert');
    const statusAlertText = document.getElementById('statusAlertText');
    const summaryContent = document.getElementById('summaryContent');
    const copySummaryBtn = document.getElementById('copySummaryBtn');
    const chatHistory = document.getElementById('chatHistory');
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const chipBtns = document.querySelectorAll('.chip');

    // State Variables
    let currentVideoId = null;
    let localChatHistory = [];

    // Configure Marked.js Options if available
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // Helper: Extract YouTube Video ID
    function extractVideoId(url) {
        if (!url) return null;
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }

    // Helper: Update Status Badge UI
    function updateStatus(state, text) {
        statusBadge.className = `status-pill status-${state}`;
        statusText.textContent = text;
    }

    // Helper: Display Alert Banner if present
    function showAlert(message, isError = false) {
        const statusAlertText = document.getElementById('statusAlertText');
        const statusMessageAlert = document.getElementById('statusMessageAlert');
        if (statusAlertText && statusMessageAlert) {
            statusAlertText.textContent = message;
            statusMessageAlert.className = `status-alert ${isError ? 'alert-error' : 'alert-success'}`;
            statusMessageAlert.classList.remove('hidden');
        }
    }


    // Embed YouTube Video in iframe
    function loadVideoEmbed(videoId) {
        currentVideoId = videoId;
        ytPlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=0&enablejsapi=1`;
        videoPlaceholder.classList.add('hidden');
        ytPlayer.classList.remove('hidden');
        videoTitle.textContent = `YouTube Video ID: ${videoId}`;
    }

    // Index Video Action
    async function handleIndexVideo() {
        const url = ytUrlInput.value.trim();
        if (!url) {
            alert('Please enter a valid YouTube Video URL.');
            return;
        }

        const videoId = extractVideoId(url);
        if (videoId) {
            loadVideoEmbed(videoId);
        }

        // UI Loading State
        updateStatus('loading', 'Indexing Transcript...');
        indexStatusTag.textContent = 'Processing...';
        indexBtn.disabled = true;
        indexBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Indexing...';
        summaryContent.innerHTML = '<p class="summary-placeholder-text"><i class="fa-solid fa-spinner fa-spin"></i> Fetching captions & generating AI summary...</p>';

        try {
            const response = await fetch('/api/index', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ youtube_url: url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to index video');
            }

            // Success State
            updateStatus('success', 'Indexed & Ready');
            indexStatusTag.textContent = 'Indexed ✅';
            showAlert(data.message, false);

            // Render Summary
            if (window.marked && data.summary) {
                summaryContent.innerHTML = marked.parse(data.summary);
            } else {
                summaryContent.textContent = data.summary || 'Summary generated successfully.';
            }
            copySummaryBtn.classList.remove('hidden');

            // Add system note to chat
            appendMessage('assistant', `Video indexed successfully! I've loaded the transcript. Feel free to ask me anything about it.`);


        } catch (error) {
            console.error('Indexing Error:', error);
            updateStatus('error', 'Indexing Failed');
            indexStatusTag.textContent = 'Error ❌';
            showAlert(`Error: ${error.message}`, true);
            summaryContent.innerHTML = `<p style="color: var(--yt-red);"><i class="fa-solid fa-circle-exclamation"></i> ${error.message}</p>`;
        } finally {
            indexBtn.disabled = false;
            indexBtn.innerHTML = 'Index Video <i class="fa-solid fa-arrow-right"></i>';
        }

    }

    // Send Question Action
    async function handleSendQuestion() {
        const question = questionInput.value.trim();
        if (!question) return;

        // Clear input field immediately
        questionInput.value = '';

        // Append User Message to UI
        appendMessage('user', question);

        // Show Typining Loading Indicator
        const loadingId = appendLoadingMessage();

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    chat_history: localChatHistory
                })
            });

            const data = await response.json();

            // Remove loading indicator
            removeMessage(loadingId);

            if (!response.ok) {
                throw new Error(data.detail || 'Error getting answer');
            }

            // Append Assistant Answer to UI
            appendMessage('assistant', data.answer);

            // Update local history
            localChatHistory = data.chat_history || [];

        } catch (error) {
            console.error('Query Error:', error);
            removeMessage(loadingId);
            appendMessage('assistant', `⚠️ **Error**: ${error.message}`);
        }
    }

    // Append Chat Message to UI
    function appendMessage(role, content) {
        const msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4);
        const bubble = document.createElement('div');
        bubble.id = msgId;
        bubble.className = `chat-bubble ${role}`;

        const isUser = role === 'user';
        const avatarIcon = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        const formattedContent = (window.marked && !isUser) ? marked.parse(content) : escapeHtml(content);

        bubble.innerHTML = `
            <div class="bubble-avatar">${avatarIcon}</div>
            <div class="bubble-content markdown-body">${formattedContent}</div>
        `;

        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return msgId;
    }

    // Append Loading Message
    function appendLoadingMessage() {
        const msgId = 'loading-' + Date.now();
        const bubble = document.createElement('div');
        bubble.id = msgId;
        bubble.className = 'chat-bubble assistant';

        bubble.innerHTML = `
            <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="bubble-content">
                <i class="fa-solid fa-spinner fa-spin"></i> Thinking...
            </div>
        `;

        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return msgId;
    }

    // Remove Message Element by ID
    function removeMessage(msgId) {
        const elem = document.getElementById(msgId);
        if (elem) elem.remove();
    }

    // Escape HTML string
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    // Event Listeners
    indexBtn.addEventListener('click', handleIndexVideo);
    sendBtn.addEventListener('click', handleSendQuestion);

    ytUrlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleIndexVideo();
    });

    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendQuestion();
    });

    clearChatBtn.addEventListener('click', async () => {
        localChatHistory = [];
        chatHistory.innerHTML = `
            <div class="system-welcome-msg">
                <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
                <div class="welcome-text">
                    <h4>Chat Context Cleared</h4>
                    <p>Enter a question below to start a fresh conversation about the video.</p>
                </div>
            </div>
        `;
        try {
            await fetch('/api/clear', { method: 'POST' });
        } catch (e) {
            console.error('Clear error', e);
        }
    });

    // Chip Click Listener
    chipBtns.forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            if (promptText) {
                questionInput.value = promptText;
                handleSendQuestion();
            }
        });
    });

    // Copy Summary Button
    copySummaryBtn.addEventListener('click', () => {
        const text = summaryContent.innerText;
        navigator.clipboard.writeText(text).then(() => {
            copySummaryBtn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--yt-green);"></i>';
            setTimeout(() => {
                copySummaryBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
            }, 2000);
        });
    });

    // Toggle Collapsible Chat Panel
    const toggleChatBtn = document.getElementById('toggleChatBtn');
    const expandChatBtn = document.getElementById('expandChatBtn');
    const mainLayout = document.querySelector('.yt-main-layout');

    function setChatCollapsed(collapsed) {
        if (!mainLayout) return;
        if (collapsed) {
            mainLayout.classList.add('chat-collapsed');
            if (expandChatBtn) expandChatBtn.classList.remove('hidden');
        } else {
            mainLayout.classList.remove('chat-collapsed');
            if (expandChatBtn) expandChatBtn.classList.add('hidden');
        }
    }

    if (toggleChatBtn) {
        toggleChatBtn.addEventListener('click', () => setChatCollapsed(true));
    }

    if (expandChatBtn) {
        expandChatBtn.addEventListener('click', () => setChatCollapsed(false));
    }
});


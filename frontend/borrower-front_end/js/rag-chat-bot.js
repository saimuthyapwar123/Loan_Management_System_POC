const CHAT_API_URL = "http://localhost:8000/chat/query";

// UI Elements
const chatbotBtn = document.getElementById("chatbotBtn");
const chatbox = document.getElementById("chatbox");
const closeChat = document.getElementById("closeChat");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatInput");
const chatBody = document.getElementById("chatBody");

// Toggle
chatbotBtn.onclick = () => chatbox.classList.toggle("active");
closeChat.onclick = () => chatbox.classList.remove("active");

// Events
sendBtn.onclick = sendMessage;
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    appendUser(message);
    chatInput.value = "";

    const thinking = appendBot("✨Thinking... 🤔");

    try {
        const res = await fetch(CHAT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: message, k: 3 })
        });

        const data = await res.json();
        thinking.remove();

        if (!res.ok) {
            appendBot("I’m unable to answer this right now.");
            return;
        }

        appendBot(data.answer);

    } catch (err) {
        thinking.remove();
        appendBot("Unable to connect. Please try again later.");
        console.error(err);
    }
}

// Helpers
function appendUser(text) {
    const div = document.createElement("div");
    div.className = "user-msg";
    div.textContent = text;
    chatBody.appendChild(div);
    scroll();
}

function appendBot(text) {
    const div = document.createElement("div");
    div.className = "bot-msg";
    div.textContent = text;
    chatBody.appendChild(div);
    scroll();
    return div;
}

function scroll() {
    chatBody.scrollTop = chatBody.scrollHeight;
}

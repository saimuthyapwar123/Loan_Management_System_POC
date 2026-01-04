// ===============================
// AUTHENTICATED CHAT CONFIG
// ===============================

const AUTH_CHAT_URL =
    "http://localhost:8000/Generative_AI_loan_assistant/chat";

// UI Elements
const chatbotBtn = document.getElementById("chatbotBtn");
const chatbox = document.getElementById("chatbox");
const closeChat = document.getElementById("closeChat");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatInput");
const chatBody = document.getElementById("chatBody");

// ===============================
// THREAD ID (CRITICAL FOR MEMORY)
// ===============================

// One thread per logged-in user session
let THREAD_ID = localStorage.getItem("auth_thread_id");

if (!THREAD_ID) {
    THREAD_ID = `auth_chat_${Date.now()}`;
    localStorage.setItem("auth_thread_id", THREAD_ID);
}

// ===============================
// UI EVENTS
// ===============================

chatbotBtn.onclick = () => chatbox.classList.toggle("active");
closeChat.onclick = () => chatbox.classList.remove("active");

sendBtn.onclick = sendMessage;
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

// ===============================
// SEND MESSAGE
// ===============================

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
        appendBot("Please login first.");
        return;
    }

    appendUser(message);
    chatInput.value = "";

    const thinking = appendBot("✨ Thinking...");

    try {
        const res = await fetch(AUTH_CHAT_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                query: message,
                thread_id: THREAD_ID 
            })
        });

        const data = await res.json();
        thinking.remove();

        if (!res.ok) {
            appendBot(data.detail || "Request failed.");
            return;
        }

        appendBot(data.answer);

    } catch (err) {
        thinking.remove();
        appendBot("Server connection failed.");
        console.error(err);
    }
}

// ===============================
// HELPERS
// ===============================

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

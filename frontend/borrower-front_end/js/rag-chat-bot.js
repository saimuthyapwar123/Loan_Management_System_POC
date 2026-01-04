// ===============================
// CONFIG
// ===============================
const CHAT_API_URL = "http://localhost:8000/chat/query";

// ===============================
// STABLE THREAD ID (SESSION)
// survives icon toggle, clears on reload
// ===============================
let threadId = sessionStorage.getItem("thread_id");

if (!threadId) {
    threadId = "public_" + crypto.randomUUID();
    sessionStorage.setItem("thread_id", threadId);
}

// ===============================
// UI ELEMENTS
// ===============================
const chatbotBtn = document.getElementById("chatbotBtn");
const chatbox = document.getElementById("chatbox");
const closeChat = document.getElementById("closeChat");
const sendBtn = document.getElementById("sendBtn");
const chatInput = document.getElementById("chatInput");
const chatBody = document.getElementById("chatBody");

// ===============================
// TOGGLE CHAT (NO CLEARING HERE ❗)
// ===============================
chatbotBtn.onclick = () => chatbox.classList.toggle("active");
closeChat.onclick = () => chatbox.classList.remove("active");

// ===============================
// EVENTS
// ===============================
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

    appendUser(message);
    chatInput.value = "";

    const thinking = appendBot("✨ Thinking...");

    try {
        const res = await fetch(CHAT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: message,
                thread_id: threadId   // 🔥 MEMORY KEY
            })
        });

        const data = await res.json();
        thinking.remove();

        if (!res.ok) {
            appendBot("Unable to answer now.");
            return;
        }

        appendBot(data.answer);

    } catch (err) {
        thinking.remove();
        appendBot("Server unavailable.");
        console.error(err);
    }
}

// ===============================
// UI HELPERS
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

// ===============================
// CLEAR ONLY ON PAGE RELOAD
// ===============================
window.addEventListener("beforeunload", () => {
    sessionStorage.removeItem("thread_id");
});

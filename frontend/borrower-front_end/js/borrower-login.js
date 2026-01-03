const API_BASE_URL = "http://localhost:8000";

async function loginBorrower() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const messageEl = document.getElementById("message");

    messageEl.innerText = "";
    messageEl.className = "message";

    if (!username || !password) {
        messageEl.innerText = "Username and password are required";
        messageEl.classList.add("error");
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/loan_auth/borrower/login`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            messageEl.innerText = data.detail || "Invalid credentials";
            messageEl.classList.add("error");
            return;
        }

        // ✅ Save auth info
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("token_type", data.token_type);
        localStorage.setItem("role", "BORROWER");

        if (data.borrower_id) {
            localStorage.setItem("borrower_id", data.borrower_id);
        }

        // ✅ Redirect
        window.location.href = "borrower-dashboard.html";

    } catch (err) {
        console.error("Borrower login error:", err);
        messageEl.innerText = "Server unreachable. Try again later.";
        messageEl.classList.add("error");
    }
}

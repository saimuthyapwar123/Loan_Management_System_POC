const API_BASE_URL = "http://localhost:8000";

async function loginAdmin() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const messageEl = document.getElementById("message");

    messageEl.innerText = "";

    if (!username || !password) {
        messageEl.innerText = "Username and password are required";
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/loan_auth/admin/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            messageEl.innerText = data.detail || "Invalid admin credentials";
            return;
        }

        // Save auth data
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("token_type", data.token_type);
        localStorage.setItem("role", "ADMIN");

        // Redirect admin dashboard
        window.location.href = "admin-dashboard.html";

    } catch (err) {
        console.error("Admin login error:", err);
        messageEl.innerText = "Server unreachable. Try again later.";
    }
}

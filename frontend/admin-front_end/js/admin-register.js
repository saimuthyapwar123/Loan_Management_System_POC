const API_BASE_URL = "http://localhost:8000";

async function registerAdmin() {
    const messageEl = document.getElementById("message");

    // Reset message state
    messageEl.className = "message";
    messageEl.innerText = "";

    // Build payload (MATCHES RegisterUser model)
    const payload = {
        username: document.getElementById("username").value.trim(),
        password: document.getElementById("password").value.trim(),
        first_name: document.getElementById("first_name").value.trim(),
        last_name: document.getElementById("last_name").value.trim(),
        dob: document.getElementById("dob")?.value || null,
        address: document.getElementById("address")?.value.trim() || null,
        email: document.getElementById("email")?.value.trim() || null,
        aadhar_number: document.getElementById("aadhar_number")
            ? document.getElementById("aadhar_number").value.trim()
            : null,
        pan_number: document.getElementById("pan_number")
            ? document.getElementById("pan_number").value.trim().toUpperCase()
            : null
    };

    // Minimal frontend validation
    if (!payload.username || !payload.password) {
        messageEl.className = "message error";
        messageEl.innerText = "Username and password are required";
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/loan_auth/admin/register`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        /* =========================
           ❌ ERROR FROM BACKEND
           ========================= */
        if (!response.ok) {
            messageEl.className = "message error";

            // 1️⃣ Pydantic validation errors (422)
            if (Array.isArray(data.detail)) {
                messageEl.innerText = data.detail
                    .map(err => {
                        const field = err.loc?.[1] || "field";
                        return `${field}: ${err.msg}`;
                    })
                    .join("\n");
            }
            // 2️⃣ HTTPException(detail="...")
            else if (typeof data.detail === "string") {
                messageEl.innerText = data.detail;
            }
            // 3️⃣ Fallback
            else {
                messageEl.innerText = "Registration failed";
            }

            return;
        }

        /* =========================
           ✅ SUCCESS (ROUTER MESSAGE)
           ========================= */
        messageEl.className = "message success";
        messageEl.innerText = data.message;

        // Optional redirect
        setTimeout(() => {
            window.location.href = "index.html";
        }, 2000);

    } catch (error) {
        console.error("Admin registration error:", error);
        messageEl.className = "message error";
        messageEl.innerText = "Server unreachable. Try again later.";
    }
}

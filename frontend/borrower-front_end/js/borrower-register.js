const API_BASE_URL = "http://localhost:8000";

async function registerBorrower() {
    const message = document.getElementById("message");

    message.className = "message";
    message.innerText = "";

    const payload = {
        username: document.getElementById("username").value.trim(),
        password: document.getElementById("password").value.trim(),
        first_name: document.getElementById("first_name").value.trim(),
        last_name: document.getElementById("last_name").value.trim(),
        dob: document.getElementById("dob").value || null,
        address: document.getElementById("address").value.trim() || null,
        email: document.getElementById("email").value.trim() || null,
        aadhar_number: document.getElementById("aadhar_number").value.trim() || null,
        pan_number: document.getElementById("pan_number").value.trim().toUpperCase() || null
    };

    // Basic validation
    if (!payload.username || !payload.password) {
        message.className = "message error";
        message.innerText = "Username and password are required";
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/loan_auth/borrower/register`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        // ❌ Backend validation / business error
        if (!response.ok) {
            message.className = "message error";

            if (Array.isArray(data.detail)) {
                message.innerText = data.detail
                    .map(err => `${err.loc?.[1]}: ${err.msg}`)
                    .join("\n");
            } else {
                message.innerText = data.detail || "Registration failed";
            }
            return;
        }

        // ✅ Success
        message.className = "message success";
        message.innerText = data.message || "Registration successful 🎉";

        setTimeout(() => {
            window.location.href = "index.html";
        }, 1200);

    } catch (err) {
        console.error("Borrower register error:", err);
        message.className = "message error";
        message.innerText = "Server error. Please try again later.";
    }
}

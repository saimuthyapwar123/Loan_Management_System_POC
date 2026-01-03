const API = "http://localhost:8000";

async function applyLoan() {
    const loan_type = document.getElementById("loan_type").value;
    const credit_score = Number(document.getElementById("credit_score").value);
    const principal = Number(document.getElementById("principal").value);
    const tenure_months = Number(document.getElementById("tenure_months").value);
    const messageBox = document.getElementById("message");

    // Reset message
    messageBox.className = "message";
    messageBox.innerText = "";

    // Frontend validation
    if (!loan_type || !credit_score || !principal || !tenure_months) {
        messageBox.classList.add("error");
        messageBox.innerText = "All fields are required.";
        return;
    }

    if (credit_score < 650 || credit_score > 900) {
        messageBox.classList.add("error");
        messageBox.innerText = "Credit score must be between 650 and 900.";
        return;
    }

    const payload = {
        loan_type,
        credit_score,
        principal,
        tenure_months
    };

    try {
        const res = await fetch(`${API}/loans/apply`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        // ❌ Error from Python (HTTPException)
        if (!res.ok) {
            messageBox.classList.add("error");
            messageBox.innerText = data?.detail || "Loan application failed.";
            return;
        }

        // ✅ Success
        messageBox.classList.add("success");
        messageBox.innerText = "Loan applied successfully 🎉";

        // Optional redirect
        setTimeout(() => {
            window.location.href = "my-loans.html";
        }, 1500);

    } catch (error) {
        messageBox.classList.add("error");
        messageBox.innerText = "Unable to connect to server. Please try again.";
        console.error(error);
    }
}

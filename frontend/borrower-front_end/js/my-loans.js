async function loadMyLoans() {
    const message = document.getElementById("message");
    const tbody = document.querySelector("#loanTable tbody");

    try {
        const res = await fetch("http://localhost:8000/loans/my-loans", {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        });

        const data = await res.json();

        if (!res.ok) {
            message.className = "error";
            message.innerText = data.detail || "Failed to load loans";
            return;
        }

        if (!Array.isArray(data) || data.length === 0) {
            message.innerText = "No loans applied yet";
            return;
        }

        tbody.innerHTML = "";

        data.forEach(loan => {
            tbody.insertAdjacentHTML("beforeend", `
                <tr>
                    <td>${loan.id}</td>
                    <td>${loan.loan_type || "-"}</td>
                    <td>₹ ${loan.principal?.toLocaleString() || "-"}</td>
                    <td>${loan.tenure_months || "-"}</td>
                    <td><strong>₹ ${loan.total_payable?.toLocaleString() || "-"}</strong></td>
                    <td class="status-${loan.status}">${loan.status}</td>
                    <td>₹ ${loan.remaining_balance?.toLocaleString() || "-"}</td>
                    <td>${loan.rejection_reason || "-"}</td>
                    <td>${loan.applied_at ? new Date(loan.applied_at).toLocaleDateString() : "-"}</td>
                </tr>
            `);
        });

    } catch (err) {
        console.error(err);
        message.className = "error";
        message.innerText = "Server error while loading loans";
    }
}

loadMyLoans();

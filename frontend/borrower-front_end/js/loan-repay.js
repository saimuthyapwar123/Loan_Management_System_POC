const API = "http://localhost:8000";

/**
 * Load DISBURSED loans only
 */
async function loadRepaymentLoans() {
    const tbody = document.querySelector("#repaymentTable tbody");
    const msg = document.getElementById("message");

    tbody.innerHTML = "";
    msg.innerText = "";

    try {
        const res = await fetch(`${API}/loans/my-loans`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        });

        const loans = await res.json();

        if (!res.ok) {
            msg.innerText = loans.detail || "Failed to load loans";
            return;
        }

        // ✅ ONLY DISBURSED LOANS
        const disbursedLoans = loans.filter(
            loan => loan.status === "DISBURSED"
        );

        if (disbursedLoans.length === 0) {
            msg.innerText = "No DISBURSED loans available for repayment";
            return;
        }

        disbursedLoans.forEach(loan => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${loan.id}</td>
                <td>${loan.loan_type}</td>
                <td>${loan.tenure_months}</td> <!-- ✅ TENURE -->
                <td>₹${loan.remaining_balance.toLocaleString()}</td>
                <td>
                    <button 
                        class="btn-pay"
                        ${loan.remaining_balance <= 0 ? "disabled" : ""}
                        onclick="goToPayPage('${loan.id}', ${loan.remaining_balance})">
                        Pay
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        msg.innerText = "Server error while loading repayment loans";
    }
}

/**
 * Redirect to payment page
 */
function goToPayPage(loanId, remaining) {
    window.location.href =
        `pay-loan.html?loan_id=${loanId}&remaining=${remaining}`;
}

// Load on page open
loadRepaymentLoans();

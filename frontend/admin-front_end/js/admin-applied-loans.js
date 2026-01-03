const tableBody = document.getElementById("loanTableBody");
const rejectModal = document.getElementById("rejectModal");
const rejectReason = document.getElementById("rejectReason");

let selectedLoanId = null;

async function loadAppliedLoans() {
    tableBody.innerHTML = "<tr><td colspan='8'>Loading...</td></tr>";

    const res = await fetch(
        "http://127.0.0.1:8000/loans_list/list_of_applied_loan",
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    );

    const data = await res.json();
    tableBody.innerHTML = "";

    if (!Array.isArray(data)) {
        tableBody.innerHTML = "<tr><td colspan='8'>No applied loans</td></tr>";
        return;
    }

    data.forEach(item => {
        const loan = item.loan;

        tableBody.innerHTML += `
            <tr>
                <td>${item.name}</td>
                <td>${item.aadhar_number}</td>
                <td>${item.pan_number || "N/A"}</td>
                <td>${loan.loan_type}</td>
                <td>${loan.credit_score}</td>
                <td>${loan.tenure_months}</td>
                <td>₹ ${loan.principal}</td>

                <td>${new Date(loan.applied_at).toLocaleDateString()}</td>
                <td>
                    <button class="approve-btn" onclick="approveLoan('${loan.id}')">Approve</button>
                    <button class="reject-btn" onclick="openRejectModal('${loan.id}')">Reject</button>
                </td>
            </tr>
        `;
    });
}

async function approveLoan(loanId) {
    if (!confirm("Approve this loan?")) return;

    const res = await fetch(
        `http://127.0.0.1:8000/loans/${loanId}/approve`,
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    );

    const data = await res.json();
    if (!res.ok) {
        alert(data.detail || "Approval failed");
        return;
    }

    alert("Loan Approved");
    loadAppliedLoans();
}

/* REJECT FLOW */
function openRejectModal(loanId) {
    selectedLoanId = loanId;
    rejectReason.value = "";
    rejectModal.style.display = "flex";
}

function closeRejectModal() {
    rejectModal.style.display = "none";
}

async function confirmReject() {
    if (!rejectReason.value.trim()) {
        alert("Please enter rejection reason");
        return;
    }

    const res = await fetch(
        `http://127.0.0.1:8000/loans/${selectedLoanId}/reject`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            },
            body: JSON.stringify({ reason: rejectReason.value })
        }
    );

    const data = await res.json();
    if (!res.ok) {
        alert(data.detail || "Reject failed");
        return;
    }

    alert("Loan Rejected");
    closeRejectModal();
    loadAppliedLoans();
}

loadAppliedLoans();

const tableBody = document.getElementById("loanTableBody");

async function loadApprovedLoans() {
    const res = await fetch(
        "http://127.0.0.1:8000/loans_list/list_of_approved_loans",
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    );

    const data = await res.json();
    tableBody.innerHTML = "";

    if (!Array.isArray(data)) {
        tableBody.innerHTML =
            "<tr><td colspan='7'>No approved loans</td></tr>";
        return;
    }

    data.forEach(item => {
        tableBody.innerHTML += `
        <tr>
            <td>${item.name}</td>
            <td>${item.aadhar_number}</td>
            <td>${item.loan.loan_type || "-"}</td>
            <td>₹ ${item.loan.principal || "-"}</td>
            <td>${item.loan.tenure_months || "-"}</td>
            <td>
              <span class="status-badge status-approved">APPROVED</span>
            </td>
            <td>
              <button class="disburse-btn"
                onclick="disburseLoan('${item.loan.id}')">
                Disburse
              </button>
            </td>
        </tr>
        `;
    });
}

async function disburseLoan(loanId) {
    if (!confirm("Are you sure you want to DISBURSE this loan?")) return;

    const res = await fetch(
        `http://127.0.0.1:8000/loans/${loanId}/disburse`,
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    );

    const data = await res.json();
    alert(data.message || "Loan disbursed");

    loadApprovedLoans();
}

loadApprovedLoans();

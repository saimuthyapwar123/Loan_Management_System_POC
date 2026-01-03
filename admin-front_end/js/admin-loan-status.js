const tableBody = document.getElementById("loanTableBody");
const statusFilter = document.getElementById("statusFilter");

statusFilter.addEventListener("change", loadLoans);
document.addEventListener("DOMContentLoaded", loadLoans);

function getStatusClass(status) {
    return {
        APPLIED: "status-applied",
        APPROVED: "status-approved",
        DISBURSED: "status-disbursed",
        REJECTED: "status-rejected",
        CLOSED: "status-closed"
    }[status] || "";
}

async function loadLoans() {
    const status = statusFilter.value;
    tableBody.innerHTML = `<tr><td colspan="9">Loading...</td></tr>`;

    try {
        const res = await fetch(
            `http://127.0.0.1:8000/loans_list/list?status=${status}`,
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`
                }
            }
        );

        const data = await res.json();
        tableBody.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            tableBody.innerHTML =
                `<tr><td colspan="9">No loans found</td></tr>`;
            return;
        }

        data.forEach(item => {
            const loan = item.loan || {};

            tableBody.insertAdjacentHTML("beforeend", `
                <tr>
                    <td>${item.name || "N/A"}</td>
                    <td>${item.email || "N/A"}</td>
                    <td>${item.aadhar_number || "N/A"}</td>

                    <td>${loan.loan_type || "-"}</td>
                    <td>₹ ${loan.principal ? loan.principal.toLocaleString() : "-"}</td>
                    <td>${loan.tenure_months ? loan.tenure_months + " months" : "-"}</td>

                    <td>
                        ₹ ${loan.total_payable ? loan.total_payable.toLocaleString() : "-"}
                    </td>

                    <td>
                        <span class="status-badge ${getStatusClass(loan.status)}">
                            ${loan.status || "-"}
                        </span>
                    </td>

                    <td>
                        ${loan.status === "REJECTED"
                            ? (loan.rejection_reason || "No reason provided")
                            : "-"}
                    </td>
                </tr>
            `);
        });

    } catch (err) {
        console.error("Failed to load loans", err);
        tableBody.innerHTML =
            `<tr><td colspan="9">Failed to load data</td></tr>`;
    }
}

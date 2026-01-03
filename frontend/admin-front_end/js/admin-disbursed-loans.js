const tableBody = document.getElementById("loanTableBody");

async function loadDisbursedLoans() {
    try {
        const res = await fetch(
            "http://127.0.0.1:8000/loans_list/list_of_disbursed_loans",
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
                "<tr><td colspan='8'>No disbursed loans</td></tr>";
            return;
        }

        data.forEach(item => {
            const loan = item.loan;

            tableBody.innerHTML += `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.aadhar_number || "N/A"}</td>
                    <td>${loan.loan_type || "-"}</td>
                    <td>₹ ${loan.principal?.toLocaleString() || "-"}</td>
                    <td>${loan.tenure_months || "-"}</td>

                    <td>
                        <strong>₹ ${loan.total_payable?.toLocaleString() || "-"}</strong>
                    </td>

                    <td>
                        <strong>₹ ${loan.remaining_balance?.toLocaleString() || "-"}</strong>
                    </td>

                    <td>
                        <span class="status-badge status-disbursed">
                            DISBURSED
                        </span>
                    </td>
                </tr>
            `;
        });


    } catch (err) {
        console.error("Failed to load disbursed loans", err);
        tableBody.innerHTML =
            "<tr><td colspan='8'>Error loading data</td></tr>";
    }
}

// Load on page open
loadDisbursedLoans();

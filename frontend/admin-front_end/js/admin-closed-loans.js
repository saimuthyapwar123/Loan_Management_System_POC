const tableBody = document.getElementById("loanTableBody");

async function loadClosedLoans() {
    try {
        const res = await fetch(
            "http://127.0.0.1:8000/loans_list/list_of_closed_loans",
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
                "<tr><td colspan='8'>No closed loans</td></tr>";
            return;
        }

        data.forEach(item => {
            const loan = item.loan;

            tableBody.insertAdjacentHTML("beforeend", `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.aadhar_number || "N/A"}</td>
                    <td>${loan.loan_type || "-"}</td>
                    <td>₹ ${loan.principal?.toLocaleString() || "-"}</td>
                    <td>${loan.tenure_months || "-"} months</td>
                    <td><strong>₹ ${loan.total_payable?.toLocaleString() || "-"}</strong></td>
                    <td>
                        <span class="status-badge status-closed">
                            CLOSED
                        </span>
                    </td>
                </tr>
            `);
        });

    } catch (err) {
        console.error("Failed to load closed loans", err);
        tableBody.innerHTML =
            "<tr><td colspan='8'>Error loading data</td></tr>";
    }
}

loadClosedLoans();

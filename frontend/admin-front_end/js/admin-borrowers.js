const tableBody = document.getElementById("borrowerTableBody");

async function loadBorrowers() {
    try {
        const res = await fetch(
            "http://127.0.0.1:8000/loan_auth/admin/users?role=BORROWER",
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
                "<tr><td colspan='4'>No borrowers found</td></tr>";
            return;
        }

        data.forEach(user => {
            tableBody.innerHTML += `
                <tr>
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.email || "N/A"}</td>
                    <td>${user.dob || "N/A"}</td>
                    <td>${user.aadhar_number || "N/A"}</td>
                    <td>${user.pan_number}</td>
                    <td>${user.address}</td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Failed to load borrowers", err);
        tableBody.innerHTML =
            "<tr><td colspan='4'>Error loading data</td></tr>";
    }
}

// Load on page open
loadBorrowers();

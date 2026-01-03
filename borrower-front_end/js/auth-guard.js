const token = localStorage.getItem("access_token");
const role = localStorage.getItem("role");

if (!token || role !== "BORROWER") {
    window.location.href = "index.html";
}

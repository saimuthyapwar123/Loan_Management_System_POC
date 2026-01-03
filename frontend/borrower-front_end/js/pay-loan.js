const API = "http://localhost:8000";

const params = new URLSearchParams(window.location.search);
const loanId = params.get("loan_id");
const remaining = Number(params.get("remaining"));

document.getElementById("loanInfo").innerText =
  `Loan ID: ${loanId} | Remaining: ₹${remaining}`;

function handlePaymentMode() {
  const mode = document.getElementById("paymentMethod").value;

  document.getElementById("upiField").classList.add("hidden");
  document.getElementById("debitField").classList.add("hidden");
  document.getElementById("creditField").classList.add("hidden");

  if (mode === "UPI") {
    document.getElementById("upiField").classList.remove("hidden");
  }
  if (mode === "DEBIT") {
    document.getElementById("debitField").classList.remove("hidden");
  }
  if (mode === "CREDIT") {
    document.getElementById("creditField").classList.remove("hidden");
  }
}

async function payLoan() {
  const method = document.getElementById("paymentMethod").value;
  const amount = Number(document.getElementById("amount").value);
  const msg = document.getElementById("message");

  msg.innerText = "";

  if (!method) {
    msg.innerText = "Select a payment method";
    return;
  }

  if (!amount || amount <= 0) {
    msg.innerText = "Enter a valid amount";
    return;
  }

  if (amount > remaining) {
    msg.innerText = "Amount exceeds remaining balance";
    return;
  }

  if (method === "UPI") {
    const upi = document.getElementById("upiId").value.trim();
    if (!upi || !upi.includes("@")) {
      msg.innerText = "Enter valid UPI ID";
      return;
    }
  }

  if (method === "DEBIT") {
    const debit = document.getElementById("debitCard").value.trim();
    if (debit.length < 16) {
      msg.innerText = "Enter valid Debit Card number";
      return;
    }
  }

  if (method === "CREDIT") {
    const credit = document.getElementById("creditCard").value.trim();
    if (credit.length < 16) {
      msg.innerText = "Enter valid Credit Card number";
      return;
    }
  }

  const res = await fetch(
    `${API}/loans/${loanId}/repay?amount=${amount}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`
      }
    }
  );

  const data = await res.json();

  if (!res.ok) {
    msg.innerText = data.detail || "Payment failed";
    return;
  }

  msg.innerText = `Payment successful 🎉 Remaining ₹${data.remaining_balance}`;

  setTimeout(() => {
    window.location.href = "loan-repay.html";
  }, 5000);
}

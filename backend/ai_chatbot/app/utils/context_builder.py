def build_customer_context(borrower: dict | None, loans: list[dict]) -> str:
    if not borrower:
        return "Customer profile unavailable."

    first_name = borrower.get("first_name", "")
    last_name = borrower.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()

    context = f"""
        Customer Profile:
        Name: {full_name}
        Email: {borrower.get("email", "N/A")}
        Address: {borrower.get("address", "N/A")}
        """

    if loans:
        context += "\nLoans:\n"
        for loan in loans:
            context += (
                f"- Loan Type: {loan.get('loan_type')}, "
                f"Principal: {loan.get('principal')}, "
                f"Status: {loan.get('status')}\n"
            )
    else:
        context += "\nNo active loans found.\n"

    return context.strip()

from fastapi import HTTPException, status

class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="User already exists")

class PasswordPolicyException(HTTPException):
    def __init__(self): super().__init__(status_code=422, detail="Weak password or reuse")

class LoanNotFound(HTTPException):
    def __init__(self, loan_id):
        super().__init__(status_code=404, detail=f"Loan {loan_id} not found")

class InvalidLoanOperation(HTTPException):
    def __init__(self, msg="Invalid operation"):
        super().__init__(status_code=400, detail=msg)

class LoanAlreadyStatus(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
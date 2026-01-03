# AI Loan Management System

An **AI-powered Loan Management System** built with  **FastAPI** ,  **MongoDB** , and  **Generative AI (RAG + LLMs)** . This project automates the complete loan lifecycle for borrowers and administrators, while providing intelligent, policy-aware conversational AI assistance.

🔗 **GitHub Repository:** [https://github.com/saimuthyapwar123/AI_Loan_Management_System](https://github.com/saimuthyapwar123/AI_Loan_Management_System)

---

## 🚀 Project Overview

The **AI Loan Management System** is designed to simulate a modern digital banking platform with:

* Secure authentication using JWT
* Role-based access (Borrower & Admin)
* End-to-end loan lifecycle management
* AI-powered loan policy assistance using RAG (Retrieval-Augmented Generation)
* Conversational AI chatbot for borrowers and admins

The system combines **traditional backend banking workflows** with **Generative AI intelligence** to improve user experience and decision support.

---

## 🧰 Tech Stack

### 🔹 Backend

* **Python**
* **FastAPI** – High-performance API framework
* **Uvicorn** – ASGI server
* **Pydantic v2** – Data validation & schemas
* **JWT (python-jose)** – Authentication & authorization
* **Passlib + Bcrypt** – Secure password hashing

### 🔹 Database

* **MongoDB**
* **Motor (Async MongoDB driver)**
* **PyMongo**

### 🔹 AI / LLM / RAG Stack

* **LangChain**
* **LangGraph** (Multi-agent orchestration)
* **ChromaDB** (Vector Database)
* **Sentence Transformers** (Embeddings)
* **Google Gemini / Groq LLMs**
* **RAG (Retrieval-Augmented Generation)**

### 🔹 Document Processing

* **PyPDF** – PDF parsing
* **Docx2txt** – DOCX parsing

### 🔹 Utilities

* Requests, Python-Dotenv

---

## 👤 User Roles & Features

### 🧑‍💼 Borrower Features

1. **Register & Login** (JWT-based authentication)
2. **Apply for Loan**
   * Loan type, amount, tenure, credit score
3. **My Loans Dashboard**
   * View applied / approved / disbursed loans
4. **Loan Repayment**
   * Pay EMI using **UPI / Credit Card / Debit Card** (simulated)
5. **Auto Loan Closure**
   * When `remaining_balance = 0`, loan status automatically changes to **CLOSED**

#### 🤖 AI Assistance for Borrower

* **Login Page Chatbot**
  * AI answers questions using **loan policy documents**
* **Home Page Chatbot**
  * AI uses:
    * Loan policy documents (RAG)
    * Borrower-specific loan data from MongoDB

---

### 🧑‍💼 Admin Features

1. **Register & Login** (Admin-only access)
2. **Borrower Management**
   * View all registered borrowers
3. **Loan Management Dashboard**
   * View loans by status:
     * Applied
     * Approved
     * Disbursed
     * Rejected
     * Closed
4. **Loan Actions**
   * Approve loan
   * Reject loan (with reason)
   * Disburse loan
5. **Track Repayments**
   * Monitor borrower repayments

#### 🤖 AI Assistance for Admin

* **Login Page Chatbot**
* **Home Page Chatbot**
  * AI retrieves answers from **loan policy documents**
  * Helps admins understand policies and decisions

---

## 🧠 AI Architecture (RAG)

* Loan policies stored as documents (PDF / DOCX)
* Documents are split, embedded, and stored in **ChromaDB**
* User queries are:
  1. Embedded
  2. Matched against vector DB
  3. Passed to LLM with retrieved context
* Responses are **policy-grounded** (no hallucination)

---

## 🔐 Security & Access Control

* JWT-based authentication
* Role-based authorization (BORROWER / ADMIN)
* Secure password hashing
* Protected admin routes

---

## 📂 Key Modules

AI_Loan_Management_System/
├── backend/
|   ├──ai_chatbot/
|   |   ├── app/
|   |   ├── models/
|   │   ├── ai_routers/
|   │   ├── ai_services/
|   │   ├── database/
|   │   ├── ai_utils/
|   │   └── main.py
|   ├──console/
|   |   ├── app/
|   |   ├── models/
|   │   ├── routers/
|   │   ├── services/
|   │   ├── database/
|   │   ├── utils/
|   ├──main.py
|   └── requirements.txt
├── frontend/
│   ├── borrower/
│   └── admin/
└── README.md

---

## ▶️ How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/saimuthyapwar123/AI_Loan_Management_System.git
cd AI_Loan_Management_System
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```
MONGO_URI=your_mongodb_uri
JWT_SECRET_KEY=your_secret_key
LLM_API_KEY=your_llm_key
```

### 5️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

---

## 🎯 Key Highlights

* ✅ End-to-end loan lifecycle automation
* ✅ Secure JWT authentication
* ✅ Role-based access control
* ✅ AI-powered policy-aware chatbot
* ✅ RAG-based document retrieval
* ✅ MongoDB-backed borrower data context
* ✅ Clean admin & borrower dashboards

---

## 📌 Future Enhancements

* AI-based credit risk scoring
* Fraud detection
* Loan recommendation engine
* Multi-language chatbot
* Dashboard analytics

---

🔗 GitHub: [https://github.com/saimuthyapwar123](https://github.com/saimuthyapwar123)

---

⭐ If you find this project useful, please give it a star on GitHub!

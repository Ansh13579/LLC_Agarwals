# Closing Disclosure (CD) Benefit Extractor

This application is designed to ingest a Closing Disclosure (CD) PDF document and compute a Benefit Summary with two primary components as per standard specifications:
1. Savings Depicted by Cost (How Benefits Received)
2. Savings Depicted by Escrows & Payoff

It is built with a **Python (FastAPI)** backend to handle PDF extraction and calculation, and a **React/Vite** frontend to visualize the summary clearly.

## Features
- **Accurate Extraction:** Safely parses text out of PDFs using PyPDF2 and Regex patterns tailored to standard CD form sections.
- **Traceable Formulas:** Implements the exact formulas for finding benefits, separating negative values correctly like Lender Credits and Aggregate Adjustments.
- **Graceful Error Handling:** Treats missing fields as `$0.00` to allow calculations to succeed.
- **Clear output:** Formats outputs accurately with dollar signs and two decimal places in a web interface.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**

## How to Run

### 1. Backend (FastAPI) Setup
The backend runs on Python and provides the PDF processing endpoint.

1. Navigate to the API directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate.ps1 or .venv\Scripts\activate.bat
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python main.py
   # Or directly: uvicorn main:app --reload
   ```
The backend will run on `http://localhost:8000`.

### 2. Frontend (React + Vite) Setup
The frontend securely sends the selected PDF to the backend and formats the payload.

1. Open a new terminal and navigate to the UI directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
The interface will be available typically on `http://localhost:5173`. Open it in your browser, upload your CD document, and view the precise extracted result!

## Logic & Assumptions
- Missing fields in the PDF text fallback to `0.0`. 
- Explicit negations, like "Aggregate Adjustment" and "Lender Credits" are parsed and converted to floating-point negatives to ensure math behaves consistently (`Section D + Section E + Lender Credits (Negative value)`).
- Multiple properties under standard headings (e.g. multiple payoff values under 'Payoffs and Payments' page) are recursively found and summed automatically.
- Assumptions: PyPDF2 correctly captures the sequential text and amounts for target section headers without excessive artifacts breaking the regex boundaries. Where Quotes wrap numbers differently (like "Loan Amount"), fallback rules try standard matching.

## Live Deployment
- **Frontend (Live Demo):** [https://llc-garwals.vercel.app/](https://llc-garwals.vercel.app/)
- **Backend (FastAPI):** [https://abd420-llc-backend.hf.space](https://abd420-llc-backend.hf.space)

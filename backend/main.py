import re
import io
import PyPDF2
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Closing Disclosure API is running successfully!"}

def get_amount(line, next_line=""):
    amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', line)
    if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
    
    if next_line and not re.search(r'^\s*(0\d|[A-Z]\.)', next_line) and not re.search(r'TOTAL', next_line, re.IGNORECASE):
        amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', next_line)
        if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
        
    return 0.0

def process_cd_text(text: str):
    lines = text.split('\n')
    
    section_a = section_b = section_c = section_e = 0.0
    lender_credits = loan_amount = cash_to_close = 0.0
    principal_reduction = payoff_amount = 0.0
    homeowners_ins_f = prepaid_interest = 0.0
    homeowners_ins_g = mortgage_ins_g = property_taxes_g = city_property_tax = aggregate_adjustment = 0.0
    
    for i, line in enumerate(lines):
        nl = lines[i+1] if i+1 < len(lines) else ""
        
        if re.search(r'^A\.\s*Origination', line): section_a = get_amount(line, nl)
        elif re.search(r'^B\.\s*Services Borrower Di', line): section_b = get_amount(line, nl)
        elif re.search(r'^C\.\s*Services Borrower Di', line): section_c = get_amount(line, nl)
        elif re.search(r'^E\.\s*Taxes and Other', line): section_e = get_amount(line, nl)
        elif 'Lender Credits' in line and '-' in line and lender_credits == 0: lender_credits = get_amount(line, nl) 
        
        elif 'Cash to Close $' in line and cash_to_close == 0.0: cash_to_close = get_amount(line, nl)
        elif line.startswith('Loan Amount') and loan_amount == 0.0: loan_amount = get_amount(line, nl)
        elif 'Payoff to ' in line: payoff_amount += get_amount(line, nl)
        elif 'Principal Reduction' in line: principal_reduction = get_amount(line, nl)
        
        elif '01 Homeowner\'s Insurance Premium' in line: homeowners_ins_f = get_amount(line, nl)
        elif '03 Prepaid' in line: prepaid_interest = get_amount(line, nl)
        
        elif '01 Homeowner\'s Insurance' in line and 'mo.' in line and homeowners_ins_g == 0: homeowners_ins_g = get_amount(line, nl)
        elif '02 Mortgage Insurance' in line and 'mo.' in line and mortgage_ins_g == 0: mortgage_ins_g = get_amount(line, nl)
        elif '03 Property Taxes' in line and 'mo.' in line and property_taxes_g == 0: property_taxes_g = get_amount(line, nl)
        elif '04 City Property Tax' in line and 'mo.' in line and city_property_tax == 0: city_property_tax = get_amount(line, nl)
        elif '08 Aggregate' in line: aggregate_adjustment = get_amount(line, nl)

    section_d = section_a + section_b + section_c
    total_cost_of_loan = section_d + section_e
    benefits_cost = total_cost_of_loan + lender_credits
    
    excess_amount_over_payoff = payoff_amount + principal_reduction - loan_amount
    prepaid_f = homeowners_ins_f + prepaid_interest
    escrows_g = homeowners_ins_g + mortgage_ins_g + property_taxes_g + city_property_tax + aggregate_adjustment
    escrows_plus_prepaid = escrows_g + prepaid_f
    escrows_prepaid_excess = escrows_plus_prepaid + excess_amount_over_payoff
    benefits_escrow = escrows_prepaid_excess - cash_to_close

    return {
        "part1": {
            "sectionA": section_a, "sectionB": section_b, "sectionC": section_c,
            "sectionD": section_d, "sectionE": section_e,
            "totalCost": total_cost_of_loan, "lenderCredits": lender_credits,
            "benefitsCost": benefits_cost
        },
        "part2": {
            "loanAmount": loan_amount, "payoffAmount": payoff_amount,
            "principalReduction": principal_reduction, "excessAmount": excess_amount_over_payoff,
            "prepaid": {"homeownersIns": homeowners_ins_f, "prepaidInterest": prepaid_interest},
            "escrows": {
                "homeownersIns": homeowners_ins_g, "mortgageIns": mortgage_ins_g,
                "propertyTaxes": property_taxes_g, "cityPropertyTax": city_property_tax,
                "aggregateAdjustment": aggregate_adjustment, "totalG": escrows_g
            },
            "escrowsPlusPrepaid": escrows_plus_prepaid, "escrowsPrepaidExcess": escrows_prepaid_excess,
            "cashToClose": cash_to_close, "benefitsEscrow": benefits_escrow
        }
    }

@app.post("/api/extract-pdf")
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")
    
    try:
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
            
        result = process_cd_text(extracted_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

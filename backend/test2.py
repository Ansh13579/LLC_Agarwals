import re, main, PyPDF2
text=''.join([p.extract_text()+'\n' for p in PyPDF2.PdfReader('sample-closing-disclosure.pdf').pages])
lines = text.split('\n')

def get_amount(line, next_line=""):
    amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', line)
    if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
    
    if next_line and not re.search(r'^\s*(0\d|[A-Z]\.)', next_line) and not re.search(r'TOTAL', next_line, re.IGNORECASE):
        amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', next_line)
        if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
        
    return 0.0

out = {}
for i, line in enumerate(lines):
    nl = lines[i+1] if i+1 < len(lines) else ""
    if re.search(r'^A\.\s*Origination', line): out['A'] = get_amount(line, nl)
    elif re.search(r'^B\.\s*Services Borrower', line): out['B'] = get_amount(line, nl)
    elif re.search(r'^C\.\s*Services Borrower', line): out['C'] = get_amount(line, nl)
    elif re.search(r'^E\.\s*Taxes and Other', line): out['E'] = get_amount(line, nl)
    elif 'Lender Credits' in line and '-' in line: out['LenderCredits'] = get_amount(line, nl) 
    elif '01 Homeowner\'s Insurance Premium' in line: out['F_Ins'] = get_amount(line, nl)
    elif '03 Prepaid' in line: out['F_Prep'] = get_amount(line, nl)
    elif '01 Homeowner\'s Insurance' in line and str(get_amount(line,nl)) != "0.0": out['G_Ins'] = get_amount(line, nl)
    elif '02 Mortgage' in line and str(get_amount(line,nl)) != "0.0": out['G_Mort'] = get_amount(line, nl)
    elif '03 Property Taxes' in line and str(get_amount(line,nl)) != "0.0": out['G_Tax'] = get_amount(line, nl)
    elif '08 Aggregate' in line: out['G_Agg'] = get_amount(line, nl)
    elif 'Principal Reduction' in line: out['PrinRed'] = get_amount(line, nl)
    elif 'TOTAL PAYOFFS' in line: out['Payoffs'] = get_amount(line, nl)
    elif 'Cash to Close $' in line: out['Cash'] = get_amount(line, nl)
    elif line.startswith('Loan Amount'): out['Loan'] = get_amount(line, nl)
print(out)

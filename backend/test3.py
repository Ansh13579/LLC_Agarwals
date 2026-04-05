import re, PyPDF2
text=''.join([p.extract_text()+'\n' for p in PyPDF2.PdfReader('sample-closing-disclosure.pdf').pages])
lines = text.split('\n')
def get_amount(line, next_line=""):
    amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', line)
    if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
    if next_line and not re.search(r'^\s*(0\d|[A-Z]\.)', next_line) and not re.search(r'TOTAL', next_line, re.IGNORECASE):
        amounts = re.findall(r'(-?\s*\$\s*[\d,]+\.\d{2})', next_line)
        if amounts: return float(amounts[-1].replace('$', '').replace(',', '').replace(' ', ''))
    return 0.0
payoff = sum([get_amount(lines[k], lines[k+1] if k+1 < len(lines) else "") for k in range(len(lines)) if 'Payoff to' in lines[k]])
print('Payoff Sum:', payoff)

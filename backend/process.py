import re, main, PyPDF2
text=''.join([p.extract_text()+'\n' for p in PyPDF2.PdfReader('sample-closing-disclosure.pdf').pages])
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'Principal Reduction' in line:
        print(line)
        print(lines[i+1])

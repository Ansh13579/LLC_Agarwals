import React, { useState } from 'react';

const formatMoney = (val, useParentheses = false) => {
  if (val === undefined || val === null) return "$0.00";
  const isNegative = val < 0;
  const formatted = Math.abs(val).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  return isNegative ? (useParentheses ? `(${formatted})` : `-${formatted}`) : formatted;
};

const DataRow = ({ label, value, isBold = false, isIndented = false, isNegative = false, highlightLabel = false, useParentheses = false }) => (
  <div className={`flex justify-between py-3 border-b border-[#1E293B] ${isIndented ? 'pl-6' : ''}`}>
    <span className={`text-sm ${highlightLabel ? 'text-indigo-400 font-semibold' : 'text-gray-300'} ${isBold ? 'font-bold text-white' : ''}`}>
      {label}
    </span>
    <span className={`text-sm font-semibold ${isNegative || value < 0 ? 'text-red-500' : 'text-white'}`}>
      {formatMoney(value, useParentheses)}
    </span>
  </div>
);

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      alert("Please upload a PDF file first.");
      return;
    }
    
    setLoading(true);
    
    // Prepare the file as multipart/form-data
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Send to the new PDF endpoint
      const res = await fetch('https://abd420-llc-backend.hf.space/api/extract-pdf', {
        method: 'POST',
        body: formData, // Browser automatically sets the correct Content-Type for FormData
      });
      
      if (!res.ok) {
        throw new Error("Server error processing PDF");
      }
      
      const json = await res.json();
      setData(json);
    } catch (error) {
      console.error("Failed to fetch data", error);
      alert("Failed to analyze the PDF. Ensure your backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return (
      <div className="min-h-screen bg-[#070B14] flex flex-col items-center justify-center text-white p-6">
        <div className="max-w-md w-full bg-[#111827] border border-gray-800 rounded-2xl p-8 shadow-2xl flex flex-col items-center gap-6">
          <div className="w-16 h-16 bg-indigo-600/20 text-indigo-400 rounded-full flex items-center justify-center mb-2">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
          </div>
          
          <h1 className="text-2xl font-bold text-center">Upload CD Document</h1>
          <p className="text-gray-400 text-sm text-center">Upload your sample Closing Disclosure in PDF format to generate the benefit summary.</p>
          
          <input 
            type="file" 
            accept="application/pdf"
            onChange={handleFileChange}
            className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-900 file:text-indigo-300 hover:file:bg-indigo-800 transition cursor-pointer"
          />
          
          <button 
            onClick={handleAnalyze} 
            disabled={loading || !file}
            className="w-full py-3 bg-indigo-600 disabled:bg-gray-800 disabled:text-gray-500 rounded-lg font-bold hover:bg-indigo-500 transition shadow-lg mt-2"
          >
            {loading ? "Analyzing Document..." : "Generate Dashboard"}
          </button>
        </div>
      </div>
    );
  }

  const { part1, part2 } = data;

  return (
    <div className="min-h-screen bg-[#070B14] text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10 border-b border-gray-800 pb-6 flex items-center justify-between">
           <div className="flex items-center gap-4">
             <div className="w-10 h-10 bg-white rounded flex items-center justify-center text-indigo-900 font-bold text-xl">A</div>
             <div>
               <h1 className="font-bold text-lg tracking-wide">AgarwalsLLC</h1>
               <p className="text-xs text-gray-500 tracking-widest uppercase">Hiring Challenge</p>
             </div>
           </div>
           <button onClick={() => {setData(null); setFile(null);}} className="text-sm text-indigo-400 hover:text-indigo-300 transition">← Upload Another</button>
        </div>

        <h2 className="text-xs text-indigo-400 tracking-widest uppercase font-semibold mb-2">Reference Output</h2>
        <h1 className="text-4xl font-extrabold mb-4 tracking-tight">Sample Benefits Summary</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#111827] rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">
            <div className="p-6 bg-[#0F172A] border-b border-gray-800">
              <h2 className="text-lg font-bold">Part 1 — Savings Depicted by Cost</h2>
            </div>
            
            <div className="p-6">
              <DataRow label="Section A" value={part1.sectionA} />
              <DataRow label="Section B" value={part1.sectionB} />
              <DataRow label="Section C" value={part1.sectionC} />
              <DataRow label="Section D (Sum)" value={part1.sectionD} isBold highlightLabel />
              <DataRow label="Section E" value={part1.sectionE} />
              <DataRow label="Total Cost of Loan" value={part1.totalCost} isBold />
              <DataRow label="Lenders Credit" value={part1.lenderCredits} isNegative />
              
              <div className="mt-4 pt-4 border-t border-gray-700">
                <div className="flex justify-between py-3">
                  <span className="font-bold text-white">Benefits</span>
                  <span className="font-bold text-red-500">{formatMoney(part1.benefitsCost, true)}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#111827] rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">
            <div className="p-6 bg-[#0F172A] border-b border-gray-800">
              <h2 className="text-lg font-bold">Part 2 — Savings Depicted by Escrows & Payoff</h2>
            </div>
            
            <div className="p-6">
              <DataRow label="Loan Amount (Page 1)" value={part2.loanAmount} />
              <DataRow label="Payoff Amount (Page 3, Summed)" value={part2.payoffAmount} />
              <DataRow label="Principal Reduction" value={part2.principalReduction} />
              <DataRow label="Excess Amount over Payoff" value={part2.excessAmount} isBold highlightLabel />
              
              <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mt-6 mb-2">Prepaid (Section F)</h3>
              <DataRow label="Home Owners Insurance" value={part2.prepaid.homeownersIns} isIndented />
              <DataRow label="Prepaid Interest" value={part2.prepaid.prepaidInterest} isIndented />
              <div className="bg-[#111827]">
                <DataRow label="Prepaid (Section F)" value={part2.prepaid.homeownersIns + part2.prepaid.prepaidInterest} isBold highlightLabel />
              </div>
              
              <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mt-6 mb-2">Escrows (Section G)</h3>
              <DataRow label="01 Homeowner's Insurance" value={part2.escrows.homeownersIns} isIndented />
              <DataRow label="02 Mortgage Insurance per month" value={part2.escrows.mortgageIns} isIndented />
              <DataRow label="03 Property Taxes" value={part2.escrows.propertyTaxes} isIndented />
              <DataRow label="04 City Property Tax" value={part2.escrows.cityPropertyTax} isIndented />
              <DataRow label="Aggregate Adjustment" value={part2.escrows.aggregateAdjustment} isIndented isNegative />
              
              <div className="mt-6 border-t border-gray-800">
                <DataRow label="Escrows (Section G)" value={part2.escrows.totalG} isBold highlightLabel />
                <DataRow label="Escrows + Prepaid" value={part2.escrowsPlusPrepaid} isBold highlightLabel />
                <DataRow label="Escrows + Prepaid + Excess Payoff" value={part2.escrowsPrepaidExcess} isBold highlightLabel />
                <DataRow label="Cash to Close (Page 1)" value={part2.cashToClose} isBold />
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-700 bg-[#0A0F1A] -mx-6 -mb-6 px-6 pb-6">
                <div className="flex justify-between py-2">
                  <span className="font-bold text-white text-lg">Benefits</span>
                  <span className="font-bold text-indigo-300 text-lg">{formatMoney(part2.benefitsEscrow, true)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
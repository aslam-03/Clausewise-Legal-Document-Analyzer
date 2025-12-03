import os
import pandas as pd
from processing.extract_text import TextExtractor
from processing.detect_clauses import ClauseDetector
from processing.summarize_and_flag import ClauseAnalyzer

def analyze_contract(file_path: str, output_dir: str = "outputs"):
    """Main analysis pipeline"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Extract text
    print("Extracting text...")
    text = TextExtractor.extract_text(file_path)
    
    # Step 2: Detect clauses
    print("Detecting clauses...")
    detector = ClauseDetector()
    clauses = detector.detect_clauses(text)
    
    # Step 3: Analyze each clause
    print("Analyzing clauses...")
    results = []
    for clause in clauses:
        analysis = ClauseAnalyzer.analyze_clause(clause["text"])
        results.append({
            "Clause Type": analysis["type"],
            "Original Text": clause["text"],
            "Summary": analysis["summary"],
            "Risk Level": analysis["risk_level"],
            "Risk Reasons": "; ".join(analysis["risk_reasons"])
        })
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, "clause_summary_table.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Analysis complete! Results saved to {output_path}")
    return df

if __name__ == "__main__":
    # Example usage
    contract_path = "contracts/sample_nda.pdf"
    analyze_contract(contract_path)
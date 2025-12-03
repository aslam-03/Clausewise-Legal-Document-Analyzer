import sys
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import time
import shutil

# Fix import paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import processing modules
from processing.extract_text import TextExtractor
from processing.detect_clauses import ClauseDetector
from processing.summarize_and_flag import ClauseAnalyzer

def analyze_contract(file_path: str, max_clauses: int = 50) -> pd.DataFrame:
    """Analyze contract document and return DataFrame"""
    try:
        # Step 1: Extract text
        with st.spinner("Extracting text..."):
            text = TextExtractor.extract_text(file_path)
            if not text.strip():
                st.error("Failed to extract text")
                return pd.DataFrame()

        # Step 2: Detect clauses
        with st.spinner("Identifying clauses..."):
            detector = ClauseDetector()
            clauses = detector.detect_clauses(text)[:max_clauses]
            if not clauses:
                st.warning("No clauses detected")
                return pd.DataFrame()

        # Step 3: Analyze clauses
        analyzer = ClauseAnalyzer()
        results = []
        progress_bar = st.progress(0)
        
        for i, clause in enumerate(clauses):
            progress_bar.progress((i + 1) / len(clauses))
            analysis = analyzer.analyze_clause(clause["text"])
            results.append({
                "Clause Type": analysis["type"],
                "Original Text": clause["text"][:500] + "..." if len(clause["text"]) > 500 else clause["text"],
                "Summary": analysis["summary"],
                "Risk Level": analysis["risk_level"],
                "Risk Reasons": "; ".join(analysis["risk_reasons"])
            })
            time.sleep(0.5)
            
        progress_bar.empty()
        return pd.DataFrame(results)
    
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return pd.DataFrame()

def load_saved_analyses():
    """Load all CSV files from outputs directory"""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    return sorted(output_dir.glob("*.csv"), key=os.path.getmtime, reverse=True)

def save_analysis_to_output(df: pd.DataFrame, filename: str) -> Path:
    """Save analysis to outputs directory and return path"""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f"analysis_{filename.split('.')[0]}_{timestamp}.csv"
    df.to_csv(output_path, index=False)
    return output_path

def show_analysis_results(df, title="Analysis Results", key_suffix=""):
    """Display analysis results with filtering"""
    if df is None or df.empty:
        st.warning("No data to display")
        return

    st.success(f"{title} loaded successfully!")
    
    # Summary stats
    st.subheader("📊 Document Summary")
    cols = st.columns(4)
    cols[0].metric("Total Clauses", len(df))
    cols[1].metric("High Risk", len(df[df["Risk Level"] == "high"]))
    cols[2].metric("Medium Risk", len(df[df["Risk Level"] == "medium"]))
    cols[3].metric("Low Risk", len(df[df["Risk Level"] == "low"]))
    
    # Filtering with unique key
    st.subheader("🧾 Clause Analysis")
    risk_filter = st.selectbox(
        "Filter by Risk Level",
        ["All", "High", "Medium", "Low", "None"],
        key=f"risk_filter_{key_suffix}"
    )
    
    filtered_df = df if risk_filter == "All" else df[df["Risk Level"] == risk_filter.lower()]
    
    st.dataframe(
        filtered_df,
        height=600,
        use_container_width=True,
        column_config={
            "Original Text": st.column_config.TextColumn(width="large"),
            "Summary": st.column_config.TextColumn(width="large")
        }
    )
    
    # Download button with unique key
    st.download_button(
        "📥 Download CSV",
        filtered_df.to_csv(index=False).encode('utf-8'),
        f"clause_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        key=f"download_{key_suffix}"
    )

# Streamlit UI
st.set_page_config(page_title="ClauseWise", layout="wide")
st.title("📋 ClauseWise Legal Analyzer")

# Initialize session state
if 'saved_analyses' not in st.session_state:
    st.session_state.saved_analyses = load_saved_analyses()

# Tab interface
tab1, tab2 = st.tabs(["📂 Saved Analyses", "📁 Analyze New Document"])

with tab1:
    st.subheader("Previously Analyzed Documents")
    
    if not st.session_state.saved_analyses:
        st.info("No saved analyses found")
    else:
        selected_file = st.selectbox(
            "Choose analysis file:",
            options=st.session_state.saved_analyses,
            format_func=lambda x: x.name,
            key="saved_file_selector"
        )
        
        if selected_file:
            df = pd.read_csv(selected_file)
            show_analysis_results(df, f"Analysis: {selected_file.name}", key_suffix="saved")
            
        if st.button("🔄 Refresh File List", key="refresh_button"):
            st.session_state.saved_analyses = load_saved_analyses()
            st.rerun()

with tab2:
    st.subheader("Upload Document for Analysis")
    uploaded_file = st.file_uploader("Choose PDF/DOCX", type=["pdf", "docx"], key="file_uploader")
    
    if uploaded_file:
        temp_path = Path("temp_uploads") / uploaded_file.name
        temp_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            df = analyze_contract(temp_path)
            if not df.empty:
                # Save the analysis directly to outputs directory
                output_path = save_analysis_to_output(df, uploaded_file.name)
                
                # Update the saved analyses list
                st.session_state.saved_analyses.insert(0, output_path)
                
                # Show the current analysis
                show_analysis_results(df, "New Analysis Results", key_suffix="new")
                
                # Show success message
                st.success(f"Analysis saved! You can find it in the 'Saved Analyses' tab.")
        finally:
            if temp_path.exists():
                temp_path.unlink()
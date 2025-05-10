# Clausewise-Legal-Document-Analyzer

AI-powered contract analysis for risk-aware decision making

## Project Description

ClauseWise is an intelligent legal document analyzer that automatically:

- Extracts key clauses from contracts/NDAs
- Identifies potential risks and obligations
- Provides plain-English explanations
- Flags unusual terms

## Key Features

- **Multi-Format Support**: Processes PDF, DOCX, and plain text
- **Smart Clause Detection**: Identifies 50+ clause types using NLP
- **Risk Assessment**: Flags high-risk terms with severity scoring
- **Penalty Detection**: Extracts financial obligations automatically
- **Visualization**: Interactive risk dashboard and reports

## Installation and Run Instructions

1. Clone the repository:

  - gh repo clone aslam-03/Clausewise-Legal-Document-Analyzer

2.Navigate to project directory:

  - cd Clausewise Legal Document Analyzer

3.Install dependencies:

  - pip install -r requirements.txt

  - python -m spacy download en_core_web_sm

4.Set up API key:

 - Add your API key in .env file:
      - GEMINI_API_KEY=YOUR_API_KEY

5.Run the application:

Command Line Interface:
  
 - python main.py

Web Interface:
      
 - streamlit run app/viewer.py

## Project Structure
Clausewise Legal Document Analyzer/
├── app/                  # Web interface
│   └── viewer.py         # Streamlit UI
├── processing/           # Core analysis
│   ├── extract_text.py   # Document parsing
│   ├── detect_clauses.py # Clause identification
│   └── analyze_risk.py   # Risk assessment
├── outputs/              # Analysis results
├── contracts/            # Sample documents
├── config.py             # Settings and patterns
└── requirements.txt      # Dependencies

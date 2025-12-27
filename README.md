# 💼 NYAYA SAHAYAK -Contract Analysis & Risk Assessment Bot

This project analyzes legal contracts to identify risks, summarize key clauses, and provide compliance insights with Indian labor and commercial laws.  
It uses **GPT-4-based AI agents** for clause-level analysis, executive summarization, and risk scoring, and provides an interactive **Streamlit dashboard** for visualization and report generation.

---

## 📁 Project Structure

NYAYA_SAHAYAK_CONTRACT_ANALYSIS
```
├── app.py # Streamlit app for contract upload, clause analysis, and visualization
├── preprocessing/
│ ├── file_loader.py # Extracts text from PDF, DOCX, TXT
│ ├── clause_splitter.py # Splits contract into clauses
│ └── cleaning.py # Cleans and normalizes contract text
├── analysis/
│ ├── clause_explainer.py # AI agent to explain clauses and detect risks
│ │── report_generator.py # Formats analysis into JSON and Markdown
│ │── risk_scorer.py # Calculates overall safety score based on weighted clause risks
│ └── summarizer_agent.py # Summarizes contract and calculates risk score
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```


---

## ⚙️ Features

✅ **Clause-Level Analysis**  
- Generates **plain-language explanations** of each clause  
- Identifies **risks and legal ambiguities**  
- Suggests **safer alternatives** to high-risk clauses  

✅ **Executive Summary**  
- Aggregates risks across all clauses  
- Provides **overall safety score** and **final recommendation**  
- Highlights **key obligations and compliance issues**

✅ **Interactive Streamlit Dashboard**  
- Upload contracts in **PDF, DOCX, or TXT** format  
- View **extracted text** and **detected clauses**  
- Expand individual clauses to see explanations, risks, and safer alternatives  
- Export **full report as JSON or Markdown**  

✅ **Dynamic Risk Scoring**  
- Scores individual clauses and entire document  
- Labels **Low / Medium / High** risk  
- Generates actionable recommendations based on risk profile

---

## 🧩 Tech Stack

- **Python**  
- **OpenAI GPT-4 models** – Clause explanations & summarization  
- **Streamlit** – Interactive UI and dashboard  
- **Pandas, NumPy** – Data handling and aggregation  
- **Regex & NLP preprocessing** – Clause splitting and text cleaning  
- **JSON & Markdown** – Report generation

---

## 🚀 How to Run

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/NYAYA_SAHAYAK_CONTRACT_ANALYSIS.git
cd NYAYA_SAHAYAK_CONTRACT_ANALYSIS
2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Launch the Streamlit Dashboard
streamlit run app.py

4️⃣ Upload a Contract
Supported formats: PDF, DOCX, TXT

View clause analysis, risks, and safer alternatives
```


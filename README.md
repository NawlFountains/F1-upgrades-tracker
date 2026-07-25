# F1 Upgrades Tracker

A simple python pipelines that extracts the upgrades components a F1 teams brings into a GP and summarizes it.

---

# Built with
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastF1](https://img.shields.io/badge/FastF1-E10600?style=for-the-badge&logo=formula1&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![pdfplumber](https://img.shields.io/badge/pdfplumber-FF6F61?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-3776AB?style=for-the-badge&logo=python&logoColor=white)
![python-dotenv](https://img.shields.io/badge/dotenv-ECD53F?style=for-the-badge&logo=dotenv&logoColor=black)

---

## Features

1. **Document Ingestion**: Fetches official FIA Car Presentation / Upgrade PDFs for selected Grand Prix race weekends via `requests` and `FastF1` schedule metadata.
2. **Table & Text Extraction**: Parses complex layout elements and technical update tables directly from PDFs using `pdfplumber`.
3. **Data Structuring (`.csv`)**: Cleans raw technical terms, aligns component categories (Floor, Wings, Sidepods, etc.), and exports fully structured datasets as `.csv`.
4. **LLM Insights (`.json`)**: Feeds structured upgrade tables into `Groq` to generate key takeaway summaries, aerodynamic intent analysis, and team-by-team development breakdowns formatted as valid `.json`.

---

## Project Structure

```text
.
├── data/                # GPs updated queried (.csv and summary.json)
├── run_weekend.py       # Main ingestion and execution logic
├── downloader.py        # Data extraction from FIA documents
├── processor.py         # pdfplumber parsing functions
├── summarizer.py        # Groq API integration
├── requirements.txt     # Dependency list
└── README.md
```

---

## Setup

Clone repository
```Bash
git clone https://github.com/your-username/f1-upgrades.git
cd f1-upgrades-tracker
```
Activate the enviroment and install dependencies
```Bash
python -m venv/ .venv/
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Configure your `GROQ_API_KEY` in a .env file:
```  Bash
echo "GROQ_API_KEY='your-api-key-here'" >> .env
``` 
Run the Pipeline
Run the main script for a specific year and round or the current weekend gp (if any):
``` Bash
python run_weekend.py --year 2024 --round 8
```

or

``` Bash
python run_weekend.py
```
---

## ⚠️ Limitations & Disclaimers

> **Note:** This project relies on automated PDF extraction (`pdfplumber`) and LLM processing (`Groq`). While the pipeline works cleanly for most official documents, please keep the following in mind:

* **PDF Layout Variations**: The FIA occasionally alters document formatting, font sizes, or column alignments between Grand Prix weekends. This can sometimes cause multi-line table entries to split prematurely or truncate.
* **LLM Interpretations**: Summaries in `.json` format are AI-generated based on extracted text. Minor phrasing nuances or complex technical aero updates may occasionally be simplified or misrepresented.
* **Data Verification**: Always cross-reference critical upgrade data with official [FIA Documents](https://www.fia.com/documents) before referencing in articles or reports.

---

### 🤝 Contributing Edge Cases
If you spot a race weekend where table parsing cuts short, drops team rows or attributes upgrades to another team (sometimes it happens the parsing isn't perfect):
1. Open an **Issue** with the tag `bug:parsing`.
2. Include the **Race Weekend / Year** and the specific team/component affected.
3. PRs with improved regex rules or coordinate-based table bounding boxes in `pdfplumber` are always welcome!

# Customer Feedback Analysis Dashboard

## Project Structure
```
feedback_dashboard/
├── app.py                     # Main Streamlit dashboard
├── requirements.txt           # Python dependencies
├── generate_sample_csv.py     # Creates a sample CSV for testing
├── data/
│   └── sample_feedback.csv    # Ready-to-use sample dataset
└── README.md
```

## CSV Format Expected
Columns (auto-detected, case-insensitive, also manually re-mappable in the sidebar):
- `date` (or created_at / review_date / timestamp)
- `rating` (1–5, or score/stars)
- `region` (or location/state/city)
- `feedback_text` (or review/comment/feedback/text)

## Steps to Run in VS Code

1. **Open the folder in VS Code**
   - `File > Open Folder` → select `feedback_dashboard`

2. **Create a virtual environment** (open VS Code terminal: `` Ctrl+` ``)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **(One-time) Download TextBlob corpora** — needed for sentiment analysis
   ```bash
   python -m textblob.download_corpora
   ```

6. **(Optional) Generate the sample CSV**
   ```bash
   python generate_sample_csv.py
   ```
   This creates `data/sample_feedback.csv`.

7. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

8. **View in browser**
   - VS Code will show a clickable link, or open manually:
     ```
     http://localhost:8501
     ```

9. **Using the dashboard**
   - Upload your own CSV via the sidebar, **or** check "Use sample demo data."
   - Use sidebar filters: Region, Rating range, Date range, Sentiment.
   - Explore tabs: Rating Distribution, Sentiment Analysis, Monthly Trends, Raw Data.
   - Download filtered results as CSV from the "Raw Data" tab.

## Notes
- If port 8501 is busy: `streamlit run app.py --server.port 8502`
- To stop the server: `Ctrl + C` in the terminal.

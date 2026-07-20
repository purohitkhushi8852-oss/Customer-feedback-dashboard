# Customer Feedback Analysis Dashboard
Live Link :  https://purohitkhushi8852-oss.github.io/Customer-feedback-dashboard/
This project now runs as a static site that can be deployed directly to GitHub Pages.

## Project Structure
```
customer_feedback_dashboard/
├── index.html                # Main page for the dashboard
├── styles.css                # Dashboard styling
├── app.js                    # Client-side dashboard logic
├── data/
│   └── sample_feedback.csv   # Ready-to-use sample dataset
├── .github/workflows/deploy.yml
└── README.md
```

## CSV Format Expected
The dashboard expects a CSV with columns such as:
- `date` (or `created_at`, `review_date`, `timestamp`)
- `rating` (or `score`, `stars`)
- `region` (or `location`, `state`, `city`)
- `feedback_text` (or `review`, `review_text`, `comment`, `feedback`, `text`)

## Deploy to GitHub Pages
1. Push this repository to GitHub.
2. Open the repository settings.
3. Go to Pages.
4. Choose GitHub Actions as the source.
5. The workflow in [.github/workflows/deploy.yml](.github/workflows/deploy.yml) will build and publish the site automatically.

## Run Locally
You can preview the site locally with any static file server:
```bash
python -m http.server 8000
```
Then open http://127.0.0.1:8000/.

## Notes
- The dashboard works entirely in the browser, so no Python backend is required for GitHub Pages.
- Upload your own CSV file from the sidebar to analyze it in the same interface.

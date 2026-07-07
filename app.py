"""
Customer Feedback Analysis Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from datetime import datetime

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Feedback Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS (Clean UI)
# ----------------------------------------------------------------------------
st.markdown("""
    <style>
        .main { background-color: #f8f9fb; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 15px 15px 5px 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        h1, h2, h3 { color: #1f2937; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

@st.cache_data
def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def find_column(df: pd.DataFrame, candidates):
    """Find the first matching column name from a list of possible names."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


@st.cache_data
def generate_sample_data(n=300) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    regions = ["North", "South", "East", "West", "Central"]
    products = ["Product A", "Product B", "Product C", "Product D"]

    positive_texts = [
        "I love this product, it works great!",
        "Excellent service and fast delivery.",
        "Very satisfied with the quality.",
        "Amazing experience, will buy again.",
        "The support team was very helpful and kind.",
    ]
    neutral_texts = [
        "The product is okay, nothing special.",
        "It works as described, average experience.",
        "Delivery was on time, product is fine.",
        "Not bad, could be better.",
    ]
    negative_texts = [
        "Very disappointed with the quality.",
        "The product broke after one use, terrible.",
        "Customer service was rude and unhelpful.",
        "Delivery was late and packaging was damaged.",
        "I regret buying this, waste of money.",
    ]

    all_texts = positive_texts + neutral_texts + negative_texts

    dates = pd.date_range(end=datetime.today(), periods=n, freq="D")
    dates = rng.choice(dates, size=n)

    data = {
        "date": dates,
        "customer_name": [f"Customer_{i}" for i in range(n)],
        "region": rng.choice(regions, size=n),
        "product": rng.choice(products, size=n),
        "rating": rng.integers(1, 6, size=n),
        "feedback_text": rng.choice(all_texts, size=n),
    }
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def get_sentiment(text: str):
    """Return polarity score and label using TextBlob."""
    if not isinstance(text, str) or text.strip() == "":
        return 0.0, "Neutral"
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    return polarity, label


@st.cache_data
def apply_sentiment(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    df = df.copy()
    results = df[text_col].apply(get_sentiment)
    df["polarity"] = results.apply(lambda x: x[0])
    df["sentiment"] = results.apply(lambda x: x[1])
    return df


SENTIMENT_COLORS = {
    "Positive": "#22c55e",
    "Neutral": "#94a3b8",
    "Negative": "#ef4444",
}

# ----------------------------------------------------------------------------
# SIDEBAR - DATA SOURCE
# ----------------------------------------------------------------------------
st.sidebar.title("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Feedback CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample demo data", value=uploaded_file is None)

if uploaded_file is not None:
    raw_df = load_csv(uploaded_file)
    st.sidebar.success(f"Loaded {len(raw_df)} rows from uploaded file.")
elif use_sample:
    raw_df = generate_sample_data()
    st.sidebar.info("Using generated sample data.")
else:
    st.warning("👈 Please upload a CSV file or enable sample data from the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# COLUMN MAPPING
# ----------------------------------------------------------------------------
date_col = find_column(raw_df, ["date", "created_at", "review_date", "timestamp"])
rating_col = find_column(raw_df, ["rating", "score", "stars"])
region_col = find_column(raw_df, ["region", "location", "state", "city"])
text_col = find_column(raw_df, ["feedback_text", "review", "review_text", "comment", "feedback", "text"])

with st.sidebar.expander("⚙️ Column Mapping (auto-detected)", expanded=False):
    date_col = st.selectbox("Date column", options=raw_df.columns,
                             index=list(raw_df.columns).index(date_col) if date_col else 0)
    rating_col = st.selectbox("Rating column", options=raw_df.columns,
                               index=list(raw_df.columns).index(rating_col) if rating_col else 0)
    region_col = st.selectbox("Region column", options=raw_df.columns,
                               index=list(raw_df.columns).index(region_col) if region_col else 0)
    text_col = st.selectbox("Feedback text column", options=raw_df.columns,
                             index=list(raw_df.columns).index(text_col) if text_col else 0)

df = raw_df.copy()
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col])
df["month"] = df[date_col].dt.to_period("M").astype(str)

# Apply sentiment analysis (cached)
df = apply_sentiment(df, text_col)

# ----------------------------------------------------------------------------
# SIDEBAR - FILTERS
# ----------------------------------------------------------------------------
st.sidebar.title("🔎 Filters")

regions = sorted(df[region_col].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

min_rating, max_rating = int(df[rating_col].min()), int(df[rating_col].max())
rating_range = st.sidebar.slider("Rating range", min_rating, max_rating, (min_rating, max_rating))

min_date, max_date = df[date_col].min(), df[date_col].max()
date_range = st.sidebar.date_input("Date range", value=(min_date.date(), max_date.date()))

sentiment_options = ["Positive", "Neutral", "Negative"]
selected_sentiments = st.sidebar.multiselect("Sentiment", options=sentiment_options, default=sentiment_options)

# Apply filters
filtered = df[
    (df[region_col].isin(selected_regions)) &
    (df[rating_col].between(rating_range[0], rating_range[1])) &
    (df["sentiment"].isin(selected_sentiments))
]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered[date_col].dt.date >= start_date) & (filtered[date_col].dt.date <= end_date)
    ]

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("📊 Customer Feedback Analysis Dashboard")
st.caption("Upload feedback data, explore ratings, sentiment, and trends over time.")

if filtered.empty:
    st.warning("No data matches the selected filters. Please adjust filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

avg_rating = filtered[rating_col].mean()
total_feedback = len(filtered)
positive_pct = (filtered["sentiment"] == "Positive").mean() * 100
negative_pct = (filtered["sentiment"] == "Negative").mean() * 100

col1.metric("Total Feedback", f"{total_feedback:,}")
col2.metric("Average Rating", f"{avg_rating:.2f} ⭐")
col3.metric("Positive Sentiment", f"{positive_pct:.1f}%")
col4.metric("Negative Sentiment", f"{negative_pct:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["⭐ Rating Distribution", "💬 Sentiment Analysis", "📈 Monthly Trends", "🗂️ Raw Data"]
)

# --- TAB 1: RATING DISTRIBUTION -----------------------------------------
with tab1:
    c1, c2 = st.columns([2, 1])

    with c1:
        rating_counts = filtered[rating_col].value_counts().sort_index()
        fig = px.bar(
            x=rating_counts.index.astype(str),
            y=rating_counts.values,
            labels={"x": "Rating", "y": "Count"},
            title="Rating Distribution",
            color=rating_counts.index.astype(str),
            color_discrete_sequence=px.colors.sequential.Blues_r,
            text=rating_counts.values,
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(
            names=rating_counts.index.astype(str),
            values=rating_counts.values,
            title="Rating Share",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Average Rating by Region")
    region_rating = filtered.groupby(region_col)[rating_col].mean().sort_values(ascending=False)
    fig3 = px.bar(
        x=region_rating.index, y=region_rating.values,
        labels={"x": "Region", "y": "Average Rating"},
        color=region_rating.values,
        color_continuous_scale="Blues",
        text=np.round(region_rating.values, 2),
    )
    fig3.update_layout(plot_bgcolor="white", coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

# --- TAB 2: SENTIMENT ANALYSIS ------------------------------------------
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        sentiment_counts = filtered["sentiment"].value_counts()
        fig4 = px.pie(
            names=sentiment_counts.index,
            values=sentiment_counts.values,
            title="Overall Sentiment Breakdown",
            color=sentiment_counts.index,
            color_discrete_map=SENTIMENT_COLORS,
            hole=0.4,
        )
        st.plotly_chart(fig4, use_container_width=True)

    with c2:
        fig5 = px.histogram(
            filtered, x="polarity", nbins=30,
            title="Sentiment Polarity Distribution",
            color_discrete_sequence=["#3b82f6"],
        )
        fig5.update_layout(plot_bgcolor="white", xaxis_title="Polarity (-1 to 1)")
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Sentiment by Region")
    sent_region = filtered.groupby([region_col, "sentiment"]).size().reset_index(name="count")
    fig6 = px.bar(
        sent_region, x=region_col, y="count", color="sentiment",
        barmode="group",
        color_discrete_map=SENTIMENT_COLORS,
        title="Sentiment Counts by Region",
    )
    fig6.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Sample Feedback by Sentiment")
    sel_sentiment_view = st.selectbox("Choose sentiment to view examples", sentiment_options)
    examples = filtered[filtered["sentiment"] == sel_sentiment_view][[text_col, rating_col, "polarity"]].head(10)
    st.dataframe(examples, use_container_width=True)

# --- TAB 3: MONTHLY TRENDS ----------------------------------------------
with tab3:
    monthly = filtered.groupby("month").agg(
        avg_rating=(rating_col, "mean"),
        feedback_count=(rating_col, "count"),
        avg_polarity=("polarity", "mean"),
    ).reset_index().sort_values("month")

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["avg_rating"],
        mode="lines+markers", name="Avg Rating", line=dict(color="#3b82f6", width=3)
    ))
    fig7.update_layout(
        title="Average Rating Over Time",
        xaxis_title="Month", yaxis_title="Average Rating",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig7, use_container_width=True)

    fig8 = px.bar(
        monthly, x="month", y="feedback_count",
        title="Feedback Volume Over Time",
        color_discrete_sequence=["#60a5fa"],
    )
    fig8.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig8, use_container_width=True)

    fig9 = go.Figure()
    fig9.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["avg_polarity"],
        mode="lines+markers", name="Avg Sentiment Polarity",
        line=dict(color="#22c55e", width=3), fill="tozeroy",
    ))
    fig9.update_layout(
        title="Average Sentiment Polarity Over Time",
        xaxis_title="Month", yaxis_title="Polarity",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig9, use_container_width=True)

# --- TAB 4: RAW DATA -----------------------------------------------------
with tab4:
    st.subheader("Filtered Dataset")
    st.dataframe(filtered, use_container_width=True)

    csv_download = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data as CSV",
        data=csv_download,
        file_name="filtered_feedback.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("Built with Streamlit, Pandas, NumPy, Plotly, and TextBlob.")

"""Generates sample_feedback.csv for testing the dashboard."""
import pandas as pd
import numpy as np
from datetime import datetime

rng = np.random.default_rng(42)
n = 300
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
df = pd.DataFrame(data).sort_values("date")
df.to_csv("data/sample_feedback.csv", index=False)
print("sample_feedback.csv generated in data/ folder.")

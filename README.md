## Project Overview
This project implements a high-performance "Related Queries" API designed to handle 1 million search logs and provide real-time recommendations. 

---

## 1. Data Preprocessing (SQL)
The preprocessing was performed using **Google BigQuery** to transform raw logs into a refined dataset of query relationships.
* **Stemming:** Applied to the query field to prevent variations (e.g., 'hoodie' and 'hoodies') from diluting the top-K results.
* **Noise Filtering:** Queries shorter than 3 characters (e.g., 'a', 'to') were excluded to focus on meaningful search intent.
* **Jaccard Similarity:** To eliminate popularity bias, I implemented the Jaccard similarity metric instead of simple co-occurrence counts:
  $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
* **Reliability Threshold:** To ensure quality, only pairs that appeared together in **at least 2 sessions** were considered.
* **Symmetry:** Assumed bidirectional relationships (if A relates to B, then B relates to A) to maximize recommendation coverage.

## 2. Data Ingestion & Storage
* **Storage:** Used **Google Cloud Datastore** for its high scalability and low latency.
* **Retrieval Efficiency:** The search query itself serves as the **Datastore Key**, enabling $O(1)$ lookup complexity.

## 3. GAE Application (The API)
Implemented as a **Python Flask** application deployed on **Google App Engine**.
* **Performance Optimizations:**
    * **LRU Caching:** Implemented a cache (size 5000), minimizing Datastore read operations.

---

## Project Structure
- `main.py`: Flask API implementation.
- `app.yaml`: App Engine configuration.
- `ingest_data.py`: Script to populate Datastore from BigQuery.
- `load_test.py` & `test_api.py`: Performance and functional testing suites.
- `bigquery_transformation.sql`: The core data processing logic executed in BigQuery.

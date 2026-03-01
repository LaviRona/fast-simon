# Real-Time Search Suggestions Pipeline
### BigQuery • Datastore • App Engine

## Project Overview
This project implements a high-performance Related Queries API designed to process 1 million search logs and deliver real-time recommendations. The system leverages a GCP-native ETL pipeline to transform raw data into a serving-ready format, optimized for scalability and data integrity.

---

## 1. Data Preprocessing (SQL)
The preprocessing was performed in **Google BigQuery** to handle large-scale data transformation.

### Key Logic Features:
* **Stemming:** Used `REGEXP_REPLACE` to standardize query variations (e.g., 'hoodie' and 'hoodies'), ensuring diverse top-K results.
* **Noise Filtering:** Queries shorter than 3 characters (e.g., 'a', 'to') were excluded using `LENGTH(related_query) > 2`.
* **Jaccard Similarity:** Implemented to prevent popularity bias by calculating the intersection over union:
  $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
* **Reliability Threshold:** Only query pairs appearing together in **at least 2 sessions** (`HAVING COUNT > 1`) were considered to ensure statistical significance.
* **Symmetry:** Bidirectional relationships were assumed to maximize recommendation coverage.

## 2. Data Ingestion & Storage
 The search query itself is used as the **Datastore Key**, enabling $O(1)$ lookup complexity during API requests.

## 3. GAE Application (The API)
The API is a **Python Flask** application deployed on **Google App Engine**.


### Performance Optimizations:
* **LRU Caching:** An in-memory cache (size 5000) was implemented, significantly reducing Datastore read costs and latency.
* **Anti-Cold Start:** Configured `min_idle_instances: 1` in `app.yaml` to maintain steady performance.

## 4. Performance & Load Testing
System efficiency was verified through load tests simulating 10 concurrent users for 200 requests.

![Load Test Results](results.png)

*Results show a clear **warm-up effect**: as the LRU cache populates, average latency drops to **107.84ms** (including Network RTT).*

---

## Project Structure
- `main.py`: Flask API implementation.
- `app.yaml`: App Engine configuration.
- `ingest_data.py`: Script to populate Datastore from BigQuery.
- `load_test.py` & `test_api.py`: Performance and functional testing suites.
- `extract_related_queries.sql`: Core BigQuery data processing logic.

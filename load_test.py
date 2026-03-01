import json
import os
import time
import random
import statistics
import concurrent.futures
import requests
from google.cloud import bigquery

# --- Configuration ---
PROJECT_ID = 'fast-simon-rona'
LOGS_PROJECT = 'rona-455616'
URL = "https://fast-simon-rona.ey.r.appspot.com/related"
CONCURRENT_USERS = 10  # Parallel threads
TOTAL_REQUESTS = 200   # Sample size

def get_query_distribution():
    """Fetches distribution with local caching to save time."""
    cache_file = 'query_dist.json'
    
    if os.path.exists(cache_file):
        print("--- Loading distribution from local cache ---")
        with open(cache_file, 'r') as f:
            data = json.load(f)
            return data['population'], data['weights']

    print("--- Fetching distribution from BigQuery (this may take a moment) ---")
    client = bigquery.Client(project=PROJECT_ID)
    query = f"SELECT query, COUNT(*) as count FROM `{LOGS_PROJECT}.search_logs.raw_logs` GROUP BY query"
    
    population, weights = [], []
    for row in client.query(query):
        population.append(row.query)
        weights.append(row.count)
    
    with open(cache_file, 'w') as f:
        json.dump({'population': population, 'weights': weights}, f)
        
    return population, weights

def send_request(q):
    """Sends a request and returns latency in ms."""
    start = time.time()
    try:
        response = requests.get(f"{URL}?query={q}", timeout=10)
        if response.status_code == 200:
            return (time.time() - start) * 1000
    except Exception:
        return None
    return None

# --- Main Execution Block (The "Start" Switch) ---
if __name__ == "__main__":
    # 1. Get Distribution
    population, weights = get_query_distribution()

    # 2. Weighted Sampling according to distribution
    test_queries = random.choices(population, weights=weights, k=TOTAL_REQUESTS)

    print(f"--- Simulating {CONCURRENT_USERS} users for {TOTAL_REQUESTS} requests ---")
    
    # 3. Parallel Execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        latencies = list(executor.map(send_request, test_queries))

    # 4. Statistical Analysis
    latencies = [l for l in latencies if l is not None]
    
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        print(f"Average Latency: {avg_lat:.2f}ms")
    else:
        print("Error: No successful requests recorded.")
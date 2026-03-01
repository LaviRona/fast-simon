import requests
BASE_URL = "https://fast-simon-rona.ey.r.appspot.com/related"

def test_query(query_name, query_val):
    print(f"--- Testing {query_name}: '{query_val}' ---")
    try:
        # Requesting related queries with a 5-second timeout [cite: 17]
        res = requests.get(f"{BASE_URL}?query={query_val}", timeout=5)
        print(f"Status: {res.status_code}")
        
        results = res.json()
        print(f"Results: {results}")
    except Exception as e:
        print(f"Request failed: {e}")

def run_extended_tests():
    # 1. Popular Item: Hoodies
    test_query("Popular (Hoodies)", "hoodies")

    # 2. Less Popular / Specific Item
    test_query("Less Popular", "cola")

    # 3. Stop Words / Very Short Queries
    # Verifying that SQL filters (e.g., length > 2) prevent returning "garbage" 
    test_query("Short/Stop word", "to")

    # 4. Special Characters / SQL Injection Check
    # Ensuring the system handles special characters gracefully without crashing 
    test_query("Special Characters", "@")

    # 5. Case Sensitivity
    # Confirming that lowercase normalization in GAE/SQL provides consistent results [cite: 20]
    test_query("Case Sensitivity", "HOODIES")

    # 6. Empty Query Handling
    # Validating that an empty parameter returns an empty list rather than an error 
    test_query("Empty Query", "")

if __name__ == "__main__":
    run_extended_tests()
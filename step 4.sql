DECLARE K INT64 DEFAULT 3;

WITH raw_data AS (
  SELECT session, 
         REGEXP_REPLACE(LOWER(query), r'ies$', '') as stemmed_query,
         query as original_query
  FROM `search_logs.raw_logs`
  WHERE query IS NOT NULL AND query != ''
),
--Ignore if a user searches for the same thing more then once in a session
unique_queries AS (
  SELECT DISTINCT session, stemmed_query
  FROM raw_data
),
--Counting for each (stemmed) query in how many sessions it appeared
query_totals AS (
  SELECT stemmed_query, COUNT(DISTINCT session) as total_sessions
  FROM unique_queries
  GROUP BY stemmed_query
),
-- Getting all possible query pairs that appeared together in the same session
query_pairs AS (
  SELECT a.stemmed_query AS query_a, b.stemmed_query AS query_b, a.session
  FROM unique_queries a
  JOIN unique_queries b ON a.session = b.session
  -- Assuming symmetry (if query_a relates to query_b, then query_b relates to query_a)
  WHERE a.stemmed_query < b.stemmed_query -- The pair (a,b) is the same as (b,a)
),
--Using Jaccard Similarity (normalizing by total appearance of each query) to deal with popularity bias
pair_counts AS (
  SELECT 
    p.query_a, 
    p.query_b, 
    COUNT(p.session) / (ta.total_sessions + tb.total_sessions - COUNT(p.session)) as jaccard_score
  FROM query_pairs p
  JOIN query_totals ta ON p.query_a = ta.stemmed_query
  JOIN query_totals tb ON p.query_b = tb.stemmed_query
  GROUP BY p.query_a, p.query_b, ta.total_sessions, tb.total_sessions
  HAVING COUNT(p.session) > 1
),
--The pair (a,b) gets the same score as (b,a).
ranked_results AS (
  SELECT query_a as original_query, query_b as related_query, jaccard_score FROM pair_counts
  UNION ALL
  SELECT query_b, query_a, jaccard_score FROM pair_counts 
),
final_top_k AS (
  SELECT 
    original_query, 
    related_query,
    ROW_NUMBER() OVER(PARTITION BY original_query ORDER BY jaccard_score DESC) as rank
  FROM ranked_results
)

SELECT 
    original_query, 
    ARRAY_AGG(related_query LIMIT 3) as related_list 
FROM (
  SELECT * FROM final_top_k
  WHERE rank <= 5
)
WHERE LENGTH(related_query) > 2 # Filtering out short queries like 'a', 'to'
GROUP BY original_query
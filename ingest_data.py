from google.cloud import bigquery
from google.cloud import datastore

def ingest_to_datastore():
    # 1. Initialize Clients
    bq_client = bigquery.Client(project='fast-simon-rona')
    ds_client = datastore.Client(project='fast-simon-rona')

    # 2. Fetch the preprocessed results from BigQuery
    sql_query = "SELECT original_query, related_list FROM `rona-455616.search_logs.top_3_related_queries`"
    query_job = bq_client.query(sql_query)
    results = query_job.result()

    # 3. Batch Ingestion to Datastore
    batch = ds_client.batch()
    batch.begin()
    
    count = 0
    for row in results:
        # 1. DATA VALIDATION: Skip empty or null keys to avoid the 400 error
        if not row.original_query or row.original_query.strip() == "":
            continue

        # 2. CLEANING: Convert suggestions to a list for manipulation
        suggestions = list(row.related_list)

        # 3. INGESTION: Use the validated query as the Datastore Key
        key = ds_client.key('RelatedQueries', row.original_query)
        entity = datastore.Entity(key=key, exclude_from_indexes=['suggestions'])
        entity.update({
            'suggestions': suggestions
        })
        
        batch.put(entity)
        count += 1

    # Final commit for the remaining entries
    batch.commit()
    print(f"Success! Ingested {count} unique query relationships.")

if __name__ == "__main__":
    ingest_to_datastore()
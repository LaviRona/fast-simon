import os
import re
from flask import Flask, request, jsonify
from google.cloud import datastore
from cachetools import TTLCache, LRUCache

app = Flask(__name__)
ds_client = datastore.Client()
cache = LRUCache(maxsize=5000) #Caching the 5000 least recently used queries
def stem_query(text):
    # Match the SQL logic: REGEXP_REPLACE(LOWER(query), r'ies$', '')
    text = text.strip().lower()
    return re.sub(r'ies$', '', text)


@app.route('/related', methods=['GET'])
def get_related():
    raw_query = request.args.get('query', '')
    query = stem_query(raw_query) 
    
    if not query:
        return jsonify([])

    if query in cache:
        return jsonify(cache[query])

    try:
        # Trying to find it in the premade bigQuery datastructre
        key = ds_client.key('RelatedQueries', query)
        entity = ds_client.get(key)

        if entity and 'suggestions' in entity:
            results = entity['suggestions']
        else:
            results = [] 

        cache[query] = results
        return jsonify(results)

    except Exception as e:
        print(f"Error fetching from Datastore: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)
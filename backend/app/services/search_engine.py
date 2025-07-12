import os
import requests

from app.core.config import SERPER_API_KEY

def search_google(queries, num_results=10):
    a=1
    results={}
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    for query in queries:
        payload = {
            "q": query,
            "num": num_results
        }

        response = requests.post(url, json=payload, headers=headers)
        print("Response:",response.json())
        response.raise_for_status()
        results = response.json()
        if a==1:
            print("example_snippet",results.get("organic", [])[0].get("snippet"))
            a=2
        results[query] = [
            {
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
                "source": item.get("link").split("/")[2]
            }
            for item in results.get("organic", [])
        ]
    return results


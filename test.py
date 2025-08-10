import requests
import time
import json

API_BASE = "http://127.0.0.1:8000"

test_cases = [
    {
        "name": "Wikipedia Films Analysis",
        "description": "Test the films analysis endpoint",
        "data": """Scrape the list of highest grossing films from Wikipedia. It is at the URL:
https://en.wikipedia.org/wiki/List_of_highest-grossing_films

Answer the following questions and respond with a JSON array of strings containing the answer.

1. How many $2 bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between the Rank and Peak?
4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
   Return as a base-64 encoded data URI, "data:image/png;base64,iVBORw0KG..." under 100,000 bytes."""
    },
    {
        "name": "Court Data Analysis",
        "description": "Test the court data analysis",
        "data": """The Indian high court judgement dataset contains judgements from the Indian High Courts, downloaded from ecourts website. It contains judgments of 25 high courts, along with raw metadata (as .json) and structured metadata (as .parquet).

Answer the following questions and respond with a JSON object containing the answer.

{
  "Which high court disposed the most cases from 2019 - 2022?": "...",
  "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": "...",
  "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": "data:image/webp:base64,..."
}"""
    },
    {
        "name": "CSV Analysis",
        "description": "Test CSV upload and analysis",
        "csv_data": """Name,Age,Salary,Department,Experience
John Smith,25,50000,Engineering,2
Jane Doe,30,60000,Marketing,5
Bob Johnson,35,75000,Engineering,8
Alice Brown,28,55000,Sales,3
Charlie Davis,32,70000,Marketing,6
Eva Wilson,27,52000,Engineering,4
Frank Miller,29,58000,Sales,5
Grace Lee,31,65000,Marketing,7""",
        "data": "Analyze the uploaded CSV data and provide statistical insights, correlations, and visualizations."
    }
]

def test_health():
    print("🏥 Testing health endpoint...")
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=10)
        resp.raise_for_status()
        print("✅ Health check passed:", resp.json())
        return True
    except Exception as e:
        print("❌ Health check failed:", e)
        return False

def test_text_request(tc):
    print(f"\n🧪 Testing: {tc['name']}")
    print(f"📝 Description: {tc['description']}")
    start = time.time()
    try:
        resp = requests.post(f"{API_BASE}/api/", data=tc['data'], headers={"Content-Type": "text/plain"}, timeout=180)
        resp.raise_for_status()
        duration = round(time.time() - start, 2)
        print(f"⏱️ Duration: {duration}s")
        print("✅ Response received")
        print("📊 Response data:", json.dumps(resp.json(), indent=2))
        return {"success": True, "duration": duration}
    except Exception as e:
        print(f"❌ Test failed: {tc['name']}")
        print("Error:", e)
        return {"success": False}

def test_csv_upload(tc):
    print(f"\n🧪 Testing: {tc['name']}")
    print(f"📝 Description: {tc['description']}")
    start = time.time()
    try:
        files = {
            "file": ("test.csv", tc["csv_data"], "text/csv"),
            "task": (None, tc["data"])
        }
        resp = requests.post(f"{API_BASE}/api/", files=files, timeout=180)
        resp.raise_for_status()
        duration = round(time.time() - start, 2)
        print(f"⏱️ Duration: {duration}s")
        print("✅ CSV upload test passed")
        print("📊 Response data:", json.dumps(resp.json(), indent=2))
        return {"success": True, "duration": duration}
    except Exception as e:
        print(f"❌ CSV upload test failed: {tc['name']}")
        print("Error:", e)
        return {"success": False}

def run_all_tests():
    print("🚀 Starting API tests...")
    print("=" * 50)
    if not test_health():
        print("❌ Server not ready. Make sure it's running on port 8000")
        return

    results = []
    for tc in test_cases:
        if "csv_data" in tc:
            result = test_csv_upload(tc)
        else:
            result = test_text_request(tc)
        results.append((tc["name"], result))
        time.sleep(2)

    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, r in results if r["success"])
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    for name, r in results:
        status = "✅" if r["success"] else "❌"
        dur = f"({r['duration']}s)" if r.get("duration") else ""
        print(f"{status} {name} {dur}")

if __name__ == "__main__":
    run_all_tests()

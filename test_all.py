#!/usr/bin/env python3
"""
Consolidated test script for Saṃśodhakaḥ API endpoints and pipeline.
"""

import argparse
import requests
import subprocess
import json
import os

def test_api_endpoints():
    """Test all relevant API endpoints."""
    endpoints = [
        ("/api/documents/", "GET", "List documents"),
        ("/api/drafting/section-types", "GET", "List section types"),
    ]

    for endpoint, method, description in endpoints:
        url = f"http://127.0.0.1:8000{endpoint}"
        print(f"\nTesting {description} at {url}:")

        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url)

            if response.status_code == 200:
                print(f"✅ Success: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"❌ Error: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")

def test_drafting_section():
    """Test the drafting section endpoint."""
    url = "http://127.0.0.1:8000/api/drafting/section"
    data = {
        "document_id": "cf8c47b8730d",
        "section_type": "related_work",
        "topic": "Machine Learning in Healthcare"
    }

    print(f"\nTesting drafting section endpoint at {url}:")

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Success: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def test_pipeline():
    """Test the ingestion pipeline."""
    print("\nTesting ingestion pipeline:")

    try:
        # Run ingestion script for sample_paper.md
        subprocess.run(
            ["python", "-m", "backend.ingestion.pipeline", "runtime/data/sample_paper.md"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Ingestion pipeline executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ingestion pipeline error: {e.stderr}")

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="Test Saṃśodhakaḥ API endpoints and pipeline.")
    parser.add_argument("--api", action="store_true", help="Test API endpoints")
    parser.add_argument("--pipeline", action="store_true", help="Test ingestion pipeline")
    parser.add_argument("--all", action="store_true", help="Test both API and pipeline")

    args = parser.parse_args()

    if args.api:
        test_api_endpoints()
    elif args.pipeline:
        test_pipeline()
    elif args.all:
        test_api_endpoints()
        test_drafting_section()
        test_pipeline()
    else:
        print("No test specified. Use --api, --pipeline, or --all.")

if __name__ == "__main__":
    main()
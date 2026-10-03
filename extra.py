import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["jobportal"]
jobs_collection = db["jobs"]

EMPLOYER_ID = ObjectId("6aa798749c1a4a92115f97")

def generate_job_posting():
    print("=== AI Job Agent for Musa Khan ===")
    user_input = input("Which job? Ex: Senior MERN Developer: ")

    prompt = f"""
    User wants: "{user_input}"
    Return ONLY valid JSON:
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, Country",
      "type": "Full-time",
      "salary": 180000,
      "salaryMin": 120000,
      "salaryMax": 250000,
      "description": "250+ words detailed job description"
    }}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", # NEW WORKING MODEL - SEPT 2026
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    job_data = json.loads(response.choices[0].message.content)
    print("\n--- Generated ---")
    print(json.dumps(job_data, indent=2))

    confirm = input("\nSave to MongoDB? (y/n): ")
    if confirm.lower() == 'y':
        job_data["postedBy"] = EMPLOYER_ID
        job_data["salary"] = int(job_data["salary"])
        result = jobs_collection.insert_one(job_data)
        print(f"\nSUCCESS! ID: {result.inserted_id}")

if __name__ == "__main__":
    generate_job_posting()
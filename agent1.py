import os, json, re, random, time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["jobportal"]
jobs_collection = db["jobs"]

# ===== YAHAN APNI NAYI COMPANY KA DATA DALO =====
COMPANY = "ITBS" # Change kar sakte ho: Systems Ltd, 10Pearls, etc
LOCATION = "Islamabad" # Lahore, Karachi, Remote, Peshawar
EMPLOYER_ID = ObjectId("6aacfbaab8a9cbf6b2c7fbb9") # <-- Yahan dusra employer ID
# =================================================

AUTO_JOBS = [
    "Senior Data Scientist",
    "Junior QA Engineer",
    "Content Writer",
    "Product Manager",
    "WordPress Developer",
    "Social Media Manager",
    "Graphic Designer",
    "Cyber Security Analyst",
    "Mobile App Developer",
    "HR Manager"
]

JOB_TYPES = ["Full-time", "Part-time", "Remote", "Contract", "Internship"]

def get_smart_salary(title):
    t = title.lower()
    if "intern" in t: return random.randint(35000, 45000)
    elif "junior" in t: return random.randint(60000, 80000)
    elif "mid" in t: return random.randint(90000, 120000)
    elif "senior" in t: return random.randint(130000, 180000)
    elif "lead" in t or "manager" in t: return random.randint(180000, 250000)
    else: return random.randint(90000, 150000)

def get_smart_job_type(title):
    if "intern" in title.lower():
        return "Internship"
    return random.choice(JOB_TYPES)

def generate_one(title):
    print(f"\n>>> Generating: {title} for {COMPANY} - {LOCATION}")
    prompt = f"Generate job description for {title} at {COMPANY} in {LOCATION}. Return ONLY JSON: {{\"description\": \"250+ words\"}}"
    response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": prompt}], temperature=0.9)
    content = re.sub(r'```json|```', '', response.choices[0].message.content).strip()
    m = re.search(r'\{.*\}', content, re.DOTALL)
    if m: content = m.group(0)
    try: job_data = json.loads(content)
    except: job_data = {"description": f"About the Role: {COMPANY} is looking for {title} in {LOCATION}."}

    final_job = {
        "title": title.title(),
        "company": COMPANY,
        "location": LOCATION,
        "type": get_smart_job_type(title),
        "salary": get_smart_salary(title),
        "description": job_data.get("description", ""),
        "postedBy": EMPLOYER_ID,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    result = jobs_collection.insert_one(final_job)
    print(f"SAVED: {final_job['title']} | {final_job['company']} | {final_job['location']} | {final_job['type']} | Rs. {final_job['salary']}")
    return final_job

def auto_generate():
    print(f"=== AUTO MODE - {COMPANY} ({LOCATION}) - {len(AUTO_JOBS)} jobs ===")
    for job_title in AUTO_JOBS:
        generate_one(job_title)
        time.sleep(2)
    print("\nALL DONE!")

if __name__ == "__main__":
    auto_generate()
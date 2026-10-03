import os, json, re, random, time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import schedule

#.env ka path pakka karo
load_dotenv(dotenv_path=".env")

GROQ_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")

if not GROQ_KEY:
    print("ERROR: GROQ_API_KEY.env me nahi mili!.env check karo")
    exit()
if not MONGO_URI:
    print("ERROR: MONGODB_URI.env me nahi mili!.env check karo")
    exit()

client = OpenAI(api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["jobportal"]
jobs_collection = db["jobs"]

# ===== 3rd AGENT - DAILY 1 JOB =====
COMPANY = "Contour Software"
LOCATION = "Karachi"

# Auto Employer ID - galat ID ka masla khatam
try:
    user = db["users"].find_one({"role": "employer"})
    if user:
        EMPLOYER_ID = user["_id"]
        print(f"Employer Found: {user.get('email')} -> {EMPLOYER_ID}")
    else:
        # fallback - 24 char ka valid ID
        EMPLOYER_ID = ObjectId("68aacfbcc8a9cbf6b2c7fb")
        print(f"No employer found, using fallback ID: {EMPLOYER_ID}")
except Exception as e:
    print(f"Employer find error: {e}, using fallback")
    EMPLOYER_ID = ObjectId("68aacfbcc8a9cbf6b2c7fb")

AUTO_JOBS = [
    "Senior Flutter Developer", "Junior Graphic Designer", "Digital Marketing Specialist",
    "Business Analyst", "Cloud Engineer", "UI/UX Intern", "Full Stack Developer",
    "Content Strategist", "Network Administrator", "Sales Executive",
    "Data Scientist", "DevOps Engineer", "HR Manager", "SEO Specialist", "Video Editor",
    "Backend Developer", "Frontend Developer", "MERN Stack Developer", "Python Developer", "AI Engineer"
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
    if "intern" in title.lower(): return "Internship"
    return random.choice(JOB_TYPES)

def post_one_daily_job():
    title = random.choice(AUTO_JOBS)
    print(f"\n[{datetime.now()}] >>> Daily Job: {title} for {COMPANY}")

    prompt = f"Generate job description for {title} at {COMPANY} in {LOCATION}. Return ONLY JSON: {{\"description\": \"250+ words\"}}"
    try:
        response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": prompt}], temperature=0.9)
        content = re.sub(r'```json|```', '', response.choices[0].message.content).strip()
        m = re.search(r'\{.*\}', content, re.DOTALL)
        if m: content = m.group(0)
        job_data = json.loads(content)
    except Exception as e:
        print(f"Groq API Error: {e}")
        job_data = {"description": f"{COMPANY} is looking for a passionate {title} in {LOCATION}. Great opportunity!"}

    final_job = {
        "title": title.title(), "company": COMPANY, "location": LOCATION,
        "type": get_smart_job_type(title), "salary": get_smart_salary(title),
        "description": job_data.get("description", ""),
        "postedBy": EMPLOYER_ID, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
    }
    jobs_collection.insert_one(final_job)
    print(f"SUCCESS SAVED: {final_job['title']} | {final_job['type']} | Rs. {final_job['salary']}")
    print("Next job will post tomorrow same time.")

# Testing ke liye har 1 minute, baad me daily kar dena
schedule.every(1).minutes.do(post_one_daily_job)
# schedule.every().day.at("09:00").do(post_one_daily_job)

print("Agent3 Started - Daily 1 job at 09:00 AM")
print("Press Ctrl+C to stop")
post_one_daily_job()

while True:
    schedule.run_pending()
    time.sleep(60)
import os, json, re, random
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")
client = OpenAI(api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["jobportal"]
blogs_collection = db["blogs"]
users_collection = db["users"]

print(f"Connected to DB: {db.name} | Collection: blogs")
try:
    user = users_collection.find_one({"role": "admin"}) or users_collection.find_one({})
    AUTHOR_ID = user["_id"] if user else ObjectId()
except:
    AUTHOR_ID = ObjectId("68aacfbcc8a9cbf6b2c7fbb9a")

CATEGORY_IMAGES = {
    "Career Guide": ["https://images.unsplash.com/photo-1499750310107-5fef28a66643?q=80&w=800","https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=800"],
    "Interview Tips": ["https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=800","https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?q=80&w=800"],
    "Tech News": ["https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=800","https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800"],
    "CV & Resume": ["https://images.unsplash.com/photo-1586281380349-632531db7ed4?q=80&w=800","https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=800"],
    "Freelancing": ["https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=800","https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=800"],
    "Job Market": ["https://images.unsplash.com/photo-1553877522-43269d4ea984?q=80&w=800","https://images.unsplash.com/photo-1556761175-5973dc0f32e7?q=80&w=800"]
}
BLOG_TOPICS = ["Top 10 Tips for Job Interview in Pakistan 2026","How to Write a Perfect CV for Freshers in Pakistan","Future of AI Jobs in Pakistan 2026","Remote Work vs Office Work - Which is Better?","How to Get First Job as a MERN Stack Developer","Best Programming Languages to Learn in 2026","How to Negotiate Salary in Pakistan - Complete Guide","LinkedIn Profile Optimization Guide for Job Seekers","Freelancing vs Full-time Job in Pakistan","How to Switch Career to IT in 2026"]
TOPIC_CATEGORY_MAP = {"CV": "CV & Resume","Resume": "CV & Resume","Interview": "Interview Tips","MERN": "Tech News","Programming": "Tech News","AI Jobs": "Tech News","Developer": "Tech News","Salary": "Career Guide","Negotiate": "Career Guide","LinkedIn": "Job Market","Remote": "Freelancing","Freelancing": "Freelancing","Switch Career": "Career Guide"}

def detect_category(topic):
    for k,v in TOPIC_CATEGORY_MAP.items():
        if k.lower() in topic.lower(): return v
    return "Career Guide"

def generate_unique_slug(base_slug):
    slug = re.sub(r'[^a-z0-9]+', '-', base_slug.lower()).strip('-')
    if blogs_collection.find_one({"slug": slug}): slug = f"{slug}-{random.randint(1000,9999)}"
    return slug

def get_smart_image(category, slug):
    images = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["Career Guide"])
    return images[sum(ord(c) for c in slug) % len(images)]

def get_next_topic():
    existing = [b["slug"][:30] for b in blogs_collection.find({}, {"slug":1})]
    for _ in range(20):
        t = random.choice(BLOG_TOPICS)
        base = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:30]
        if not any(base in s for s in existing): return t
    return random.choice(BLOG_TOPICS)

# NEW: Detailed fallback - agar Groq fail bhi ho to 800 words ka content
def generate_detailed_fallback(topic, category):
    return f"""
    <h1>{topic}</h1>
    <p><strong>{topic}</strong> is one of the most important topics for job seekers in Pakistan in 2026. With the job market becoming highly competitive, especially in cities like Karachi, Lahore, and Islamabad, understanding {topic} can give you a significant advantage. In this comprehensive guide on Talent-Hive, we will cover everything you need to know.</p>
    <h2>Why {topic} is Important in Pakistan 2026?</h2>
    <p>In 2026, Pakistan's job market has shifted dramatically. According to recent surveys, over 70% of recruiters in Pakistan now check online presence and professional skills before hiring. Whether you are a fresh graduate from UET, FAST, or Punjab University, or an experienced professional, mastering {topic} is no longer optional. Companies like Systems Limited, Netsol, and Careem are looking for candidates who understand modern career strategies. The competition is high, with thousands applying for a single position on Rozee.pk and LinkedIn.</p>
    <p>Moreover, the rise of remote work and freelancing has changed the dynamics. Pakistani talent is now competing globally on Upwork and Fiverr. To stand out, you need to be well-versed in {topic}. This is where Talent-Hive helps you.</p>
    <h2>Complete Step-by-Step Guide for {topic}</h2>
    <h3>1. Understand the Basics</h3>
    <p>First, start with research. For {topic}, you need to understand what employers actually want. For example, if it's about CV writing, don't just list your education. Focus on achievements. Instead of writing "Worked as intern", write "Developed a MERN stack job portal that increased user engagement by 40%". Use numbers. Pakistani recruiters love measurable results.</p>
    <h3>2. Practical Implementation</h3>
    <p>Second step is implementation. Create a draft. If it's a LinkedIn profile, update your headline, about section, and experience. Use keywords like "Pakistan Jobs 2026", "MERN Stack", "Remote Work". Join relevant groups. For interview preparation, practice common questions like "Tell me about yourself" and "Why should we hire you?" in both English and Urdu, as many Pakistani companies conduct mixed interviews.</p>
    <h3>3. Advanced Strategies</h3>
    <p>Third, go advanced. Network. In Pakistan, reference still matters a lot. Connect with HR managers on LinkedIn. Attend career expos at Expo Center Lahore. For tech jobs, contribute to GitHub. For freelancing, build a strong portfolio on Behance or Dribbble. Remember, consistency is key. Spend at least 1 hour daily on improving your profile related to {topic}.</p>
    <h2>Common Mistakes to Avoid in Pakistan</h2>
    <ul>
        <li><strong>Using Generic CV:</strong> Many freshers in Pakistan send the same CV to every company. This is the biggest mistake. Customize for each job.</li>
        <li><strong>Ignoring Soft Skills:</strong> Companies don't just hire for technical skills. Communication, especially English communication, is critical in 2026.</li>
        <li><strong>Not Following Up:</strong> After applying on Talent-Hive or LinkedIn, always follow up after 3-4 days via email.</li>
    </ul>
    <h2>Pro Tips for Talent-Hive Users</h2>
    <p>At Talent-Hive, we have seen thousands of success stories. The best candidates are those who keep learning. Take free courses from Coursera or DigiSkills. Add certifications to your profile. Keep your Talent-Hive profile 100% complete. Apply early - jobs posted within 24 hours have 8x more chance of getting shortlisted. And always, always be honest.</p>
    <h2>Final Conclusion</h2>
    <p>To conclude, {topic} is your gateway to a successful career in Pakistan in 2026. Whether you aim for a government job, a private job in a multinational, or freelancing, the principles remain the same. Focus on value, be consistent, and use platforms like Talent-Hive to find the right opportunities. Good luck with your job search! Remember, your next job is just one good application away.</p>
    """

def post_one_blog():
    topic = get_next_topic()
    category_forced = detect_category(topic)
    print(f"\n>>> Generating: {topic} | Category: {category_forced}")

    prompt = f"""You are a career blog writer for Pakistan. Topic: "{topic}" Category: {category_forced}. Return ONLY JSON: {{"title": "SEO title 60 chars with Pakistan 2026","slug": "url-slug","excerpt": "150-160 chars summary","content": "HTML with <h1>{topic}</h1> then <p>150 words intro</p> <h2>Why Important</h2><p>200 words</p> <h2>Step by Step</h2><h3>1. Step</h3><p>150 words</p><h3>2. Step</h3><p>150 words</p><h3>3. Step</h3><p>150 words</p><h2>Mistakes</h2><ul><li>Mistake</li></ul><h2>Tips</h2><p>150 words</p><h2>Conclusion</h2><p>100 words</p> - MIN 700 WORDS HTML","tags": ["pakistan jobs","{category_forced.lower()}","2026","career"]}} """

    blog_data = None
    try:
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.7, max_tokens=3500)
        raw = response.choices[0].message.content
        print(f"Raw Groq Len: {{len(raw)}}")
        clean = re.sub(r'```json|```', '', raw).strip()
        m = re.search(r'\{{.*\}}', clean, re.DOTALL)
        if m: clean = m.group(0)
        blog_data = json.loads(clean)
        print(f"Groq SUCCESS: {{blog_data.get('title')}}")
    except Exception as e:
        print(f"Groq Error: {{e}} - Using DETAILED FALLBACK (not short)")
        blog_data = {
            "title": topic,
            "slug": re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-'),
            "excerpt": f"Complete 2026 guide for {topic} in Pakistan. Learn practical tips, mistakes to avoid and pro strategies for Talent-Hive job seekers.",
            "content": generate_detailed_fallback(topic, category_forced),
            "tags": ["pakistan jobs", category_forced.lower(), "2026", "career guide", "talent-hive"]
        }

    final_slug = generate_unique_slug(blog_data.get("slug", topic))
    cover = get_smart_image(category_forced, final_slug)

    final_blog = {
        "title": blog_data.get("title", topic)[:200], "slug": final_slug,
        "excerpt": blog_data.get("excerpt", "")[:300], "content": blog_data.get("content", ""),
        "coverImage": cover, "ogImage": cover, "author": AUTHOR_ID,
        "category": category_forced,
        "tags": [t.lower().strip() for t in blog_data.get("tags", [])],
        "metaTitle": blog_data.get("title", "")[:60], "metaDescription": blog_data.get("excerpt", "")[:160],
        "metaKeywords": [t.lower().strip() for t in blog_data.get("tags", [])],
        "canonicalUrl": f"https://jobportal.com/blog/{final_slug}",
        "status": "published", "views": 0, "likes": [], "isFeatured": False,
        "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
    }
    result = blogs_collection.insert_one(final_blog)
    print(f"✅ SAVED: {final_slug} | Len: {len(final_blog['content'])} | Category: {category_forced}")
    return final_blog

if __name__ == "__main__":
    post_one_blog()
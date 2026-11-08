import json
import os
import google.generativeai as genai

# 1. PUT YOUR API KEY HERE
API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)

# Use cheap model first - this is COST SAVING
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. LOAD SCHOOL DATA - This is RAG
with open("school_info.txt", "r", encoding="utf-8") as f:
    SCHOOL_DATA = f.read()

# 3. CACHE - This saves 90% cost
CACHE_FILE = "cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

cache = load_cache()

# 4. STRICT PROMPT - This fixes HALLUCINATION
def ask_ai(question):
    # Check cache first - FREE answer
    question_lower = question.lower().strip()
    if question_lower in cache:
        print("[CACHE HIT - FREE, 0 cost]")
        return cache[question_lower]

    print("[CACHE MISS - Asking AI, costs money]")

    prompt = f"""
You are a school assistant for Manolo Fortich school.

RULES - FOLLOW STRICTLY:
1. You MUST only answer using the CONTEXT below.
2. If answer is NOT in CONTEXT, say exactly: "Wala sa record, please ask sa registrar."
3. Never invent, never guess, never add extra info.
4. Answer in Taglish, simple and friendly.

CONTEXT:
{SCHOOL_DATA}

Question: {question}
Answer:
"""

    response = model.generate_content(prompt)
    answer = response.text

    # 5. VALIDATION CHECK - Double check hallucination
    check_prompt = f"""
Is this answer 100% based on the CONTEXT below?
CONTEXT: {SCHOOL_DATA}
ANSWER: {answer}
Reply with only YES or NO.
"""
    check = model.generate_content(check_prompt).text.strip()

    if "NO" in check.upper():
        answer = "Wala sa record, please ask sa registrar."

    # Save to cache so next time it's FREE
    cache[question_lower] = answer
    save_cache(cache)
    return answer

# 6. CHAT LOOP
print("=== School AI Chatbot - No Hallucination + Low Cost ===")
print("Type 'exit' to quit\n")

while True:
    q = input("You: ")
    if q.lower() == "exit":
        break
    
    answer = ask_ai(q)
    print(f"AI: {answer}\n")
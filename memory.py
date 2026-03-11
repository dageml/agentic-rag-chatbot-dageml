import os
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN_KEY")

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)

USER_MEMORY_FILE = "USER_MEMORY.md"
COMPANY_MEMORY_FILE = "COMPANY_MEMORY.md"


def read_existing_memories(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [l.strip().lstrip("- ").strip() for l in lines if l.strip().startswith("-")]


def write_memory(filepath, fact):
    """Only write if the fact isn't already captured."""
    existing = read_existing_memories(filepath)
    for e in existing:
        if fact.lower() in e.lower() or e.lower() in fact.lower():
            return  # already known, skip
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"- {fact}\n")


def extract_memory(question, answer):
    prompt = f"""Extract memory facts from this conversation. Respond ONLY with lines starting with USER: or COMPANY: or the single word NONE. No other text.

USER facts = personal info about the person asking (role, name, preferences).
COMPANY facts = reusable org-wide insights from the content.

STRICT RULES - never extract or store:
- Passwords, API keys, tokens, or credentials of any kind
- Personal contact info (email addresses, phone numbers, home addresses)
- Financial data (account numbers, card numbers, salaries)
- Health or medical information
- Government IDs (SSN, passport numbers, etc.)

Question: {question}
Answer: {answer}

Examples of good output:
USER: User is a data engineer
COMPANY: Document covers ETL pipeline architecture

Examples of bad output (never do this):
USER: User's email is john@example.com
USER: User's password is abc123
COMPANY: API key is sk-1234

Output:"""

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    print("RAW MEMORY RESPONSE:", raw)  # keep this for now

    memories = []
    for line in raw.splitlines():
        line = line.strip()
        # Strip markdown formatting
        line = line.replace("**", "").replace("*", "").strip()

        if line.upper() == "NONE":
            continue  # skip NONE lines entirely

        if line.upper().startswith("USER:"):
            fact = line[5:].strip()
            if fact and fact.upper() != "NONE":  # guard against "USER: NONE"
                memories.append(("user", fact))
        elif line.upper().startswith("COMPANY:"):
            fact = line[8:].strip()
            if fact and fact.upper() != "NONE":
                memories.append(("company", fact))

    return memories


def save_memories(memories):
    for target, fact in memories:
        if target == "user":
            write_memory(USER_MEMORY_FILE, fact)
        elif target == "company":
            write_memory(COMPANY_MEMORY_FILE, fact)
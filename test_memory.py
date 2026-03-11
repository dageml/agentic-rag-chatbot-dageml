# test_memory.py
from memory import extract_memory, save_memories

question = "As a data engineer I prefer detailed technical answers, what does this doc say about pipelines?"
answer = "The document describes ETL pipelines used for data ingestion."

memories = extract_memory(question, answer)
print("Extracted memories:", memories)
save_memories(memories)
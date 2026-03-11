import os
from huggingface_hub import InferenceClient
from retrieve import retrieve
from memory import extract_memory, save_memories
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN_KEY")

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)


def generate_answer(question):

    docs, metadatas = retrieve(question)

    context = "\n\n".join(docs)

    prompt = f"""
Answer using ONLY the context below.

Context:
{context}

Question:
{question}

Include citations referencing source and chunk number.
"""

    response = client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
    
    response_text = response.choices[0].message.content


    citations = [
        f"{meta['source']} (chunk {meta['chunk']})"
        for meta in metadatas
    ]

    memories = extract_memory(question, response_text)
    save_memories(memories)

    return response_text, citations

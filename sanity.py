import os
import json

from ingest import ingest_document
from chat import generate_answer

ARTIFACT_PATH = "artifacts/sanity_output.json"


def run_sanity():

    os.makedirs("artifacts", exist_ok=True)

    ingest_document("sample_docs/sample.txt")

    question = "What does this chatbot do?"

    answer, citations = generate_answer(question)

    output = {
        "question": question,
        "answer": answer,
        "citations": citations
    }

    with open(ARTIFACT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print("Sanity check complete.")


if __name__ == "__main__":
    run_sanity()

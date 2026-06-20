import requests
import time

BASE_URL = "http://localhost:8000"

# A mix of questions that SHOULD be answerable from the AWS Customer Agreement,
test_questions = [
    # answerable questions (about the actual document)
    "What is the Effective Date of this agreement?",
    "How often does AWS bill for fees and charges?",
    "What happens if I have a problem charging my default payment method?",
    "What interest rate can AWS charge on late payments?",
    "How much notice does AWS give before increasing fees?",
    "Under what conditions can AWS suspend my account?",
    "What am I responsible for if my account is suspended?",
    "How can I terminate this agreement for convenience?",
    "What notice period does AWS need to give to terminate for convenience?",
    "What happens to my content after the agreement is terminated?",
    "How long do I have to retrieve my content after termination?",
    "Who owns the rights to my content?",
    "What do I represent and warrant about my content?",
    "Can I reverse engineer the AWS services?",
    "What happens if I provide suggestions to AWS?",
    "Will AWS defend me against third-party intellectual property claims?",
    "What is excluded from the indemnification obligations?",
    "Are the services provided with any warranties?",
    "What is the aggregate liability cap under this agreement?",
    "What law governs this agreement if my AWS Contracting Party is Amazon Web Services, Inc.?",
    "How are disputes resolved if the AWS Contracting Party is in Australia?",
    "What must I do before starting an arbitration proceeding against AWS?",
    "Can AWS assign this agreement to someone else?",
    "What is the AWS Confidential Information definition?",
    "How long must I keep AWS Confidential Information confidential after the term ends?",
    "How does AWS provide notices to me?",
    "What is the definition of 'End User' in this agreement?",
    "What happens if part of this agreement is found invalid?",
    "What language must all notices be in?",
    "Where can I find the AWS Acceptable Use Policy?",
    "What is the AWS Contracting Party for customers in India?",
    "What changes were made for customers in Mexico in 2026?",

    # Out-of-scope / irrelevant questions (should trigger "not found")
    "What's the weather like today?",
    "Who won the last football World Cup?",
    "What is the capital of France?",
    "Can you recommend a good recipe for pasta?",
    "What is the meaning of life?",
]


def run_test_queries():
    print(f"Running {len(test_questions)} test queries against {BASE_URL}/ask ...\n")

    for i, question in enumerate(test_questions, start=1):
        try:
            response = requests.post(f"{BASE_URL}/ask", json={"question": question}, timeout=60)
            if response.status_code == 200:
                data = response.json()
                found = "FOUND" if data["answer_found"] else "NOT FOUND"
                print(f"[{i}/{len(test_questions)}] ({found}) {question}")
            else:
                print(f"[{i}/{len(test_questions)}] ERROR {response.status_code}: {question}")
        except requests.exceptions.RequestException as e:
            print(f"[{i}/{len(test_questions)}] Could not reach server: {e}")

        time.sleep(0.2)  # small pause so we don't hammer the local Ollama server

    print("\nDone! Now check GET /analytics to see the usage stats from these queries.")


if __name__ == "__main__":
    run_test_queries()
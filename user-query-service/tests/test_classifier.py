import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sbert_ml_model.intent_classifier import classifier


def test_queries():
    test_cases = [
        "I'm 22 years old, studying computer engineering and I'm seriously concerned about the rapid advancement of AI and its impact on the industry. Would it be wise to switch to electrical engineering or another field of engineering? I'd appreciate any insights!",
        "Python vs Java for most job security.",
        "What is Java?",
        "What features in a project stand out most to recruiters?",
        "Opinions on Golang as a programming language?",
        "What are the top 100 leetcode questions i need to study for a meta interview",
    ]

    for query in test_cases:
        print(f"Query: {query}")
        print(f"Intent: {classifier.classify(query)}")
        print("---")


if __name__ == "__main__":
    test_queries()

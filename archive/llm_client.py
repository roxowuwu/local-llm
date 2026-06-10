import requests

def get_llm_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"].strip()

    except Exception as e:
        print("LLM Error:", e)
        return None

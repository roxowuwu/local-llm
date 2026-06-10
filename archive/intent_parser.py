import json
import re

def parse_intent(output):
    try:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("Parse Error:", e)
    
    return None

import os
from google import genai
import traceback

def test():
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "invalid_key_123")
        client = genai.Client(api_key=api_key)
        print("Client initialized")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="ping"
        )
        print("Response received:", response.text)
    except Exception as e:
        print("Exception caught:")
        print(type(e))
        print(str(e))
        traceback.print_exc()

if __name__ == "__main__":
    test()

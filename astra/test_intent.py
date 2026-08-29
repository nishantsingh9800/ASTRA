from packages.core.intent_parser import IntentParser
from packages.ai.model_router import ModelRouter
from packages.ai.gemini_provider import GeminiProvider

def test():
    llm = GeminiProvider()
    router = ModelRouter(llm)
    parser = IntentParser(router)
    
    intent = parser.parse("Open YouTube and search for Main Hoon Na.", {})
    print("Extracted Intent:")
    print(intent.to_dict())

if __name__ == "__main__":
    test()

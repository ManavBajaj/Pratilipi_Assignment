import os
import json
from dotenv import load_dotenv
from extractor import extract_signals
from adjudicator import decide_subgenre

load_dotenv()

# Choose your free API
API_TYPE = "groq"  # or "together"
API_KEY = os.getenv("GROQ_API_KEY")  # or TOGETHER_API_KEY

if not API_KEY:
    raise RuntimeError(f"{API_TYPE.upper()}_API_KEY not set in .env file")

def load_test_cases():
    """Load the golden test set"""
    with open("test_cases.json") as f:
        return json.load(f)

def run_mapper():
    """Run all test cases and output results"""
    test_cases = load_test_cases()
    results = []
    
    print("=" * 80)
    print(f"ADAPTIVE TAXONOMY MAPPER - Using {API_TYPE.upper()} API")
    print("=" * 80)
    
    for case in test_cases:
        case_id = case["id"]
        tags = case["tags"]
        story = case["story"]
        
        print(f"\n{'='*80}")
        print(f"CASE {case_id}")
        print(f"{'='*80}")
        print(f"Tags: {tags}")
        print(f"Story: {story}")
        
        # Extract signals
        signals = extract_signals(API_KEY, story, tags, api_type=API_TYPE)
        print(f"\n📊 Extracted Signals:")
        for k, v in signals.items():
            print(f"   {k}: {v}")
        
        # Decide subgenre
        decision = decide_subgenre(signals, story, tags)
        
        print(f"\n✅ Decision: {decision['subgenre']}")
        if decision['parent']:
            print(f"   Category Path: {decision['parent']}")
        print(f"   Reasoning: {decision['reasoning']}")
        
        results.append({
            "id": case_id,
            "tags": tags,
            "story": story,
            "signals": signals,
            "decision": decision
        })
    
    # Save results
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("✅ Results saved to results.json")
    print(f"{'='*80}")

if __name__ == "__main__":
    run_mapper()
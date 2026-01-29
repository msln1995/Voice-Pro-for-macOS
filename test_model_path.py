
import os
import json
from cached_path import cached_path

def test_model_loading():
    print("Testing model loading...")
    config_path = "app/abus_tts_f5_models.json"
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    model_name = "SWivid/F5-TTS_v1"
    if model_name not in config:
        print(f"Model {model_name} not found in config")
        return

    paths = config[model_name]
    print(f"Paths for {model_name}: {paths}")
    
    try:
        vocab_path = paths['vocab_path']
        print(f"Configured vocab path: {vocab_path}")
        
        # Test cached_path resolution
        resolved_vocab = str(cached_path(vocab_path))
        print(f"Resolved vocab path: {resolved_vocab}")
        
        if os.path.exists(resolved_vocab):
            print("Vocab file exists!")
        else:
            print("Vocab file NOT found!")
            
        model_path = paths['model_path']
        print(f"Configured model path: {model_path}")
        resolved_model = str(cached_path(model_path))
        print(f"Resolved model path: {resolved_model}")
        
        if os.path.exists(resolved_model):
            print("Model file exists!")
        else:
            print("Model file NOT found!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model_loading()

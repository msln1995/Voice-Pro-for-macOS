
import os
from cached_path import cached_path

def test_download_behavior():
    # Use a small file from HF
    url = "hf://SWivid/F5-TTS/README.md"
    print(f"Testing download of: {url}")
    
    try:
        # Check where it goes by default
        path = cached_path(url)
        print(f"Downloaded to: {path}")
        
        if "/.cache/" in path:
            print("RESULT: Default behavior uses system cache.")
        else:
            print("RESULT: Default behavior uses unknown location.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_download_behavior()

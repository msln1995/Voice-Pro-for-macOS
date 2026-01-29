
import os
import shutil
from cached_path import cached_path
import logging

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockManager:
    def get_model_paths(self, model_name):
        # Return dummy config with URL
        return {
            "model_path": "hf://SWivid/F5-TTS/README.md",
            "vocab_path": "hf://SWivid/F5-TTS/vocab.txt",
            "config": {}
        }

def test_resolve_logic():
    print("Testing resolve logic...")
    
    # Create a mock ckpts directory
    os.makedirs("ckpts/Mock_Model", exist_ok=True)
    
    # Create a dummy local file
    with open("ckpts/Mock_Model/README.md", "w") as f:
        f.write("Local copy")
        
    # Copy resolve_path logic here for testing (since it's an inner function in the class)
    # We'll simulate it
    model_name = "Mock/Model"
    
    def resolve_path(path_or_url):
        if not path_or_url: return ""
        if not path_or_url.startswith("hf://"): return path_or_url
        
        safe_model_name = model_name.replace("/", "_")
        ckpt_dir = os.path.join(os.getcwd(), "ckpts", safe_model_name)
        filename = path_or_url.split("/")[-1]
        local_file_path = os.path.join(ckpt_dir, filename)
        
        if os.path.exists(local_file_path):
            print(f"Found local: {local_file_path}")
            return local_file_path
        
        print(f"Not found locally, falling back to cached_path: {path_or_url}")
        return "system_cache_path"

    # Test 1: Local file exists
    res = resolve_path("hf://Mock/Model/README.md")
    if "ckpts/Mock_Model/README.md" in res:
        print("Test 1 PASS: Found local file")
    else:
        print("Test 1 FAIL: Did not find local file")

    # Test 2: Local file missing
    res = resolve_path("hf://Mock/Model/missing.txt")
    if res == "system_cache_path":
        print("Test 2 PASS: Fallback to system cache")
    else:
        print("Test 2 FAIL: Incorrect fallback")

if __name__ == "__main__":
    test_resolve_logic()

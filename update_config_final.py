
import os
import json

def get_model_safe_name(model_name):
    return model_name.replace("/", "_")

def main():
    config_path = "app/abus_tts_f5_models.json"
    ckpt_base_dir = "ckpts"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    new_config = config.copy()
    
    updated_count = 0
    
    print("Updating configuration with verified local files...")
    
    for model_name, paths in config.items():
        # Special case for F5-TTS_v1 which was manually moved to ckpts/F5-TTS
        if model_name == "SWivid/F5-TTS_v1":
            # Already updated or verify it
            if paths['model_path'] == "ckpts/F5-TTS/model_1250000.safetensors":
                print(f"  [OK] {model_name} is already configured locally.")
                continue

        safe_name = get_model_safe_name(model_name)
        target_dir = os.path.join(ckpt_base_dir, safe_name)
        
        # Check model file
        current_model_path = paths['model_path']
        model_filename = current_model_path.split("/")[-1]
        local_model_path = os.path.join(target_dir, model_filename)
        
        # Check vocab file
        current_vocab_path = paths['vocab_path']
        vocab_filename = current_vocab_path.split("/")[-1]
        local_vocab_path = os.path.join(target_dir, vocab_filename)
        
        if os.path.exists(local_model_path) and os.path.exists(local_vocab_path):
            new_config[model_name]['model_path'] = local_model_path
            new_config[model_name]['vocab_path'] = local_vocab_path
            print(f"  [UPDATED] {model_name} -> {target_dir}")
            updated_count += 1
        else:
            print(f"  [SKIPPED] {model_name} (Local files not found: {local_model_path})")

    # Write back to file
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, indent=4, ensure_ascii=False)
        
    print(f"\nConfiguration update complete. {updated_count} models updated to local paths.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Preload sentence transformer models for offline use.
Run this when you have internet access to cache models locally.
"""

import os
import sys
from pathlib import Path

def preload_models():
    """Download and cache sentence transformer models"""
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        print("🤖 Preloading AI models for offline use...")
        
        # Create models directory
        models_dir = Path(".venv/models")
        models_dir.mkdir(exist_ok=True)
        
        # Lightweight models that work well for code similarity
        models_to_cache = [
            "all-MiniLM-L6-v2",  # Fast, good general purpose
            "all-mpnet-base-v2", # Better quality, slightly larger
        ]
        
        for model_name in models_to_cache:
            print(f"📦 Downloading {model_name}...")
            try:
                # Load model (this caches it automatically)
                model = SentenceTransformer(model_name)
                
                # Test encoding to ensure it works
                test_text = ["This is a test sentence.", "This is another test."]
                embeddings = model.encode(test_text)
                
                print(f"✅ {model_name} cached successfully ({embeddings.shape})")
                
            except Exception as e:
                print(f"❌ Failed to cache {model_name}: {e}")
        
        print("\n🎉 Model preloading complete!")
        print("💡 Models are cached in ~/.cache/torch/sentence_transformers/")
        print("💡 The application will work offline now for sentence embeddings.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Required packages not installed: {e}")
        print("📦 Run: .venv/Scripts/python.exe -m pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Error preloading models: {e}")
        return False

def check_cache():
    """Check what models are already cached"""
    try:
        import torch
        from sentence_transformers import SentenceTransformer
        
        cache_dir = Path.home() / ".cache" / "torch" / "sentence_transformers"
        if cache_dir.exists():
            cached_models = [d.name for d in cache_dir.iterdir() if d.is_dir()]
            if cached_models:
                print("📋 Cached models found:")
                for model in cached_models:
                    print(f"  ✅ {model}")
            else:
                print("📋 No cached models found")
        else:
            print("📋 No cache directory found")
            
    except Exception as e:
        print(f"❌ Error checking cache: {e}")

if __name__ == "__main__":
    print("🔍 Checking current model cache...")
    check_cache()
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        print("🏁 Check complete.")
    else:
        success = preload_models()
        if success:
            print("\n🔍 Final cache status:")
            check_cache()
        else:
            print("\n❌ Preloading failed. Models will be downloaded when first used.")
            sys.exit(1) 
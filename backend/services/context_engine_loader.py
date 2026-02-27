"""
Load Jen Context Engine documentation for intelligent query processing.
"""

from pathlib import Path


def load_context_engine() -> str:
    """
    Load complete Agent Trust Hub and Jen context from backend/services/jen/ directory.
    
    Loads the most impactful docs for GenClaw intelligence:
    1. jen-soul-document-complete.md (52KB) - Core identity + Agent Trust Hub knowledge
    2. jen-complete-persona-voice-document.md (110KB) - Voice and persona rules  
    3. jen-enhanced-scoring-framework-complete.md (97KB) - Post scoring criteria
    
    Total: ~260KB of context for context-aware discovery.
    """
    
    # Get path to jen/ directory relative to this file
    # This file is at: backend/services/context_engine_loader.py
    # Jen docs are at: backend/services/jen/*.md
    jen_dir = Path(__file__).resolve().parent / "jen"
    
    # Priority context files (most impactful first)
    context_files = [
        "jen-soul-document-complete.md",  # Core identity, Agent Trust Hub products, stats
        "jen-complete-persona-voice-document.md",  # Voice guidelines, personas
        "jen-enhanced-scoring-framework-complete.md",  # Scoring criteria
    ]
    
    full_context = []
    total_size = 0
    
    for filename in context_files:
        filepath = jen_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_size = len(content)
                    total_size += file_size
                    full_context.append(f"# {filename}\n{content}")
                    print(f"✅ Loaded {filename}: {file_size:,} chars")
            except Exception as e:
                print(f"⚠️  Failed to load {filename}: {e}")
        else:
            print(f"❌ Not found: {filepath}")
    
    combined_context = "\n\n".join(full_context)
    print(f"📊 Total Jen context loaded: {total_size:,} chars ({len(full_context)} files)")
    
    return combined_context


# Load once at module import
AGENT_TRUST_HUB_CONTEXT = load_context_engine()

"""
Load Jen Context Engine documentation for intelligent query processing.
"""

import os


def load_context_engine() -> str:
    """Load complete Agent Trust Hub context from memory files."""
    
    memory_dir = "/home/ubuntu/.openclaw/workspace/memory"
    
    context_files = [
        "context-engine-layer1-agent-trust-hub.md",
        "context-engine-layer2-comprehensive.md",
        "context-engine-layer3-comprehensive.md",
    ]
    
    full_context = []
    
    for filename in context_files:
        filepath = os.path.join(memory_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                full_context.append(f"# {filename}\n{content}")
    
    return "\n\n".join(full_context)


# Load once at module import
AGENT_TRUST_HUB_CONTEXT = load_context_engine()

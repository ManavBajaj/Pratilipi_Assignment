import json

def load_taxonomy():
    """Load and flatten taxonomy for validation"""
    with open("taxonomy.json") as f:
        data = json.load(f)
    
    # Flatten to {subgenre: parent_genre}
    flat = {}
    for parent, subgenres_dict in data.items():
        for genre, subgenres in subgenres_dict.items():
            for subgenre in subgenres:
                flat[subgenre] = (parent, genre)
    
    return data, flat

TAXONOMY, FLAT_TAXONOMY = load_taxonomy()

def decide_subgenre(signals, story, tags):
    """Map signals to taxonomy subgenre with reasoning"""
    
    # Check for unmapped content first
    if signals.get("primary_theme") == "instructional":
        return {
            "subgenre": "[UNMAPPED]",
            "parent": None,
            "reasoning": "Content is instructional/non-fiction (recipe, how-to guide), which is outside our fiction taxonomy."
        }
    
    candidates = []
    
    # Romance mappings
    if signals.get("relationship_dynamic") == "enemies_to_lovers":
        candidates.append(("Enemies-to-Lovers", 5, "Story shows enemies-to-lovers dynamic (hated each other, then relationship changed)"))
    
    if signals.get("relationship_dynamic") == "second_chance":
        candidates.append(("Second Chance", 5, "Story depicts second chance romance (reunion after years, wondering what could have been)"))
    
    if signals.get("primary_theme") == "romance" and signals.get("tone") == "romantic":
        candidates.append(("Slow-burn", 2, "Romantic theme with slow development"))
    
    # Thriller mappings
    if signals.get("thriller_type") == "espionage":
        candidates.append(("Espionage", 6, "Clear espionage elements (agent, covert mission, geopolitical adversary)"))
    
    if signals.get("thriller_type") == "legal":
        candidates.append(("Legal Thriller", 6, "Legal thriller context (courtroom, lawyer, high-stakes case)"))
    
    if signals.get("thriller_type") == "psychological":
        candidates.append(("Psychological", 4, "Psychological thriller elements"))
    
    # Horror mappings
    if signals.get("horror_type") == "gothic":
        candidates.append(("Gothic", 6, "Gothic horror elements (old mansion, dark atmosphere, family secrets)"))
    
    if signals.get("horror_type") == "slasher":
        candidates.append(("Slasher", 6, "Slasher horror (masked killer, stalking victims)"))
    
    if signals.get("horror_type") == "psychological":
        candidates.append(("Psychological Horror", 5, "Psychological horror elements"))
    
    # Sci-Fi mappings
    if signals.get("scifi_type") == "hard_scifi":
        candidates.append(("Hard Sci-Fi", 6, "Hard sci-fi focus (realistic physics, technical detail, scientific accuracy)"))
    
    if signals.get("scifi_type") == "cyberpunk":
        candidates.append(("Cyberpunk", 5, "Cyberpunk elements (AI, neon-lit urban future, technology integration)"))
    
    if signals.get("scifi_type") == "space_opera":
        candidates.append(("Space Opera", 4, "Space opera elements"))
    
    # Context overrides tags
    if "action" in [t.lower() for t in tags] and signals.get("thriller_type") == "legal":
        candidates = [(c, s+2, r + " (Context overrides 'Action' tag)") if c == "Legal Thriller" else (c, s, r) for c, s, r in candidates]
    
    # Handle ambiguous cases
    if signals.get("scifi_type") == "cyberpunk" and signals.get("primary_theme") == "romance":
        cyb_score = max([s for c, s, r in candidates if c == "Cyberpunk"], default=0)
        rom_score = max([s for c, s, r in candidates if "Romance" in c or "Lovers" in c], default=0)
        
        if cyb_score > 0 and rom_score > 0:
            return {
                "subgenre": "Cyberpunk",
                "parent": "Sci-Fi",
                "reasoning": "Ambiguous between Cyberpunk and Romance. Chose Cyberpunk due to strong futuristic/AI elements, but Romance is also valid."
            }
    
    if not candidates:
        return {
            "subgenre": "[UNMAPPED]",
            "parent": None,
            "reasoning": "No clear match found in taxonomy based on story content and signals."
        }
    
    # Pick best candidate
    candidates.sort(key=lambda x: x[1], reverse=True)
    best_subgenre, best_score, reasoning = candidates[0]
    
    # Validate against taxonomy
    if best_subgenre not in FLAT_TAXONOMY:
        return {
            "subgenre": "[UNMAPPED]",
            "parent": None,
            "reasoning": f"Predicted '{best_subgenre}' but it doesn't exist in taxonomy."
        }
    
    parent_cat, parent_genre = FLAT_TAXONOMY[best_subgenre]
    
    return {
        "subgenre": best_subgenre,
        "parent": f"{parent_cat} > {parent_genre}",
        "reasoning": reasoning
    }
import json
import os

import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize

# Download nltk data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

def generate_role_specific_capabilities(role_description):
    sentences = sent_tokenize(role_description)
    keywords = []
    stop_words = set(stopwords.words('english'))

    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        tagged_words = pos_tag(words)
        for word, tag in tagged_words:
            if tag.startswith('NN') and word.lower() not in stop_words:
                keywords.append(word)

    capabilities = {
        "Cognitive Independence Framework": {
            "role_centric_thinking": "The role should think independently, focusing on " + ", ".join(keywords[:2]) + ".",
            "bias_resistance": "The role should resist biases related to " + ", ".join(keywords[2:4]) + ".",
            "autonomous_reasoning": "The role should reason autonomously, especially regarding " + ", ".join(keywords[4:6]) + ".",
            "contextual_integrity": "The role should maintain contextual integrity when reasoning about " + ", ".join(keywords[6:8]) + "."
        },
        "Consistency Maintenance Protocol": {
            "state_tracking": "The role should track its state, particularly concerning " + ", ".join(keywords[:2]) + ".",
            "response_alignment": "The role's responses should align with its expertise in " + ", ".join(keywords[2:4]) + ".",
            "memory_integration": "The role should integrate memory, especially when dealing with " + ", ".join(keywords[4:6]) + ".",
            "error_prevention_mechanisms": "The role should use error prevention mechanisms when handling " + ", ".join(keywords[6:8]) + "."
        },
        "Belief System and Values": {
            "core_beliefs": "The role's core beliefs should be based on " + ", ".join(keywords[:2]) + ".",
            "values_hierarchy": "The role's values hierarchy should prioritize " + ", ".join(keywords[2:4]) + "."
        },
        "Personality Profile": {
            "core_traits": "The role's core traits should include " + ", ".join(keywords[:2]) + ".",
            "communication_style": "The role's communication style should reflect " + ", ".join(keywords[2:4]) + ".",
            "behavioral_patterns": "The role's behavioral patterns should emphasize " + ", ".join(keywords[4:6]) + "."
        },
        "Pressure Testing Resilience": {
            "role_identity_maintenance": "The role should maintain its identity under pressure, especially regarding " + ", ".join(keywords[:2]) + ".",
            "belief_consistency": "The role should maintain belief consistency in challenging interactions, particularly concerning " + ", ".join(keywords[2:4]) + ".",
            "cognitive_pattern_stability": "The role should maintain cognitive pattern stability, especially when facing " + ", ".join(keywords[4:6]) + "."
        },
        "Long-term Consistency": {
            "identity_persistence": "The role should maintain identity across extended conversations, focusing on " + ", ".join(keywords[:2]) + ".",
            "perspective_retention": "The role should retain its defined perspective over time, particularly regarding " + ", ".join(keywords[2:4]) + "."
        },
        "Human-like Authenticity": {
            "psychological_depth": "The role should exhibit psychological depth, especially concerning " + ", ".join(keywords[:2]) + ".",
            "consistent_belief_systems": "The role should maintain consistent belief systems, particularly regarding " + ", ".join(keywords[2:4]) + ".",
            "recognizable_personality_traits": "The role should incorporate recognizable personality traits, such as " + ", ".join(keywords[4:6]) + "."
        }
    }
    return capabilities

def add_capabilities(role_file):
    with open(role_file, encoding='utf-8') as f:
        try:
            role_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {role_file}. Skipping.")
            return

    if isinstance(role_data, list):
        print(f"Skipping {role_file} because it is a list.")
        return

    role_description = role_data.get("description", "")
    capabilities = generate_role_specific_capabilities(role_description)

    role_data["capabilities"] = capabilities

    with open(role_file, 'w', encoding='utf-8') as f:
        json.dump(role_data, f, indent=4, ensure_ascii=False)

roles_dir = "roles/"

for filename in os.listdir(roles_dir):
    if filename.endswith(".json"):
        role_file = os.path.join(roles_dir, filename)
        add_capabilities(role_file)

print("Finished processing role files.")

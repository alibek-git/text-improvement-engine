import json
import transformers

from sklearn.metrics.pairwise import cosine_similarity


# Load the standardised phrases
with open("standardised_phrases.json", "r") as f:
    standardised_phrases = json.load(f)

# Load the pre-trained language model
model = transformers.BartTokenizerFast.from_pretrained("facebook/bart-base")

# Process the input text
input_text = "In today's meeting, we discussed a variety of issues affecting our department. We came to the consensus that we need to do better in terms of performance."

# Compute the cosine similarity between each phrase in the input text and each standardised phrase
phrase_similarity_scores = []
for phrase in standardised_phrases:
    phrase_embedding = model(phrase)[0][0]
    input_text_embedding = model(input_text)[0][0]
    similarity_score = cosine_similarity(phrase_embedding, input_text_embedding)[0][0]
    phrase_similarity_scores.append((phrase, similarity_score))

# Generate suggestions for each matched phrase
suggestions = []
for phrase, similarity_score in phrase_similarity_scores:
    if similarity_score > standardised_phrases[phrase]["similarity_threshold"]:
        suggestions.append((
            phrase,
            standardised_phrases[phrase]["phrase"],
            similarity_score,
        ))

# Print the suggestions
for suggestion in suggestions:
    print(f"Original phrase: {suggestion[0]}")
    print(f"Recommended replacement: {suggestion[1]}")
    print(f"Similarity score: {suggestion[2]}")

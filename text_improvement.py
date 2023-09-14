import json
import transformers
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load the standardized phrases from a JSON file
try:
    with open("standardized_phrases.json", "r") as f:
        standardized_phrases_data = json.load(f)
except FileNotFoundError:
    print("Error: The 'standardized_phrases.json' file is missing.")
    standardized_phrases_data = []

# Create a dictionary from standardized phrases data
standardized_phrases = {}
for phrase_data in standardized_phrases_data:
    phrase = phrase_data["phrase"]
    threshold = phrase_data["similarity_threshold"]
    standardized_phrases[phrase] = {"phrase": phrase, "similarity_threshold": threshold}

# Load the pre-trained language model and tokenizer
model_name = "facebook/bart-base"
model = transformers.BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = transformers.BartTokenizer.from_pretrained(model_name)

# Function to calculate similarity score
def calculate_similarity(phrase, input_text):
    # Tokenize both the phrase and input_text
    phrase_tokens = tokenizer.tokenize(phrase)
    input_tokens = tokenizer.tokenize(input_text)
    
    # Convert tokens to IDs
    phrase_ids = tokenizer.convert_tokens_to_ids(phrase_tokens)
    input_ids = tokenizer.convert_tokens_to_ids(input_tokens)

    # Convert IDs to tensors
    phrase_tensor = torch.tensor(phrase_ids).unsqueeze(0)
    input_tensor = torch.tensor(input_ids).unsqueeze(0)

    # Pad the shorter tensor to match the length of the longer tensor
    max_length = max(phrase_tensor.shape[1], input_tensor.shape[1])
    phrase_tensor = torch.nn.functional.pad(phrase_tensor, (0, max_length - phrase_tensor.shape[1]))
    input_tensor = torch.nn.functional.pad(input_tensor, (0, max_length - input_tensor.shape[1]))

    # Calculate similarity using cosine similarity
    similarity_score = cosine_similarity(phrase_tensor, input_tensor).item()
    return similarity_score
    
# Function to generate suggestions
def generate_suggestions(input_text):
    suggestions = []
    for phrase in standardized_phrases:
        similarity_score = calculate_similarity(phrase, input_text)
        if similarity_score > standardized_phrases[phrase]["similarity_threshold"]:
            suggestions.append((phrase, standardized_phrases[phrase]["phrase"], similarity_score))
    return suggestions

# Main loop for user interaction
while True:
    input_text = input("Enter the text you want to analyze (or 'exit' to quit): ")
    if input_text.lower() == "exit":
        break
   
    # Check if the input text contains recognizable content
    relevant_content_keywords = ["performance", "efficiency", "growth", "innovation", "change", "leadership"]
    relevant_content = any(keyword in input_text.lower() for keyword in relevant_content_keywords)
    
    if not relevant_content:
        print("No relevant content found in the input text.")
        continue
    
    suggestions = generate_suggestions(input_text)
    
    if not suggestions:
        print("No suggestions found.")
    else:
        print("Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. Original phrase: {suggestion[0]}")
            print(f"   Recommended replacement: {suggestion[1]}")
            print(f"   Similarity score: {suggestion[2]}")

# End of the program
print("Goodbye!")

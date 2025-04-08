import random
import json
import torch
import nltk
import os

# Ensure to add the correct path if you're having issues with NLTK data
nltk.data.path.append(r'D:\PRO\source_code\chatbot-deployment\venv\Lib\site-packages\nltk')

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# Set device to GPU if available, otherwise use CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# File paths
intents_file = 'intents_new.json'
data_file = 'data.pth'

# Check if the required files exist
if not os.path.exists(intents_file):
    print(f"{intents_file} file not found.")
    exit()

if not os.path.exists(data_file):
    print(f"{data_file} file not found.")
    exit()

# Load the intents data
with open(intents_file, 'r') as json_data:
    intents = json.load(json_data)

# Load the pre-trained model data securely
data = torch.load(data_file, weights_only=True)

# Neural network parameters
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

# Load the trained neural network model
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

# Function to get a response based on the user's message
def get_response(msg):
    threshold = 0.72  # تقدر تغيرها حسب تجربتك

    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # طباعة معلومات التنقيح
    print(f"Tag Detected: {tag}, Confidence: {prob.item():.2f}")

    if prob.item() > threshold:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                valid_responses = [
                    resp for resp in intent['responses']
                    if "[insert" not in resp and "http" not in resp and resp.strip() != ""
                ]
                if valid_responses:
                    return random.choice(valid_responses)
                else:
                    return "I found the topic you're asking about, but I don't have a detailed answer at the moment."

    return "I'm not sure what you mean. Can you rephrase?"

# Function to log the conversation in a file
def log_conversation(user_input, bot_response):
    with open("chat_log.txt", "a") as log_file:
        log_file.write(f"You: {user_input}\n{bot_name}: {bot_response}\n\n")

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence.lower() == "quit":
            break

        resp = get_response(sentence)
        print(f"{bot_name}: {resp}")
        log_conversation(sentence, resp)


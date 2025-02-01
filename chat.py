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

# Load the pre-trained model data
data = torch.load(data_file)

# Neural network parameters
input_size = data["input_size"]  # Number of input features
hidden_size = data["hidden_size"]  # Number of hidden neurons
output_size = data["output_size"]  # Number of output classes
all_words = data['all_words']  # All words from the training set
tags = data['tags']  # Tags for the intents
model_state = data["model_state"]  # The trained model's state

# Load the trained neural network model
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)  # Restore the trained model state
model.eval()  # Set the model to evaluation mode

bot_name = "Sam"

# Function to get a response based on the user's message
def get_response(msg):
    """
    Processes the user's message and returns an appropriate response based on intents.
    """
    sentence = tokenize(msg)  # Tokenize the input sentence
    X = bag_of_words(sentence, all_words)  # Convert the sentence to bag-of-words representation
    X = X.reshape(1, X.shape[0])  # Reshape to match the model's input dimensions
    X = torch.from_numpy(X).to(device)  # Convert to a tensor and move to the correct device (GPU or CPU)

    output = model(X)  # Get the model's prediction
    _, predicted = torch.max(output, dim=1)  # Get the predicted tag with the highest probability

    tag = tags[predicted.item()]  # Get the corresponding tag

    probs = torch.softmax(output, dim=1)  # Compute the probabilities of all tags
    prob = probs[0][predicted.item()]  # Get the probability of the predicted tag

    # If the probability is high enough, return a response from the corresponding intent
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])  # Select a random response from the intent

    # If the probability is low, return a default message
    return "I'm not sure what you mean. Can you rephrase?"

# Function to log the conversation in a file
def log_conversation(user_input, bot_response):
    """
    Logs the conversation between the user and the bot into a text file.
    """
    with open("chat_log.txt", "a") as log_file:
        log_file.write(f"You: {user_input}\n{bot_name}: {bot_response}\n\n")

if __name__ == "__main__":
    """
    Main entry point for running the program: 
    Starts the chat with the user in the command line interface.
    """
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # Get input from the user
        sentence = input("You: ")
        if sentence.lower() == "quit":  # Check if the user wants to quit
            break

        # Get the response and log the conversation
        resp = get_response(sentence)
        print(f"{bot_name}: {resp}")

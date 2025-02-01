import numpy as np
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from nltk_utils import bag_of_words, tokenize, stem
from model import NeuralNet
with open('intents_new.json', 'r') as f:
    intents = json.load(f)
all_words = []
tags = []
xy = []
# loop through each sentence in our intents patterns
for intent in intents['intents']:
    tag = intent['tag']
    # add to tag list
    tags.append(tag)
    for pattern in intent['patterns']:
        # tokenize each word in the sentence
        w = tokenize(pattern) 
        # add to our words list (('how', 'are'), ('', 'you'))
        all_words.extend(w)
        # add to xy pair x -> pattern, y -> tag 
        xy.append((w, tag))  #[(["hello"],"grettings"),(["hey"],"grettings")]

# print('all words', all_words,'\n')
# stem and lower each word
ignore_words = ['?', '.', '!']
all_words = [stem(w) for w in all_words if w not in ignore_words] #stem the words and remove the ignore words
# remove duplicates and sort
all_words = sorted(set(all_words)) 
tags = sorted(set(tags))

# print(len(xy), "patterns")
# print(len(tags), "tags:", tags)
# print(len(all_words), "unique stemmed words:", all_words)

# print(xy, "patterns\n")
# print(tags, "tags: \n", )
# print(all_words, "unique stemmed words:\n")

# create training data
X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    # X: bag of words for each pattern_sentence
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    # print('bag of words: ',bag,'\n')
    # y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
    label = tags.index(tag)
    y_train.append(label)
    # print('label: ',label,'\n')

X_train = np.array(X_train) #[[0,0,0,1,0,],[0,0,0,1,0,],[0,0,0,1,0,]]
y_train = np.array(y_train) #[0,0,0,1,1,1]

# print('data after preparation example: ',X_train,'\n')
# print('labels example: ',y_train,'\n\n\n\n')

# Hyper-parameters 
batch_size = 8 #means that in every iteration, we train on 8 samples at the same time
input_size = len(X_train[0]) #X_train[0] same as -> all_words
hidden_size = 5
output_size = len(tags)
print(input_size, output_size)

class ChatDataset(Dataset):

    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    # support indexing such that dataset[i] can be used to get i-th sample
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    # we can call len(dataset) to return the size
    def __len__(self):
        return self.n_samples

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset,
                          batch_size=batch_size,
                          shuffle=True,
                          num_workers=0)
#shuffle to prevent the model from learning the order of the data because it will affect the model accuracy

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size, output_size).to(device)
# Loss and optimizer
criterion = nn.CrossEntropyLoss() # measures the discrepancy(تناقض) between the predicted probabilities and the true labels.
# The CrossEntropyLoss function combines the softmax function and the negative log-likelihood loss
# The negative log-likelihood loss then compares the predicted probabilities with the true labels and calculates the loss value

learning_rate = 0.001
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate) #optimze the model and update the parameters based on the lossx

#The optimizer is responsible for updating the weights and biases of the model based on the computed gradients during backpropagation

#overall goal is to iteratively update the parameters( weights and biases ) to minimize the loss function

num_epochs = 1000
# Train the model
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)
        # print('labels',labels,'\n')
        # print('words',words,'\n')
        # Forward pass
        outputs = model(words)
        # print('outputs',outputs,'\n')
        # if y would be one-hot, we must apply
        # labels = torch.max(labels, 1)[1]
        loss = criterion(outputs, labels)
        # print('loss',loss,'\n')
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    if (epoch+1) % 100 == 0:
        print (f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')


print(f'final loss: {loss.item():.4f}')

data = {
"model_state": model.state_dict(),
"input_size": input_size,
"hidden_size": hidden_size,
"output_size": output_size,
"all_words": all_words,
"tags": tags
}

# print(data)
FILE = "data.pth"
torch.save(data, FILE)

print(f'training complete. file saved to {FILE}')

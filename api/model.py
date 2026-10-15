from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

CLASSES = ['Distracted', 'Focused']

class FocusStateCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 32 * 32, 2)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = x.view(-1, 16 * 32 * 32)
        x = self.fc1(x)
        return x

TRANSFORM = transforms.Compose([
    transforms.Resize((64, 64)), #resize to 64x64
    transforms.ToTensor() #convert to tensor
])

def load_model(path: str | Path, device: str = "cpu") -> "FocusStateCNN":
    model = FocusStateCNN().to(device)
    model.load_state_dict(torch.load(path, map_location=device)) # load the model weights
    model.eval() # Turn off learning mode
    return model

def predict(model: "FocusStateCNN", image: Image.Image, device: str = "cpu") -> str:
    x = TRANSFORM(image.convert("RGB")).unsqueeze(0).to(device) # convert to RGB and add batch dimension
    with torch.no_grad(): # disable gradient calculation for inference
        idx = model(x).argmax(dim=1).item() # get the index of the class with the highest probability
    return CLASSES[idx] # return the class name


    
            

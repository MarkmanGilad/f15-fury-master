import torch
import torch.nn as nn
import torch.nn.functional as F
import copy
from constant import *

class DQN (nn.Module):
    def __init__(self, device = torch.device('cpu')) -> None:
        super().__init__()
        self.device = device
        self.linear1 = nn.Linear(DQN_INPUT_SIZE, DQN_LAYER1)
        self.linear2 = nn.Linear(DQN_LAYER1, DQN_LAYER2)
        self.linear3 = nn.Linear(DQN_LAYER2, DQN_LAYER3)
        self.output = nn.Linear(DQN_LAYER3, DQN_OUTPUT_SIZE)
        self.MSELoss = nn.MSELoss()

    def forward (self, x):
        x = self.linear1(x)
        x = F.leaky_relu(x)
        x = self.linear2(x)
        x = F.leaky_relu(x)
        x = self.linear3(x)
        x = F.leaky_relu(x)
        x = self.output(x)
        return x
    
    def loss (self, Q_values, rewards, Q_next_Values, dones ):
        Q_new = rewards.to(self.device) + GAMMA * Q_next_Values * (1- dones.to(self.device))
        return self.MSELoss(Q_values, Q_new)
    
    def load_params(self, path):
        self.load_state_dict(torch.load(path))

    def save_params(self, path):
        torch.save(self.state_dict(), path)

    def copy (self):
        return copy.deepcopy(self)

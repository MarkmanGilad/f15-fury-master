import pygame
import torch
from Environment import Environment
from airplane import Airplane
from openscreen import StartupScreen
from human_agent import Human_agent
from Ai_Agent import DQN_Agent
from endgame import EndGameScreen
from replaybuffer import ReplayBuffer
import os
import wandb
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import torchvision
import torchvision.transforms as transforms

def main():
    env = Environment(delay=0)
    human_agent = Human_agent()
    aI_agnet = DQN_Agent(parametes_path=None, train=True)
    player = aI_agnet
    player_hat = DQN_Agent()
    player_hat.DQN = player.DQN.copy()
    batch_size = 50
    buffer = ReplayBuffer(path=None)
    learning_rate = 0.0001  # הגדלתי את קצב הלמידה
    epochs = 100000
    epoch = 0
    C = 4
    loss = torch.tensor(0)
    optim = torch.optim.Adam(player.DQN.parameters(), lr=learning_rate)
    # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
    
    num = 9
    checkpoint_path = f"/save_model/checkpoint{num}.pth"
    buffer_path = f"/save_model/buffer{num}.pth"

    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
        epoch = checkpoint['epoch']+1
        player.DQN.load_state_dict(checkpoint['model_state_dict'])
        player_hat.DQN.load_state_dict(checkpoint['model_state_dict'])
        optim.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        buffer = torch.load(buffer_path)
    player.DQN.train()
    player_hat.DQN.eval()

    env.render()
    stop = False
    done = False
    step = 0
    reward= 0
    loss = torch.tensor(0)
    wanrun = wandb.init(project="F-15", name=f"test {num}")
    while(not stop):
        step += 1
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                stop = True
                break
        if done:
            # print("                                                                     ",end='\r')
            print(f'epoch: {epoch} step: {step} reward: {reward:.3f} loss: {loss.item():.3f}')

            epoch += 1
            wanrun.log({
                "time": env.time, 
                "reward": env.reward,
                "step_to_end": step 
                })
            if epoch % 1000 == 0:
                print("Saving model and buffer...")
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': player.DQN.state_dict(),
                    'optimizer_state_dict': optim.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'time': env.time,
                }
                
                torch.save(checkpoint, checkpoint_path)
                torch.save(buffer, buffer_path)
            if epoch == epochs:
                break
            # create new environment and human agent
            env.reset()
            step = 0
        env.render()
        
        
        ############## Sample Environement #########################

        state = env.Tensor_env()
        action = player.Get_Action(events=events, state=state, epoch=epoch)
        reward, done = env.move(action) 
        next_state = env.Tensor_env()
        buffer.push(state, torch.tensor(action, dtype=torch.int64), torch.tensor(reward, dtype=torch.float32), 
                    next_state, torch.tensor(done, dtype=torch.float32))

        if len(buffer) < 2000:
            continue
        
        ############## Train ################
        states, actions, rewards, next_states, dones = buffer.sample(batch_size)
        Q_values = player.Q(states, actions)
        
        next_actions, _ = player.get_Actions_Values(next_states) #DDQN
        Q_hat_Values = player_hat.Q(states=next_states, actions=next_actions)
        Q_hat_Values = Q_hat_Values.detach()

        # next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states) #DQN

        loss = player.DQN.loss(Q_values, rewards, Q_hat_Values, dones)
        loss.backward()
        optim.step()
        optim.zero_grad()
        scheduler.step()

        if env.is_end_of_game():
            if epoch % C == 0:
                player_hat.DQN.load_state_dict(player.DQN.state_dict())



        env.clock.tick(300)

    wanrun.finish()
        

if __name__ == '__main__':
    main()  # הפעל את המשחק

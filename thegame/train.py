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
from constant import *

def main():
    env = Environment(delay=0)
    human_agent = Human_agent()
    aI_agnet = DQN_Agent(parametes_path=None, train=True)
    player = aI_agnet
    player_hat = DQN_Agent()
    player_hat.DQN = player.DQN.copy()
    batch_size = BATCH_SIZE
    buffer = ReplayBuffer(path=None)
    learning_rate = LEARNING_RATE  # הגדלתי את קצב הלמידה
    epochs = TRAINING_EPOCHS
    epoch = 0
    C = TARGET_UPDATE_FREQ
    loss = torch.tensor(0)
    optim = torch.optim.Adam(player.DQN.parameters(), lr=learning_rate)
    # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim, SCHEDULER_MILESTONES, gamma=SCHEDULER_GAMMA)
    
    num = 11
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
    total_reward = 0.0
    total_loss = 0.0
    loss_count = 0
    loss = torch.tensor(0)
    wanrun = wandb.init(project="F-15", name=f"test {num}", config={
        "learning_rate": LEARNING_RATE,
        "batch_size": BATCH_SIZE,
        "gamma": GAMMA,
        "epsilon_start": EPSILON_START,
        "epsilon_final": EPSILON_FINAL,
        "epsilon_decay": EPSILON_DECAY,
        "target_update_freq": TARGET_UPDATE_FREQ,
        "replay_buffer_capacity": REPLAY_BUFFER_CAPACITY,
        "min_buffer_size": MIN_BUFFER_SIZE,
        "scheduler_milestones": SCHEDULER_MILESTONES,
        "scheduler_gamma": SCHEDULER_GAMMA,
        "dqn_input_size": DQN_INPUT_SIZE,
        "dqn_output_size": DQN_OUTPUT_SIZE,
        "network": str(player.DQN),
    })
    while(not stop):
        step += 1
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                stop = True
                break
        if done:
            # print("                                                                     ",end='\r')
            eps = player.epsilon_greedy(epoch)
            lr = optim.param_groups[0]['lr']
            print(f'epoch: {epoch} step: {step} reward: {total_reward:.3f} loss: {loss.item():.3f} eps: {eps:.4f} lr: {lr:.6f} holes: {env.holes_passed} kills: {env.enemies_killed} fuel: {env.fuels_collected}')

            epoch += 1
            wanrun.log({
                "time": env.time, 
                "reward": total_reward,
                "step_to_end": step,
                "avg_loss": total_loss / loss_count if loss_count > 0 else 0.0,
                "holes_passed": env.holes_passed,
                "enemies_killed": env.enemies_killed,
                "fuels_collected": env.fuels_collected,
                "score": env.score,
                })
            if epoch % SAVE_FREQUENCY == 0:
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
            total_reward = 0.0
            total_loss = 0.0
            loss_count = 0
        env.render()
        
        
        ############## Sample Environement #########################

        state = env.Tensor_env()
        action = player.Get_Action(events=events, state=state, epoch=epoch)
        reward, done = env.move(action)
        total_reward += reward
        next_state = env.Tensor_env()
        buffer.push(state, torch.tensor(action, dtype=torch.int64), torch.tensor(reward, dtype=torch.float32), 
                    next_state, torch.tensor(done, dtype=torch.float32))

        if len(buffer) < MIN_BUFFER_SIZE:
            continue
        
        ############## Train ################
        states, actions, rewards, next_states, dones = buffer.sample(batch_size)
        Q_values = player.Q(states, actions)
        
        next_actions, _ = player.get_Actions_Values(next_states) #DDQN
        Q_hat_Values = player_hat.Q(states=next_states, actions=next_actions)
        Q_hat_Values = Q_hat_Values.detach()

        # next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states) #DQN

        loss = player.DQN.loss(Q_values, rewards, Q_hat_Values, dones)
        total_loss += loss.item()
        loss_count += 1
        optim.zero_grad()
        loss.backward()
        optim.step()
        scheduler.step()

        if done:
            if epoch % C == 0:
                player_hat.DQN.load_state_dict(player.DQN.state_dict())



        env.clock.tick(TRAINING_FPS)

    wanrun.finish()
        

if __name__ == '__main__':
    main()  # הפעל את המשחק

import pygame
from Environment import Environment
from airplane import Airplane
from openscreen import StartupScreen
from human_agent import Human_agent
from Ai_Agent import DQN_Agent
from endgame import EndGameScreen
from constant import *


def main():
    env = Environment()
    human_agent = Human_agent()
    Agnet = DQN_Agent(parametes_path=None, train=True)
    player = human_agent

    env.render()
    stop = False
    while(not stop):

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                stop = True
                break
        
        state = env.Tensor_env()
        action = player.Get_Action(events=events, state = state)
        # print(action)
        env.move(action) 

        if env.is_end_of_game():
            # check if the player is out of gas
            if env.is_no_gas():
                env.display_out_of_gas_image()    
            # check if the player is colliding with a building
            if env.is_coliding():
                env.display_collision_image()        
            # create new environment and human agent
            EndGameScreen().run()
            env.reset()
            human_agent.reset()
        env.render()
                  
        env.clock.tick(FPS)

        

if __name__ == '__main__':
   startup_screen = StartupScreen()
   if startup_screen.run():  # אם המשתמש לחץ על "START"
    main()  # הפעל את המשחק

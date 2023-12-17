from numpy import convolve, ones, mean
from robot import HumanFollowingRobot
from DDPG_agent import DDPGAgent
import time
import os
import sys, signal
update_frequency = 0.1 
robot = HumanFollowingRobot()
agent = DDPGAgent(robot.observation_space.shape, robot.action_space.shape, lr_actor=0.000025, lr_critic=0.00025,
                      layer1_size=400, layer2_size=300, layer3_size=400, batch_size=100)
agent.load_models()                      
time.sleep(3)

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    robot.apply_action([0.0,0.0])
    time.sleep(1)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
	chosen_action = agent.choose_action_test(robot.get_observation())
	#print(chosen_action)
	robot.apply_action(chosen_action)
	#Right #Left
	time.sleep(update_frequency)	

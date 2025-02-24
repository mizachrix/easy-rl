#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-03-22 16:18:10
LastEditor: John
LastEditTime: 2021-04-28 10:13:00
Discription: 
Environment: 
'''
import sys,os
curr_path = os.path.dirname(__file__)
parent_path=os.path.dirname(curr_path) 
sys.path.append(parent_path) # add current terminal path to sys.path
import gym
import numpy as np
import torch
import datetime
from PPO.agent import PPO
from common.plot import plot_rewards
from common.utils import save_results,make_dir

curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") # obtain current time

class PPOConfig:
    def __init__(self) -> None:
        self.env = 'CartPole-v0'
        self.algo = 'PPO'
        self.result_path = curr_path+"/results/" +self.env+'/'+curr_time+'/results/'  # path to save results
        self.model_path = curr_path+"/results/" +self.env+'/'+curr_time+'/models/'  # path to save models
        self.batch_size = 5
        self.gamma=0.99
        self.n_epochs = 4
        self.actor_lr = 0.0003
        self.critic_lr = 0.0003
        self.gae_lambda=0.95
        self.policy_clip=0.2
        self.hidden_dim = 256
        self.update_fre = 20 # frequency of agent update
        self.train_eps = 300 # max training episodes
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # check gpu
        
def train(cfg,env,agent):
    rewards= []
    ma_rewards = [] # moving average rewards
    running_steps = 0
    for i_ep in range(cfg.train_eps):
        state = env.reset()
        done = False
        ep_reward = 0
        while not done:
            action, prob, val = agent.choose_action(state)
            state_, reward, done, _ = env.step(action)
            running_steps += 1
            ep_reward += reward
            agent.memory.push(state, action, prob, val, reward, done)
            if running_steps % cfg.update_fre == 0:
                agent.update()
            state = state_
        rewards.append(ep_reward)
        if ma_rewards:
            ma_rewards.append(
                0.9*ma_rewards[-1]+0.1*ep_reward)
        else:
            ma_rewards.append(ep_reward)
        print(f"Episode:{i_ep+1}/{cfg.train_eps}, Reward:{ep_reward:.3f}")
    return rewards,ma_rewards

if __name__ == '__main__':
    cfg  = PPOConfig()
    env = gym.make(cfg.env)
    env.seed(1) # Set seeds
    state_dim=env.observation_space.shape[0]
    action_dim=env.action_space.n
    agent = PPO(state_dim,action_dim,cfg)
    rewards,ma_rewards = train(cfg,env,agent)
    make_dir(cfg.result_path,cfg.model_path)
    agent.save(path=cfg.model_path)
    save_results(rewards,ma_rewards,tag='train',path=cfg.result_path)
    plot_rewards(rewards,ma_rewards,tag="train",env=cfg.env,algo = cfg.algo,path=cfg.result_path)
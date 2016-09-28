import pygame
import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # TODO: Initialize any additional variables here

        # The learning rate:
        self.alpha = 0.1

        # The discount rate:
        self.gamma = 0.2

        # the greedy value
        self.epsilon = 0.01

        #dictionary to store Q values
        self.q_values_Table ={}
        print self.q_values_Table
        
        self.actions = [None, 'forward', 'left', 'right']

        
        self.rewards = 0
        self.penalties = 0

        #These represent the past: state, action and reward
        self.pastState = None
        self.pastAction = None
        self.pastReward = None 
    
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state

        present_state = (inputs['light'],inputs['oncoming'], inputs['left'], inputs['right'], self.next_waypoint)

        self.state = present_state
        # TODO: Select action according to your policy
        present_action = self.choosing_an_Action(present_state) 

        # Execute action and get reward
        present_reward = self.env.act(self, present_action)



        # TODO: Learn policy based on state, action, reward

       
        
        #TODO: put a condition in place to identify first ever state
        if self.pastState is None: # IF gets called when the program starts running 
            self.pastAction = random.choice(self.actions)
            self.pastReward = self.env.act(self, self.pastAction)
            the_updatingQ_phase = self.the_updatingQ_phase(past_state = None, past_action = self.pastAction, past_reward = self.pastReward, present_state = present_state)
            # The current state should be saved to be accessed later on
            self.pastState = present_state
            
        #the Past state, action and reward have values  
        else:
            the_updatingQ_phase = self.the_updatingQ_phase(past_state = self.pastState, past_action = self.pastAction, past_reward = self.pastReward, present_state = present_state)
            self.pastAction = present_action
            self.pastReward = present_reward
            self.pastState = present_state


        
        # identifying the penalties 
        present_reward = self.env.act(self, present_action)
        if present_reward > 0:
            self.rewards += 1
        else:
            self.penalties += 1

            
            
        


        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

    def choosing_an_Action(self, state):
        #choose a random action 
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        
        else:
            
            q = [self.obtain_Q_value(state, a) for a in self.actions]
            
            maximum_valQ = max(q)
            
            i = self.get_maxQ_index(maximum_valQ, q)
            
            action = self.actions[i]
        return action

    
    def obtain_Q_value(self, state, action):
        q = self.q_values_Table.get((state, action), 0.0)
        return q

    # this method checks to see if there are more than 1 max Q.  It then returns the ith index of a selected q value
    def get_maxQ_index(self, maximum_valQ, q):
        #check to see if there are more than one values for max Q
        count = q.count(maximum_valQ)
        if count > 1:
        #get the index that corresponds to maximum_valQ and add them to a new array called 'best'
            best = [i for i in range(len(self.actions)) if q[i] == maximum_valQ]
            i = random.choice(best)
            # if only 1 max Q, get index for that max Q
        else:
            i = q.index(maximum_valQ)
       
        return i

    # Updating the Qtable 
    def the_Qlearner_process(self, state, action, reward, current_value):
        past_value = self.q_values_Table.get((state, action), None)
        if past_value is None:
            self.q_values_Table[(state, action)] = reward
        else:
            self.q_values_Table[(state, action)] = past_value + self.alpha * (current_value - past_value)
        

    # Obtaining the new max Q value from past state
    def the_updatingQ_phase(self, past_state, past_action, past_reward, present_state):

        max_new_q_value = max([self.obtain_Q_value(present_state, a) for a in self.actions])
        self.the_Qlearner_process(past_state, past_action, past_reward, past_reward + self.gamma*max_new_q_value)


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.00001, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    
    print a.rewards
    print a.penalties

if __name__ == '__main__':
    run()




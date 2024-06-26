import numpy as np
import random
import matplotlib.pyplot as plt
import json


class TransportEnvironment:
    def __init__(self, num_locations, num_time_steps):
        self.num_locations = num_locations
        self.num_time_steps = num_time_steps
        self.state = (0, 0)  # początkowy stan (lokalizacja, czas)

    def reset(self):
        self.state = (0, 0)
        return self.state

    def step(self, action):
        location, time_step = self.state
        new_location = (location + action) % self.num_locations
        reward = -abs(new_location - time_step) 
        self.state = (new_location, time_step + 1)
        done = (time_step + 1 == self.num_time_steps)
        return self.state, reward, done


class QLearningAgent:
    def __init__(self, num_locations, num_time_steps, num_actions, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_min=0.1,
                 epsilon_decay=0.995):
        self.num_locations = num_locations
        self.num_time_steps = num_time_steps
        self.num_actions = num_actions
        self.q_table = np.zeros((num_locations * num_time_steps, num_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def state_to_index(self, state):
        location, time_step = state
        return (location % self.num_locations) * self.num_time_steps + (time_step % self.num_time_steps)

    def choose_action(self, state):
        state_index = self.state_to_index(state)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(self.num_actions))
        else:
            return np.argmax(self.q_table[state_index])

    def update_q_value(self, state, action, reward, next_state):
        state_index = self.state_to_index(state)
        next_state_index = self.state_to_index(next_state)
        best_next_action = np.argmax(self.q_table[next_state_index])
        td_target = reward + self.gamma * self.q_table[next_state_index, best_next_action]
        td_error = td_target - self.q_table[state_index, action]
        self.q_table[state_index, action] += self.alpha * td_error

    def update_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


def simulate_day(env, agent):
    state = env.reset()
    total_reward = 0
    done = False
    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.update_q_value(state, action, reward, next_state)
        state = next_state
        total_reward += reward
    agent.update_epsilon()
    return total_reward


def run_experiments(num_episodes, env, agent):
    rewards = []
    for episode in range(num_episodes):
        total_reward = simulate_day(env, agent)
        rewards.append(total_reward)
    return rewards


def greedy_search(num_episodes_list, num_locations_list, num_time_steps_list, alpha_values, gamma_values,
                  epsilon_values, epsilon_decay=0.995, epsilon_min=0.1):
    best_params = None
    best_average_reward = float('-inf')
    results = {}

    for num_episodes in num_episodes_list:
        for num_locations in num_locations_list:
            for num_time_steps in num_time_steps_list:
                for alpha in alpha_values:
                    plt.figure(figsize=(12, 6))
                    for gamma in gamma_values:
                        for epsilon in epsilon_values:
                            print(
                                f"Testing num_episodes={num_episodes}, num_locations={num_locations}, num_time_steps={num_time_steps}, alpha={alpha}, gamma={gamma}, epsilon={epsilon}")
                            env = TransportEnvironment(num_locations, num_time_steps)
                            agent = QLearningAgent(num_locations, num_time_steps, num_locations, alpha, gamma, epsilon,
                                                   epsilon_min, epsilon_decay)
                            rewards = run_experiments(num_episodes, env, agent)
                            moving_avg_rewards = np.convolve(rewards, np.ones(100) / 100, mode='valid')
                            average_reward = np.mean(moving_avg_rewards)
                            results[(
                            num_episodes, num_locations, num_time_steps, alpha, gamma, epsilon)] = moving_avg_rewards

                            if average_reward > best_average_reward:
                                best_average_reward = average_reward
                                best_params = (num_episodes, num_locations, num_time_steps, alpha, gamma, epsilon)

                            plt.plot(moving_avg_rewards, label=f"gamma={gamma}, epsilon={epsilon}")
                    plt.xlabel('Epizod')
                    plt.ylabel('Uśredniona całkowita nagroda')
                    plt.title(
                        f'Postęp uczenia się agenta Q-Learning (num_episodes={num_episodes}, num_locations={num_locations}, num_time_steps={num_time_steps}, alpha={alpha})')
                    plt.legend()
                    plt.show()

    # Save the best parameters and results
    with open('best_params.json', 'w') as f:
        json.dump({'best_params': best_params, 'best_average_reward': best_average_reward}, f)

    print(
        f"Best parameters: num_episodes={best_params[0]}, num_locations={best_params[1]}, num_time_steps={best_params[2]}, alpha={best_params[3]}, gamma={best_params[4]}, epsilon={best_params[5]} with average reward {best_average_reward}")

    return best_params, best_average_reward, results


num_episodes_list = [2000,3000, 5000,7500, 10000]
num_locations_list = [5, 10, 15, 20, 25]
num_time_steps_list = [10, 20,30,40,50]

alpha_values = [0.1, 0.3, 0.5]
gamma_values = [0.8, 0.9, 0.99]
epsilon_values = [1.0, 0.5, 0.1]

best_params, best_average_reward, results = greedy_search(num_episodes_list, num_locations_list, num_time_steps_list,
                                                          alpha_values, gamma_values, epsilon_values)

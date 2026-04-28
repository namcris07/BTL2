import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import os

import a2_260408 as cg_logic
from coganh_env import CoGanhEnv
from coganh_agent import DQN_CoGanh
import random_agent

# Hyperparameters
BATCH_SIZE = 64
GAMMA = 0.99
EPSILON_START = 0.2
EPSILON_END = 0.02
EPSILON_DECAY = 8000
TARGET_UPDATE = 25
MEMORY_SIZE = 50000
LR = 5e-5
NUM_EPISODES = 1000
MINIMAX_TIME_LIMIT_START = 0.03
MINIMAX_TIME_LIMIT_END = 0.10
RANDOM_OPPONENT_WARMUP_RATIO = 0.10
RANDOM_OPPONENT_MIN_PROB = 0.03
TAU = 0.02

def soft_update_target_network(target_net, policy_net, tau):
    for target_param, policy_param in zip(target_net.parameters(), policy_net.parameters()):
        target_param.data.copy_(
            tau * policy_param.data + (1.0 - tau) * target_param.data
        )

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    env = CoGanhEnv()
    
    policy_net = DQN_CoGanh().to(device)

    # Tải model đã được pre-train từ bước supervised learning
    model_path = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn.pth")
    if os.path.exists(model_path):
        try:
            policy_net.load_state_dict(torch.load(model_path, map_location=device))
            print(f"[INFO] Đã tải model đã huấn luyện từ: {model_path} để tiếp tục training (fine-tuning).")
        except Exception as e:
            print(f"[WARNING] Không thể tải model, bắt đầu training từ đầu. Lỗi: {e}")

    target_net = DQN_CoGanh().to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    
    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    memory = deque(maxlen=MEMORY_SIZE)
    steps_done = 0
    
    best_reward = -float('inf')
    
    for episode in range(NUM_EPISODES):
        state = env.reset()
        total_reward = 0
        eps_threshold = EPSILON_START
        progress = episode / max(1, NUM_EPISODES - 1)
        opponent_time_limit = MINIMAX_TIME_LIMIT_START + (
            MINIMAX_TIME_LIMIT_END - MINIMAX_TIME_LIMIT_START
        ) * progress
        random_opponent_prob = max(
            RANDOM_OPPONENT_MIN_PROB,
            RANDOM_OPPONENT_WARMUP_RATIO * (1.0 - progress)
        )
        
        played_random = False
        played_minimax = False
        
        while True:
            eps_threshold = EPSILON_END + (EPSILON_START - EPSILON_END) * \
                            np.exp(-1. * steps_done / EPSILON_DECAY)
            steps_done += 1
            
            # ===== LƯỢT PHE X (DQN AGENT ĐANG TRAIN) =====
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break 
                
            if random.random() > eps_threshold:
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
                    q_values = policy_net(state_tensor)[0]
                    mask = torch.full((200,), float('-inf')).to(device)
                    for a in valid_actions: mask[a] = 0.0
                    action = torch.argmax(q_values + mask).item()
            else:
                action = random.choice(valid_actions)
                
            next_state, reward_x, done, _ = env.step(action)

            # ===== LƯỢT PHE O (MINIMAX PHẢN ĐÒN NGAY) =====
            reward_o_from_o_view = 0.0
            if not done:
                o_valid_actions = env.get_valid_actions()
                if not o_valid_actions:
                    # Phe O không còn nước đi hợp lệ -> xem như thua, kết thúc ván.
                    done = True
                    reward_o_from_o_view = -1000.0
                else:
                    use_random_opponent = (episode < int(NUM_EPISODES * RANDOM_OPPONENT_WARMUP_RATIO)) \
                        or (random.random() < random_opponent_prob)

                    if use_random_opponent:
                        played_random = True
                        opponent_move = random_agent.move(env.board, env.turn, mo_moves=env.mo_moves)
                    else:
                        played_minimax = True
                        opponent_move = cg_logic.npc_move(
                            env.board,
                            env.turn,
                            env.mo_moves,
                            time_limit=opponent_time_limit
                        )

                    if opponent_move is not None:
                        opponent_action = env.encode_action(opponent_move[0], opponent_move[1])

                        if opponent_action in o_valid_actions:
                            next_state, reward_o_from_o_view, done, _ = env.step(opponent_action)
                        else:
                            fallback_action = random.choice(o_valid_actions)
                            next_state, reward_o_from_o_view, done, _ = env.step(fallback_action)
                    else:
                        # Đối thủ không trả được nước đi hợp lệ -> xem như thua.
                        done = True
                        reward_o_from_o_view = -1000.0

            reward = reward_x - reward_o_from_o_view
            total_reward += reward

            # Lấy valid actions cho turn tiếp theo của phe X
            next_valid_actions = env.get_valid_actions() if not done else []
            memory.append((state, action, reward, next_state, done, next_valid_actions))
            state = next_state
            
            if len(memory) >= BATCH_SIZE:
                batch = random.sample(memory, BATCH_SIZE)
                state_batch = torch.FloatTensor(np.array([b[0] for b in batch])).to(device)
                action_batch = torch.LongTensor([b[1] for b in batch]).unsqueeze(1).to(device)
                reward_batch = torch.FloatTensor([b[2] for b in batch]).to(device)
                next_state_batch = torch.FloatTensor(np.array([b[3] for b in batch])).to(device)
                done_batch = torch.FloatTensor([b[4] for b in batch]).to(device)
                next_valid_actions_batch = [b[5] for b in batch]
                
                state_action_values = policy_net(state_batch).gather(1, action_batch)
                
                with torch.no_grad():
                    # Double DQN with legal-masked actions
                    next_q_values_policy = policy_net(next_state_batch)
                    next_q_values_target = target_net(next_state_batch)
                    next_state_values = torch.zeros(BATCH_SIZE, device=device)

                    for i, valid_acts in enumerate(next_valid_actions_batch):
                        # Không bootstrap ở terminal hoặc trạng thái không còn action hợp lệ.
                        if done_batch[i] > 0.5 or not valid_acts:
                            continue

                        valid_idx = torch.tensor(valid_acts, dtype=torch.long, device=device)
                        best_idx_in_valid = torch.argmax(next_q_values_policy[i, valid_idx]).item()
                        best_action = valid_idx[best_idx_in_valid]
                        next_state_values[i] = next_q_values_target[i, best_action]
                    
                expected_state_action_values = reward_batch + (next_state_values * GAMMA * (1 - done_batch))
                
                criterion = nn.SmoothL1Loss()
                loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
                
                optimizer.zero_grad()
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=1.0)
                
                optimizer.step()

                soft_update_target_network(target_net, policy_net, TAU)
                
            if done: break

        # Save best model
        if total_reward > best_reward:
            best_reward = total_reward
            best_save_path = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn_best.pth")
            os.makedirs(os.path.dirname(best_save_path), exist_ok=True)
            torch.save(policy_net.state_dict(), best_save_path)

        if episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())
            
            if played_random and played_minimax: ep_opponent = "mix"
            elif played_random: ep_opponent = "random"
            elif played_minimax: ep_opponent = "minimax"
            else: ep_opponent = "none"
            
            print(
                f"Episode {episode} | Reward: {total_reward:.2f} | Best Reward: {best_reward:.2f} | Epsilon: {eps_threshold:.2f} "
                f"| Opponent: {ep_opponent} "
                f"| Minimax time_limit: {opponent_time_limit:.3f}"
            )

    save_path = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(policy_net.state_dict(), save_path)
    print(f"Training completed. Model saved to {save_path}")

if __name__ == "__main__":
    train()
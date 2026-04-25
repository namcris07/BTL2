import random
import torch
import torch.nn as nn
import numpy as np
import os

# Import logic Cờ Gánh chỉ để lấy các nước đi hợp lệ
import a2_260408 as cg_logic

# ==========================================
# 1. KIẾN TRÚC MẠNG NƠ-RON CHÍNH (Giải thuật Deep Q-Network)
# ==========================================
class DQN_CoGanh(nn.Module):
    def __init__(self, input_shape=(3, 5, 5), num_actions=200):
        super(DQN_CoGanh, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 5 * 5, 256),
            nn.ReLU(),
            nn.Linear(256, num_actions)
        )

    def forward(self, x):
        x = self.conv(x)
        return self.fc(x)

# ==========================================
# 2. KHỞI TẠO & TẢI TRỌNG SỐ 10 TIẾNG
# ==========================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DQN_CoGanh().to(device)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn.pth")
if os.path.exists(MODEL_PATH):
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    except Exception as e:
        print("[WARNING] Không thể tải model, sẽ dùng random.")
model.eval()

# ==========================================
# 3. CÁC HÀM HỖ TRỢ TRẠNG THÁI
# ==========================================
DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

def encode_action(start, end):
    start_r, start_c = start
    end_r, end_c = end
    dir_r, dir_c = end_r - start_r, end_c - start_c
    try: dir_idx = DIRECTIONS.index((dir_r, dir_c))
    except ValueError: return -1
    return (start_r * 5 + start_c) * 8 + dir_idx

def decode_action(action_idx):
    square_idx, dir_idx = action_idx // 8, action_idx % 8
    start_r, start_c = square_idx // 5, square_idx % 5
    dir_r, dir_c = DIRECTIONS[dir_idx]
    return ((start_r, start_c), (start_r + dir_r, start_c + dir_c))

def get_state(board, player):
    state = np.zeros((3, 5, 5), dtype=np.float32)
    for r in range(5):
        for c in range(5):
            if board[r][c] == player: state[0, r, c] = 1.0
            elif board[r][c] == -player: state[1, r, c] = 1.0
    state[2, :, :] = 1.0 
    return state

# ==========================================
# 4. HÀM MOVE ĐỂ NỘP BÀI (Chỉ dùng trực giác Mạng Nơ-ron)
# ==========================================
def move(board, player, remain_time):
    # Lấy danh sách nước đi hợp lệ
    valid_moves = cg_logic.get_valid_moves(board, player)
    if not valid_moves: 
        return None
        
    # Nạp bàn cờ vào mạng Nơ-ron
    state_tensor = torch.FloatTensor(get_state(board, player)).unsqueeze(0).to(device)
    with torch.no_grad(): 
        q_values = model(state_tensor)[0]
        
    # Tạo mặt nạ (mask) để loại bỏ các nước đi sai luật
    mask = torch.full((200,), float('-inf')).to(device)
    for m in valid_moves:
        idx = encode_action(m[0], m[1])
        if idx != -1: 
            mask[idx] = 0.0
            
    # Áp dụng mặt nạ và chọn nước đi có Q-value cao nhất
    masked_q_values = q_values + mask
    best_action_idx = torch.argmax(masked_q_values).item()
    
    # Fallback an toàn: Nếu mạng lỗi, đi random trong danh sách hợp lệ
    if masked_q_values[best_action_idx] == float('-inf'): 
        return random.choice(valid_moves)
        
    return decode_action(best_action_idx)
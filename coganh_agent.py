import time
import random
import os
import a2_260408 as cg_logic

# ==========================================
# 1. KHỞI TẠO PYTORCH (CHỈ DÙNG Ở ROOT ĐỂ LẤY LỢI THẾ TỐC ĐỘ)
# ==========================================
USE_TORCH = False
model = None
device = None

try:
    import torch
    import torch.nn as nn
    import numpy as np

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

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DQN_CoGanh().to(device)
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn_best.pth")
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn.pth")
        
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.eval()
        USE_TORCH = True
except ImportError:
    pass

DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

def encode_action(start, end):
    start_r, start_c = start
    end_r, end_c = end
    dir_r, dir_c = end_r - start_r, end_c - start_c
    try: return (start_r * 5 + start_c) * 8 + DIRECTIONS.index((dir_r, dir_c))
    except ValueError: return -1

def get_state_numpy(board, player):
    state = np.zeros((3, 5, 5), dtype=np.float32)
    for r in range(5):
        for c in range(5):
            if board[r][c] == player: state[0, r, c] = 1.0
            elif board[r][c] == -player: state[1, r, c] = 1.0
    state[2, :, :] = 1.0 
    return state

# ==========================================
# 2. KHẮC CHẾ HEURISTIC CỦA MINIMAX ĐỊCH
# ==========================================
def evaluate_board(board, root_player):
    enemy = -root_player
    my_pieces = 0
    enemy_pieces = 0
    safe_score = 0
    
    for i in range(5):
        for j in range(5):
            if board[i][j] == root_player:
                my_pieces += 1
                # Chặn bài của địch: Địch đánh giá góc +15, ta đánh giá góc +20 để luôn giành giật trước
                if (i, j) in [(0, 0), (0, 4), (4, 0), (4, 4)]: safe_score += 20
                elif i == 0 or i == 4 or j == 0 or j == 4: safe_score += 5
                elif (i, j) == (2, 2): safe_score += 10 # Ta chiếm thêm trung tâm
            elif board[i][j] == enemy:
                enemy_pieces += 1
                if (i, j) in [(0, 0), (0, 4), (4, 0), (4, 4)]: safe_score -= 20
                elif i == 0 or i == 4 or j == 0 or j == 4: safe_score -= 5
                elif (i, j) == (2, 2): safe_score -= 10
                
    if enemy_pieces == 0: return 10000
    if my_pieces == 0: return -10000
    
    return (my_pieces - enemy_pieces) * 100 + safe_score

def order_moves_root(board, player, valid_moves):
    """CHỈ GỌI 1 LẦN TẠI ROOT ĐỂ KHÔNG LÀM CHẬM TỐC ĐỘ MINIMAX"""
    shuffled_moves = valid_moves.copy()
    random.shuffle(shuffled_moves)
    
    if not USE_TORCH: return shuffled_moves
        
    state_tensor = torch.FloatTensor(get_state_numpy(board, player)).unsqueeze(0).to(device)
    with torch.no_grad(): q_values = model(state_tensor)[0]
    
    scored = []
    for m in shuffled_moves:
        idx = encode_action(m[0], m[1])
        scored.append((q_values[idx].item() if idx != -1 else float('-inf'), m))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]

# ==========================================
# 3. ALPHA-BETA (THUẦN PYTHON ĐỂ TỐI ĐA HÓA TỐC ĐỘ)
# ==========================================
class TimeoutException(Exception): pass

def alpha_beta(board, player, depth, alpha, beta, is_maximizing, root_player, end_time, current_mo=None):
    if time.time() > end_time:
        raise TimeoutException()

    my_pieces = sum(row.count(root_player) for row in board)
    enemy_pieces = sum(row.count(-root_player) for row in board)
    if depth == 0 or my_pieces == 0 or enemy_pieces == 0:
        return evaluate_board(board, root_player)

    current_turn = root_player if is_maximizing else -root_player
    valid_moves = cg_logic.get_valid_moves(board, current_turn)
    
    if current_mo and len(current_mo) > 0:
        forced = [m for m in valid_moves if m in current_mo]
        if forced: valid_moves = forced
            
    if not valid_moves:
        return -10000 if is_maximizing else 10000

    # KHÔNG DÙNG PYTORCH Ở ĐÂY NỮA, LẤY ĐẦY ĐỦ TỐC ĐỘ!
    moves_to_search = valid_moves 

    if is_maximizing:
        max_eval = float('-inf')
        for m in moves_to_search:
            board_copy = cg_logic.copy_board(board)
            next_mo = cg_logic.act_moves(m, current_turn, board_copy)
            eval = alpha_beta(board_copy, player, depth - 1, alpha, beta, False, root_player, end_time, next_mo)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for m in moves_to_search:
            board_copy = cg_logic.copy_board(board)
            next_mo = cg_logic.act_moves(m, current_turn, board_copy)
            eval = alpha_beta(board_copy, player, depth - 1, alpha, beta, True, root_player, end_time, next_mo)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

# ==========================================
# 4. HÀM MAIN MOVE
# ==========================================
def move(board, player, remain_time):
    start_time = time.time()
    TIME_LIMIT = 2.8 # Đè bẹp 0.1s của địch bằng 2.8s suy nghĩ
    end_time = start_time + TIME_LIMIT
    
    valid_moves = cg_logic.get_valid_moves(board, player)
    if not valid_moves: return None
        
    # Lợi thế duy nhất DQN can thiệp: Chọn nước đi đầu tiên cực gắt
    ordered_valid_moves = order_moves_root(board, player, valid_moves)
    best_move = ordered_valid_moves[0]
    
    depth = 1
    try:
        while True:
            current_best_move = None
            best_value = float('-inf')
            alpha = float('-inf')
            beta = float('inf')
            
            for m in ordered_valid_moves:
                if time.time() > end_time:
                    raise TimeoutException()
                    
                board_copy = cg_logic.copy_board(board)
                next_mo = cg_logic.act_moves(m, player, board_copy)
                
                board_val = alpha_beta(board_copy, player, depth - 1, alpha, beta, False, player, end_time, next_mo)
                
                if board_val > best_value:
                    best_value = board_val
                    current_best_move = m
                alpha = max(alpha, best_value)
                
            if current_best_move:
                best_move = current_best_move
                
            if best_value >= 10000:
                break
            depth += 1
            
    except TimeoutException:
        pass
        
    return best_move
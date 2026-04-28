import numpy as np
import random
import os
import time
import multiprocessing as mp
import a2_260408 as cg_logic
from coganh_env import CoGanhEnv

def simulate_one_game(game_idx):
    """Hàm chạy 1 ván đấu độc lập để phân phối cho các CPU"""
    env = CoGanhEnv()
    board = cg_logic.init_board()
    player = 1
    mo = []
    move_count = 0
    max_moves = 100

    mode = random.choice([
        "teacher_x_random_o",
        "random_x_teacher_o",
        "teacher_both"
    ])
    
    local_states = []
    local_actions = []

    while move_count < max_moves:
        valid_moves = cg_logic.get_valid_moves(board, player)
        if not valid_moves:
            break

        # Lượt của Teacher (Minimax) tùy theo chế độ sinh dữ liệu
        is_teacher_turn = (
            mode == "teacher_both" or
            (mode == "teacher_x_random_o" and player == 1) or
            (mode == "random_x_teacher_o" and player == -1)
        )

        if is_teacher_turn:
            env.board = [row[:] for row in board]
            env.turn = player
            state = env.get_state()

            best_move = cg_logic.npc_move(board, player, mo, time_limit=0.1)
            if best_move is None:
                break

            action_idx = env.encode_action(best_move[0], best_move[1])
            if action_idx != -1:
                local_states.append(state)
                local_actions.append(action_idx)
            chosen_move = best_move
            
        # Lượt của Bot Random khi không phải teacher turn
        else:
            if mo and any(m in mo for m in valid_moves):
                chosen_move = random.choice([m for m in valid_moves if m in mo])
            else:
                chosen_move = random.choice(valid_moves)

        mo = cg_logic.act_moves(chosen_move, player, board)
        player *= -1
        move_count += 1

    return local_states, local_actions

def collect_data_mp(num_games=1000, out_path=None):
    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__), "data", "coganh_teacher.npz")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print(f"[INFO] Bắt đầu thu thập {num_games} ván đấu bằng Multiprocessing...")
    start_time = time.time()
    
    # Lấy số luồng CPU tối đa của máy, chừa lại 1 luồng để máy tính không bị đơ
    num_cores = max(1, mp.cpu_count() - 3)
    print(f"[INFO] Phát hiện CPU! Đang sử dụng {num_cores} luồng để chạy song song.")

    all_states = []
    all_actions = []
    completed = 0

    # Chạy song song
    with mp.Pool(num_cores) as pool:
        for states, actions in pool.imap_unordered(simulate_one_game, range(num_games)):
            all_states.extend(states)
            all_actions.extend(actions)
            completed += 1
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                print(f"[INFO] Đã mô phỏng {completed}/{num_games} ván. Thời gian chạy: {elapsed:.1f}s. Dataset: {len(all_states)} nước đi.")

    states_array = np.stack(all_states, axis=0).astype(np.float32)
    actions_array = np.array(all_actions, dtype=np.int64)
    np.savez(out_path, states=states_array, actions=actions_array)
    print(f"[INFO] Thu thập xong! Đã lưu dữ liệu vào '{out_path}'. Tổng thời gian: {(time.time() - start_time)/60:.1f} phút.")

if __name__ == "__main__":
    # Rất quan trọng khi chạy multiprocessing trên Windows
    mp.freeze_support()
    collect_data_mp()
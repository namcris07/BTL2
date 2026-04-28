import os
import random

import a2_260408 as cg_logic
import coganh_agent  # <--- Đã import file Agent mới của chúng ta
import random_agent

def play_game(agent_1, agent_2, agent_1_role):
    """
    Giả lập 1 ván cờ giới hạn tối đa 100 lượt đi.
    agent_1: "dqn" (Bây giờ là Hybrid DQN-Minimax)
    agent_2: "random" hoặc "minimax"
    agent_1_role: 1 (đi trước) hoặc -1 (đi sau)
    """
    board = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, -1],
        [-1, 0, 0, 0, -1],
        [-1, -1, -1, -1, -1]
    ]
    
    current_player = 1
    mo_moves = []
    
    for turn in range(100): # Tối đa 100 lượt (mỗi bên 50)
        # 1. Kiểm tra điều kiện hết quân
        p1_pieces = sum(row.count(1) for row in board)
        p2_pieces = sum(row.count(-1) for row in board)
        if p1_pieces == 0: return -1 # O thắng
        if p2_pieces == 0: return 1  # X thắng
        
        # 2. Kiểm tra hết nước đi hợp lệ
        if len(mo_moves) == 0:
            valid_moves = cg_logic.get_valid_moves(board, current_player)
            if not valid_moves:
                return -current_player # Đối phương thắng
        
        # 3. Lấy nước đi của phe hiện tại
        move = None
        if current_player == agent_1_role:
            
            # --- ĐÃ SỬA: SỬ DỤNG HYBRID AGENT ---
            # Xử lý luật "Mở": Nếu đang bị đối phương Mở, bắt buộc phải đi vào chỗ đó
            if mo_moves and len(mo_moves) > 0:
                # Lấy các nước đi hợp lệ nằm trong danh sách bắt buộc
                valid_mo = [m for m in cg_logic.get_valid_moves(board, current_player) if m in mo_moves]
                if valid_mo:
                    move = random.choice(valid_mo)
                else:
                    move = coganh_agent.move(board, current_player, remain_time=99)
            else:
                # Gọi Hybrid Alpha-Beta (Cho phép suy nghĩ 2.8s)
                move = coganh_agent.move(board, current_player, remain_time=99)
            # ------------------------------------
            
        else:
            if agent_2 == "random":
                move = random_agent.move(board, current_player, mo_moves=mo_moves)
            elif agent_2 == "minimax":
                try:
                    move = cg_logic.npc_move(board, current_player, mo=mo_moves if mo_moves else None, time_limit=0.1)
                except TimeoutError:
                    # Fallback nếu time_limit xử lý raise error
                    move = random_agent.move(board, current_player, mo_moves=mo_moves)
        
        if move is None:
            return -current_player # Mất khả năng đi -> Thua
            
        # 4. Cập nhật bàn cờ
        mo_moves = cg_logic.act_moves(move, current_player, board)
        current_player *= -1
        
    # Hết 100 lượt không ai hết quân -> Hòa
    return 0

def run_evaluation():
    print("=================================================")
    print("Bắt đầu giả lập thi đấu Hybrid DQN-Minimax (Evaluation)...")
    print("=================================================")
    
    results = {
        "random": { 1: {"W": 0, "L": 0, "D": 0}, -1: {"W": 0, "L": 0, "D": 0} },
        "minimax": { 1: {"W": 0, "L": 0, "D": 0}, -1: {"W": 0, "L": 0, "D": 0} }
    }
    
    opponents = ["random", "minimax"]
    roles = [1, -1]
    num_games = 50 # 50 ván cho mỗi role (tổng 100 ván/đối thủ)
    
    for opp in opponents:
        print(f"\n[HYBRID vs {opp.upper()}]")
        for role in roles:
            role_name = "Đi trước" if role == 1 else "Đi sau  "
            print(f"-> HYBRID {role_name}: ", end="", flush=True)
            
            for g in range(num_games):
                winner = play_game("dqn", opp, role)
                if winner == role:
                    results[opp][role]["W"] += 1
                elif winner == -role:
                    results[opp][role]["L"] += 1
                else:
                    results[opp][role]["D"] += 1
                    
                if (g+1) % 10 == 0:
                    print(".", end="", flush=True)
            print(" Hoàn thành!")

    # Xuất báo cáo theo format yêu cầu
    report = []
    report.append("BÁO CÁO KẾT QUẢ THI ĐẤU HYBRID DQN-MINIMAX (100 ván / Đối thủ)")
    report.append("=================================================")
    
    for i, opp in enumerate(opponents):
        opp_name = "RANDOM AGENT" if opp == "random" else "MINIMAX AGENT (time_limit=0.1)"
        report.append(f"{i+1}. HYBRID vs {opp_name}")
        
        total_W = total_L = total_D = 0
        
        for role in roles:
            w = results[opp][role]["W"]
            l = results[opp][role]["L"]
            d = results[opp][role]["D"]
            
            total_W += w
            total_L += l
            total_D += d
            
            # Win Rate = (W + D/2) / Số ván
            win_rate = (w + d / 2.0) / num_games * 100
            
            role_str = "Đi trước" if role == 1 else "Đi sau  "
            report.append(f"- HYBRID {role_str} ({num_games} ván): W: {w:2d}, L: {l:2d}, D: {d:2d} | Win Rate: {win_rate:5.1f}%")
            
        total_games = num_games * 2
        total_win_rate = (total_W + total_D / 2.0) / total_games * 100
        report.append(f"- Tổng cộng ({total_games} ván):   W: {total_W:2d}, L: {total_L:2d}, D: {total_D:2d} | Win Rate: {total_win_rate:5.1f}%")
        report.append("")
        
    report.append("=================================================")
    
    report_text = "\n".join(report)
    print("\n" + report_text)
    
    eval_file_path = os.path.join(os.path.dirname(__file__), "evaluation_results.txt")
    with open(eval_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Đã lưu kết quả chi tiết vào: {eval_file_path}")

if __name__ == "__main__":
    run_evaluation()
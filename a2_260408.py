# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 18:59:30 2021

@author: AZ
"""
import random
import time

def init_board():
    board = [[+1, +1, +1, +1, +1],
             [+1,  0,  0,  0, +1],
             [+1,  0,  0,  0, -1],
             [-1,  0,  0,  0, -1],
             [-1, -1, -1, -1, -1]]
    return board

def copy_board(board):
    new_board = [row[:] for row in board]
    return new_board

def print_board(board):
    for i in range(5):
        for j in range(5):
            if board[4-i][j] == 1:
                print('X', end = ' ')
            elif board[4-i][j] == -1:
                print('O', end = ' ')
            else:
                print('-', end = ' ')
        print()
    print()
    
def dict_neighbors():
    dict_n = {}
    for i in range(5):
        for j in range(5):
            temp = []
            if j == 0:
                temp.append((i, j+1))
            if j == 4:
                temp.append((i, j-1))
            if j > 0 and j < 4:
                temp.append((i, j-1))
                temp.append((i, j+1))
            if i == 0:
                temp.append((i+1, j))
            if i == 4:
                temp.append((i-1, j))
            if i > 0 and i < 4:
                temp.append((i-1, j))
                temp.append((i+1, j))
            if i == j:
                if i == 0:
                    temp.append((i+1, j+1))
                elif i == 4:
                    temp.append((i-1, j-1))
                else:
                    temp.append((i-1, j-1))
                    temp.append((i+1, j+1))
                    temp.append((i+1, j-1))
                    temp.append((i-1, j+1))
            elif i+j == 4:
                if i == 0:
                    temp.append((i+1, j-1))
                elif i == 4:
                    temp.append((i-1, j+1))
                else:
                    temp.append((i-1, j-1))
                    temp.append((i+1, j+1))
                    temp.append((i+1, j-1))
                    temp.append((i-1, j+1))
            if i == 0 and j == 2:
                temp.append((i+1, j-1))
                temp.append((i+1, j+1))
            if i == 4 and j == 2:
                temp.append((i-1, j-1))
                temp.append((i-1, j+1))
            if i == 2 and j == 0:
                temp.append((i+1, j+1))
                temp.append((i-1, j+1))
            if i == 2 and j == 4:
                temp.append((i+1, j-1))
                temp.append((i-1, j-1))
            dict_n[(i,j)] = temp
    return dict_n

dict_nei = dict_neighbors()

# for item in dict_nei:
#     print(item, dict_nei[item])


def get_valid_moves(board, player):
    re = []
    for i in range(5):
        for j in range(5):
            if board[i][j] == player:
                start = (i,j)
                nei = dict_nei[start]
                for item in nei:
                    if board[item[0]][item[1]] == 0:
                        re.append((start,item))
    return re

def ngang(board, i , j, enemy):
    ret = []
    if (board[i][j-1] == enemy) and (board[i][j-1] == board[i][j+1]):
        ret.append((i, j-1))
        ret.append((i, j+1)) 
    #print("ngang")
    return ret

def doc(board, i, j, enemy):
    ret = []
    if (board[i+1][j] == enemy) and (board[i+1][j] == board[i-1][j]):
        ret.append((i+1, j))
        ret.append((i-1, j))
    #print("doc")
    return ret

def cheo_1(board, i, j, enemy):
    ret = []
    if (board[i+1][j-1] == enemy) and (board[i+1][j-1] == board[i-1][j+1]):
        ret.append((i+1, j-1))
        ret.append((i-1, j+1))
    #print("cheo_1")
    return ret

def cheo_2(board, i, j, enemy):
    ret = []
    if (board[i+1][j+1] == enemy) and (board[i+1][j+1] == board[i-1][j-1]):
        ret.append((i+1, j+1))
        ret.append((i-1, j-1)) 
    #print("cheo_2")
    return ret
    
def ganh(board, i, j, enemy):
    ret = []
    if (i, j) in [(1, 1), (2, 2), (3, 3), (3, 1), (1, 3)]:
        ret = doc(board, i, j, enemy) + ngang(board, i, j, enemy) + \
                cheo_1(board, i, j, enemy) + cheo_2(board, i, j, enemy)
    if (i, j) in [(2, 1), (2, 3), (1, 2), (3, 2)]:
        ret = doc(board, i, j, enemy) + ngang(board, i, j, enemy)
    if (i, j) in [(0, 1), (0, 2), (0, 3), (4, 1), (4, 2), (4, 3)]:
        ret = ngang(board, i, j, enemy)
    if (i, j) in [(1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4)]:
        ret = doc(board, i, j, enemy)      
    return ret   

def tim_lien_thong(i, j, enemy, board):
    ret = [(i,j)]
    candidates = list(dict_nei[(i,j)])
    for item in candidates:
        if board[item[0]][item[1]] == enemy and item not in ret:
            ret.append(item)
            temp = dict_nei[item]
            for k in temp:
                if k not in candidates:
                    candidates.append(k)
    return ret

def thanh_phan_lien_thong(board, enemy):
    lien_thong = []
    for i in range(5):
        for j in range(5):
            add = True
            if board[i][j] == enemy:
                for l_temp in lien_thong:
                    if (i, j) in l_temp:
                        add = False
                if(add):
                    lien_thong.append(tim_lien_thong(i, j, enemy, board))
    return lien_thong

def tim_khi(tplt, board):
    tap_khi = dict()
    for i in range(len(tplt)):
        item_set = tplt[i]
        temp = []
        for item in item_set:
            neighbors = dict_nei[item]
            for nei in neighbors:
                if nei not in temp and board[nei[0]][nei[1]] == 0:
                    temp.append(nei)
        tap_khi[i] = len(temp)
    return tap_khi
                    

def chet(board, enemy):
    player = -1*enemy
    tplt = thanh_phan_lien_thong(board, enemy)
    khi = tim_khi(tplt, board) 
    ret = False # khong chet duoc
    for i in range(len(khi)):
        if khi[i] == 0:
            ret = True
            for (i, j) in tplt[i]:
                board[i][j] = player
    return ret
            
def act_moves(move, player, board):
    start = move[0]
    end = move[1]
    
    board[start[0]][start[1]] = 0   
    board[end[0]][end[1]] = player
    # ganh
    list_ganh = ganh(board, end[0], end[1], player*-1)
    for item in list_ganh:
        board[item[0]][item[1]] = player
    # chet
    ret2 = chet(board, player*-1)
    # mo
    mo = []
    if len(list_ganh) == 0 and not ret2:
        list_nei = dict_nei[start]
        for item in list_nei:
            if board[item[0]][item[1]] == -1 * player:
                board_copy = copy_board(board)
                move_temp = (item, start)
                ret_temp = ganh(board_copy, start[0], start[1], player)
                if len(ret_temp) > 0:
                    mo.append(move_temp)
    return mo

def evaluate_board(board, root_player):
    """
    Hàm Heuristic đánh giá trạng thái bàn cờ dựa trên 3 tiêu chí:
    1. Chênh lệch quân số (Quan trọng nhất)
    2. Độ cơ động (Mobility)
    3. Thế trận an toàn (Ưu tiên chiếm giữ các vị trí khó bị gánh/chẹt như góc, biên)
    """
    enemy = -root_player
    my_pieces = 0
    enemy_pieces = 0
    safe_score = 0
    
    # Quét toàn bộ bàn cờ để đếm quân và đánh giá vị trí an toàn
    for i in range(5):
        for j in range(5):
            if board[i][j] == root_player:
                my_pieces += 1
                # Ưu tiên vị trí an toàn: Góc (không thể bị gánh), Biên (khó bị gánh/chẹt)
                if (i, j) in [(0, 0), (0, 4), (4, 0), (4, 4)]:
                    safe_score += 15
                elif i == 0 or i == 4 or j == 0 or j == 4:
                    safe_score += 5
            elif board[i][j] == enemy:
                enemy_pieces += 1
                # Trừ điểm nếu địch chiếm được vị trí an toàn
                if (i, j) in [(0, 0), (0, 4), (4, 0), (4, 4)]:
                    safe_score -= 15
                elif i == 0 or i == 4 or j == 0 or j == 4:
                    safe_score -= 5
                
    # 1. Chênh lệch quân số (Sống còn - Trọng số rất cao)
    score = (my_pieces - enemy_pieces) * 100
    
    # 2. Độ cơ động (Số lượng nước đi hợp lệ của phe ta so với phe địch)
    my_moves = get_valid_moves(board, root_player)
    enemy_moves = get_valid_moves(board, enemy)
    mobility = (len(my_moves) - len(enemy_moves)) * 2
    
    # Tổng hợp điểm: Minimax sẽ tự động mô phỏng và tránh các nước đi bị gánh/chẹt 
    # ở các độ sâu tiếp theo, kết hợp cùng `safe_score` tĩnh tạo nên Heuristic mạnh.
    total_score = score + mobility + safe_score
    return total_score

def npc_move(board, player, mo=None, remain_time=99, time_limit=2.8):
    """
    Thuật toán Minimax kết hợp Alpha-Beta Pruning và Iterative Deepening.
    Sử dụng thời gian tối ưu, tự động ngắt sớm nếu chạm mốc 2.8 giây.
    """
    start_time = time.time()
    
    def alphabeta(state, depth, alpha, beta, maximizingPlayer, current_player, current_mo, root_player):
        # 1. Quản lý thời gian: Cắt nhánh ngay lập tức nếu hết thời gian
        if time.time() - start_time > time_limit:
            raise TimeoutError()
            
        # 2. Kiểm tra trạng thái kết thúc (có phe nào bị "chẹt" hết quân không)
        root_pieces = sum(row.count(root_player) for row in state)
        enemy_pieces = sum(row.count(-root_player) for row in state)
        if root_pieces == 0:
            return -10000 # Phe ta thua tuyệt đối
        if enemy_pieces == 0:
            return 10000  # Phe ta thắng tuyệt đối
            
        if depth == 0:
            return evaluate_board(state, root_player)
            
        # 3. Xử lý logic tìm nước đi hợp lệ & luật nước đi "Mở" bắt buộc
        valid_moves = get_valid_moves(state, current_player)
        if current_mo and len(current_mo) > 0:
            valid_mo_moves = [m for m in valid_moves if m in current_mo]
            if len(valid_mo_moves) > 0:
                valid_moves = valid_mo_moves # Bắt buộc phải đi các nước "Mở" hợp lệ
                
        if not valid_moves:
            return evaluate_board(state, root_player)
            
        # 4. Triển khai Alpha-Beta
        if maximizingPlayer:
            max_eval = -float('inf')
            for move in valid_moves:
                new_board = copy_board(state)
                next_mo = act_moves(move, current_player, new_board)
                
                # Gọi đệ quy cho phe đối phương (Minimizing)
                eval = alphabeta(new_board, depth - 1, alpha, beta, False, -current_player, next_mo, root_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: # Alpha-Beta Pruning
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = copy_board(state)
                next_mo = act_moves(move, current_player, new_board)
                
                # Gọi đệ quy cho phe ta (Maximizing)
                eval = alphabeta(new_board, depth - 1, alpha, beta, True, -current_player, next_mo, root_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: # Alpha-Beta Pruning
                    break
            return min_eval

    # Bắt đầu tại Root
    valid_moves = get_valid_moves(board, player)
    
    # Ràng buộc nước đi "Mở" ở Root (Nếu có)
    if mo and len(mo) > 0:
        valid_mo_moves = [m for m in valid_moves if m in mo]
        if len(valid_mo_moves) > 0:
            valid_moves = valid_mo_moves
            
    if not valid_moves:
        return None
        
    best_move = valid_moves[0]
    depth = 1 # Bắt đầu Iterative Deepening ở độ sâu 1
    
    try:
        while True:
            # Ngắt vòng lặp tăng dần độ sâu nếu sắp hết thời gian
            if time.time() - start_time > time_limit:
                break
                
            current_best_move = valid_moves[0]
            max_eval = -float('inf')
            alpha = -float('inf')
            beta = float('inf')
            
            for move in valid_moves:
                new_board = copy_board(board)
                next_mo = act_moves(move, player, new_board)
                eval = alphabeta(new_board, depth - 1, alpha, beta, False, -player, next_mo, player)
                
                if eval > max_eval:
                    max_eval = eval
                    current_best_move = move
                    
                alpha = max(alpha, eval)
                
            # Cập nhật nước đi tốt nhất khi duyệt trọn vẹn 1 độ sâu (Depth)
            best_move = current_best_move
            depth += 1
            
            # Tối ưu hóa: Nếu phát hiện nước đi chắc chắn thắng, dừng sớm không cần duyệt sâu thêm
            if max_eval >= 10000:
                break
                
    except TimeoutError:
        # Xảy ra khi hàm alphabeta bên trong ném ra TimeoutError do chạm mốc 2.8s
        # Chương trình bắt Exception và sẽ trả về 'best_move' an toàn đã tìm được ở 'depth' trước đó
        pass
        
    return best_move



def count_X(board):
    count = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == 1:
                count = count + 1
    return count

def main2(first = 'X'):
    board = init_board()
    count = 0
    limit = 100
    if first == 'X':
        player = 1
    else:
        player = -1
    mo = []
    while(True):
        count = count + 1
        # print(count)
        # print_board(board)
        if(count > limit):
            X_pieces = count_X(board)
            if X_pieces > 8:
                return 1
            elif X_pieces < 8:
                print("So nuoc di ca van vuot 100, va so quan co cua ban < 8")
                return -1
            else:
                print("So nuoc di ca van vuot 100, va so quan co cua ban = 8")
                return 0
        #b_copy = copy_board(board)
        if player == -1:
            chose_move = npc_move(board, player, mo)
        else:
            t = time.time()
            #chose_move = move(b_copy, player)
            chose_move = npc_move(board, player, mo)
            e = time.time() - t
            if e > 3.2:
                print("Thoi gian xu ly vuot 3.2 giay")
                return -1
        if chose_move == None:
            if player == 1:
                print("Khong chon duoc nuoc di")
                return -1
            else:
                return 1
        if player == 1 or player == -1:
            if len(mo) > 0:
                # print(mo)
                if chose_move not in mo:
                    print("Nuoc di mo: ", mo)
                    print("Lua chon cua ban: ", chose_move, " sai")
                    return -1
            valid_moves = get_valid_moves(board, player)
            if chose_move not in valid_moves:
                print("Cac nuoc di hop le: ", valid_moves)
                print("Lua chon cua ban: ", chose_move, " sai")
                return -1
        mo = act_moves(chose_move, player, board)
        player = player * -1
        
    return 0          




def test():
    b = init_board()
    print_board(b)
    b[2][2] = 1
    
    print_board(b)
    
    move = ((3, 3), (3, 2))
    ret = act_moves(move, -1, b)
    b[3][1] = 1
    print_board(b)
    print(ret)
    move = ((2, 2), (3, 3))
    ret = act_moves(move, 1, b)
    print_board(b)
    print(ret)


                
                
                
# print(main2())          
                
                
            
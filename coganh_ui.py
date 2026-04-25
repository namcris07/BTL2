import tkinter as tk
import random

# Import logic Cờ Gánh
import a2_260408 as cg_logic
import coganh_agent

try:
    import winsound
except ImportError:
    winsound = None

class CoGanhUI:
    def __init__(self, root, spacing=80, margin=40, delay=500):
        self.root = root
        self.spacing = spacing
        self.margin = margin
        self.delay = delay

        # Khởi tạo trạng thái game
        self.board = cg_logic.init_board()
        self.turn = 1  # 1: X (AI DQN), -1: O (Minimax)
        self.mo = []
        self.move_count = 0

        # Thiết lập Canvas
        width = self.margin * 2 + self.spacing * 4
        height = self.margin * 2 + self.spacing * 4 + 40
        self.canvas = tk.Canvas(root, width=width, height=height, bg="#D2B48C")
        self.canvas.pack()

        # Thông báo trạng thái
        self.status_var = tk.StringVar()
        self.status = tk.Label(root, textvariable=self.status_var, font=('Helvetica', 11, 'bold'))
        self.status.pack()

        # Cụm Nút bấm
        controls = tk.Frame(root)
        controls.pack(pady=5)
        self.start_btn = tk.Button(controls, text="Start", command=self.start_game, bg='#4CAF50', fg='white', font=('Helvetica', 10, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.step_btn = tk.Button(controls, text="Step", command=self.step, bg='#2196F3', fg='white', font=('Helvetica', 10, 'bold'))
        self.step_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn = tk.Button(controls, text="Reset", command=self.reset, bg='#F44336', fg='white', font=('Helvetica', 10, 'bold'))
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.is_running = False

        self.draw_board()
        self.draw_pieces()
        self.update_status()

    def draw_board(self):
        self.canvas.delete('grid')
        # Vẽ các đường nối theo đúng chuẩn luật lệ (từ dict_nei)
        for r in range(5):
            for c in range(5):
                neighbors = cg_logic.dict_nei[(r, c)]
                for nr, nc in neighbors:
                    # Chỉ vẽ 1 chiều để tránh trùng lặp
                    if r < nr or (r == nr and c < nc):
                        x1 = self.margin + c * self.spacing
                        y1 = self.margin + r * self.spacing
                        x2 = self.margin + nc * self.spacing
                        y2 = self.margin + nr * self.spacing
                        self.canvas.create_line(x1, y1, x2, y2, fill="#5D4037", width=3, tags='grid')
                        
        # Vẽ các chấm tọa độ
        for r in range(5):
            for c in range(5):
                x = self.margin + c * self.spacing
                y = self.margin + r * self.spacing
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="#3E2723", tags='grid')

    def draw_pieces(self):
        self.canvas.delete('piece')
        for r in range(5):
            for c in range(5):
                val = self.board[r][c]
                if val != 0:
                    x = self.margin + c * self.spacing
                    y = self.margin + r * self.spacing
                    
                    if val == 1:
                        # Quân X - Xanh
                        fill_color = "#1E88E5"
                        text_color = "white"
                        text = "X"
                    else:
                        # Quân O - Đỏ
                        fill_color = "#E53935"
                        text_color = "white"
                        text = "O"
                    
                    # Vẽ bóng đổ (shadow)
                    self.canvas.create_oval(x-18, y-18, x+22, y+22, fill="#212121", outline="", tags='piece')
                    # Vẽ quân cờ
                    self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=fill_color, outline="#FAFAFA", width=2, tags='piece')
                    # Vẽ text
                    self.canvas.create_text(x, y, text=text, fill=text_color, font=('Helvetica', 14, 'bold'), tags='piece')

    def update_status(self):
        turn_str = "X (AI Nơ-ron)" if self.turn == 1 else "O (Minimax)"
        x_count = sum(row.count(1) for row in self.board)
        o_count = sum(row.count(-1) for row in self.board)
        self.status_var.set(f"Lượt: {turn_str} | Move: {self.move_count}\n[Quân số] X: {x_count}  -  O: {o_count}")

    def get_agent_move(self):
        """Lấy nước đi từ AI tương ứng"""
        valid_moves = cg_logic.get_valid_moves(self.board, self.turn)
        if not valid_moves:
            return None
            
        # Ưu tiên các nước đi bắt buộc nếu đang bị "Mở"
        forced_moves = [m for m in valid_moves if m in self.mo] if self.mo else []
        
        if self.turn == 1:
            # Lượt của AI DQN
            if forced_moves:
                return random.choice(forced_moves)
            return coganh_agent.move(self.board, self.turn, 99)
        else:
            # Lượt của Minimax
            if forced_moves:
                return random.choice(forced_moves)
            return cg_logic.npc_move(self.board, self.turn, self.mo)

    def step(self):
        x_count = sum(row.count(1) for row in self.board)
        o_count = sum(row.count(-1) for row in self.board)
        
        if x_count == 0 or o_count == 0 or self.move_count >= 100:
            self.handle_game_over(x_count, o_count)
            return

        chosen_move = self.get_agent_move()
        
        if chosen_move is None:
            self.handle_game_over(x_count, o_count, no_moves=True)
            return

        # Thực hiện nước đi
        self.mo = cg_logic.act_moves(chosen_move, self.turn, self.board)
        self.move_count += 1
        self.turn *= -1

        self.draw_pieces()
        self.update_status()
        
        if winsound:
            winsound.MessageBeep()

        # Kiểm tra thắng thua sau nước đi
        x_count = sum(row.count(1) for row in self.board)
        o_count = sum(row.count(-1) for row in self.board)
        if x_count == 0 or o_count == 0 or self.move_count >= 100:
            self.handle_game_over(x_count, o_count)

    def handle_game_over(self, x_count, o_count, no_moves=False):
        self.is_running = False
        self.start_btn.config(text='Start', bg='#4CAF50')
        
        if x_count == 0:
            winner = "O (Minimax) THẮNG!"
        elif o_count == 0:
            winner = "X (AI Nơ-ron) THẮNG!"
        else:
            if x_count > o_count:
                winner = "HẾT GIỜ! X THẮNG!"
            elif o_count > x_count:
                winner = "HẾT GIỜ! O THẮNG!"
            else:
                winner = "HÒA NHAU!"
                
        if no_moves:
            winner = "Hết nước đi! " + winner
            
        self.show_overlay(winner)

    def show_overlay(self, text):
        self.canvas.delete('overlay')
        cx = (self.margin * 2 + self.spacing * 4) / 2
        cy = (self.margin * 2 + self.spacing * 4) / 2
        
        # Vẽ mảng làm mờ
        self.canvas.create_rectangle(0, 0, cx*2, cy*2, fill='#000000', stipple='gray25', outline='', tags='overlay')
        
        # Khung chứa text
        pad = 20
        self.canvas.create_rectangle(cx - 140, cy - 40, cx + 140, cy + 40, fill='#222222', outline='#FAFAFA', width=3, tags='overlay')
        
        # Shadow
        self.canvas.create_text(cx + 2, cy + 2, text=text, font=('Helvetica', 16, 'bold'), fill='black', tags='overlay')
        # Text chính
        self.canvas.create_text(cx, cy, text=text, font=('Helvetica', 16, 'bold'), fill='#FFEB3B', tags='overlay')

    def run_loop(self):
        if not self.is_running:
            return
            
        self.step()
        
        if self.is_running:
            self.root.after(self.delay, self.run_loop)

    def start_game(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(text='Pause', bg='#FFB74D')
            self.run_loop()
        else:
            self.is_running = False
            self.start_btn.config(text='Start', bg='#4CAF50')

    def reset(self):
        self.is_running = False
        self.start_btn.config(text='Start', bg='#4CAF50')
        self.board = cg_logic.init_board()
        self.turn = 1
        self.move_count = 0
        self.mo = []
        self.canvas.delete('overlay')
        self.draw_board()
        self.draw_pieces()
        self.update_status()

def main():
    root = tk.Tk()
    root.title("Cờ Gánh AI - Battle UI")
    # Có thể điều chỉnh tốc độ tự động đi qua biến delay (ms)
    ui = CoGanhUI(root, spacing=70, margin=30, delay=200) 
    root.mainloop()

if __name__ == '__main__':
    main()
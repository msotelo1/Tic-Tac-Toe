import socket
import threading
from tkinter import *
from game_logic import TicTacToeGame  # updated to match the class name you provided

# Function to send result to server
def send_game_result(result_msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))  # Change to actual server IP/port
            s.sendall(result_msg.encode())
    except Exception as e:
        print("[Error] Failed to send result to server:", e)

# Threaded function to receive remote moves
def receive_moves(ui_instance):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 8888))  # Listening port for incoming moves
        s.listen()
        print("[Info] Waiting for remote moves...")
        conn, addr = s.accept()
        print(f"[Info] Connected to {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                move = data.decode().strip()
                try:
                    row, col = map(int, move.split(','))
                    ui_instance.remote_move(row, col)
                except Exception as e:
                    print("[Error] Invalid move received:", move, e)

class TicTacToeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multicomputer Tic Tac Toe")
        self.game = TicTacToeGame()
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.build_grid()
        threading.Thread(target=receive_moves, args=(self,), daemon=True).start()

    def build_grid(self):
        for r in range(3):
            for c in range(3):
                btn = Button(self.root, text='', font=('Arial', 40), width=5, height=2,
                             command=lambda row=r, col=c: self.local_move(row, col))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def local_move(self, row, col):
        result = self.game.make_move(row, col)
        if "Invalid" not in result:
            self.update_ui(row, col)
            self.check_game_over(result)

    def remote_move(self, row, col):
        print(f"[Info] Applying remote move: ({row}, {col})")
        result = self.game.make_move(row, col)
        if "Invalid" not in result:
            self.update_ui(row, col)
            self.check_game_over(result)

    def update_ui(self, row, col):
        player = self.game.board[row][col]
        self.buttons[row][col]['text'] = player
        self.buttons[row][col]['state'] = DISABLED

    def check_game_over(self, result):
        if result in ["X wins", "O wins", "Draw"]:
            send_game_result(result)
            self.disable_all_buttons()
            print("[Game Over]", result)

    def disable_all_buttons(self):
        for row in self.buttons:
            for btn in row:
                btn['state'] = DISABLED

if __name__ == '__main__':
    root = Tk()
    app = TicTacToeUI(root)
    root.mainloop()

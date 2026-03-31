#! python3

from tkinter import *

import os
import random

from common import ExperimentFrame
from gui import GUI


class Game:
    def __init__(self, canvas, width=600, height=337):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.configure(background="white", highlightbackground="white", highlightcolor="white")

        self.cols = 10
        self.rows = 20
        self.cell = 14
        self.board_width = 0
        self.board_height = 0
        self.offset_x = 0
        self.offset_y = 0
        self.info_y = 0
        self.score_x = 0
        self.speed_x = 0
        self.controls_y = 0

        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.colors = {
            "I": "#00e5ff",
            "O": "#ffd700",
            "T": "#bf5fff",
            "S": "#2ecc71",
            "Z": "#ff4d4d",
            "J": "#3f7fff",
            "L": "#ff9f43",
        }

        self.shapes = {
            "I": [
                [(0, 1), (1, 1), (2, 1), (3, 1)],
                [(2, 0), (2, 1), (2, 2), (2, 3)],
            ],
            "O": [
                [(1, 0), (2, 0), (1, 1), (2, 1)],
            ],
            "T": [
                [(1, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (2, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (1, 2)],
                [(1, 0), (0, 1), (1, 1), (1, 2)],
            ],
            "S": [
                [(1, 0), (2, 0), (0, 1), (1, 1)],
                [(1, 0), (1, 1), (2, 1), (2, 2)],
            ],
            "Z": [
                [(0, 0), (1, 0), (1, 1), (2, 1)],
                [(2, 0), (1, 1), (2, 1), (1, 2)],
            ],
            "J": [
                [(0, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (2, 0), (1, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (2, 2)],
                [(1, 0), (1, 1), (0, 2), (1, 2)],
            ],
            "L": [
                [(2, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (1, 2), (2, 2)],
                [(0, 1), (1, 1), (2, 1), (0, 2)],
                [(0, 0), (1, 0), (1, 1), (1, 2)],
            ],
        }

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0

        self.running = False
        self.game_over = False
        self.loop_job = None
        self.restart_job = None
        self.base_tick_ms = 550
        self.tick_ms = self.base_tick_ms
        self.speed_level = 1
        self.cleared_lines_total = 0

        self.restart_seconds_remaining = None
        self.restart_show_start = False

        self.score = 0

        self._recalculate_layout()
        self._spawn_piece()
        self._draw()

    def stop(self):
        self.running = False
        if self.loop_job is not None:
            self.canvas.after_cancel(self.loop_job)
            self.loop_job = None
        if self.restart_job is not None:
            self.canvas.after_cancel(self.restart_job)
            self.restart_job = None
        self.canvas.unbind_all("<Left>")
        self.canvas.unbind_all("<Right>")
        self.canvas.unbind_all("<Down>")
        self.canvas.unbind_all("<Up>")
        self.canvas.unbind_all("<space>")

    def play(self):
        if self.running or self.game_over:
            return
        self.running = True
        self.canvas.bind_all("<Left>", lambda event: self._move(-1, 0))
        self.canvas.bind_all("<Right>", lambda event: self._move(1, 0))
        self.canvas.bind_all("<Down>", lambda event: self._move(0, 1))
        self.canvas.bind_all("<Up>", lambda event: self._rotate())
        self.canvas.bind_all("<space>", lambda event: self._hard_drop())
        self._tick()

    def _shape_cells(self, piece_type=None, rotation=None):
        if piece_type is None:
            piece_type = self.current_piece
        if rotation is None:
            rotation = self.current_rotation
        variants = self.shapes[piece_type]
        return variants[rotation % len(variants)]

    def _can_place(self, x, y, rotation=None):
        for dx, dy in self._shape_cells(rotation=rotation):
            cx = x + dx
            cy = y + dy
            if cx < 0 or cx >= self.cols or cy < 0 or cy >= self.rows:
                return False
            if self.board[cy][cx] is not None:
                return False
        return True

    def _spawn_piece(self):
        self.current_piece = random.choice(list(self.shapes.keys()))
        self.current_rotation = 0
        self.current_x = self.cols // 2 - 2
        self.current_y = 0
        if not self._can_place(self.current_x, self.current_y):
            self.game_over = True
            self.running = False
            self._start_restart_countdown()

    def _move(self, dx, dy):
        if not self.running or self.game_over:
            return
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if self._can_place(new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            self._draw()
            return True

        if dy == 1:
            self._lock_piece()
            self._clear_lines()
            self._spawn_piece()
            self._draw()
        return False

    def _rotate(self):
        if not self.running or self.game_over:
            return
        new_rotation = self.current_rotation + 1
        if self._can_place(self.current_x, self.current_y, new_rotation):
            self.current_rotation = new_rotation
            self._draw()
            return

        for kick in (-1, 1, -2, 2):
            if self._can_place(self.current_x + kick, self.current_y, new_rotation):
                self.current_x += kick
                self.current_rotation = new_rotation
                self._draw()
                return

    def _hard_drop(self):
        if not self.running or self.game_over:
            return
        while self._move(0, 1):
            pass

    def _lock_piece(self):
        for dx, dy in self._shape_cells():
            cx = self.current_x + dx
            cy = self.current_y + dy
            if 0 <= cx < self.cols and 0 <= cy < self.rows:
                self.board[cy][cx] = self.current_piece

    def _clear_lines(self):
        cleared = 0
        new_board = []
        for row in self.board:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_board.append(row)

        while len(new_board) < self.rows:
            new_board.insert(0, [None for _ in range(self.cols)])
        self.board = new_board

        if cleared:
            multiplier = {1: 1, 2: 2, 3: 4, 4: 8}.get(cleared, 1)
            self.score += cleared * 100 * multiplier

            self.cleared_lines_total += cleared
            self.speed_level = 1 + (self.cleared_lines_total // 10)
            self.tick_ms = max(100, self.base_tick_ms - (self.speed_level - 1) * 60)

    def _start_restart_countdown(self):
        if self.restart_job is not None:
            return
        self.restart_seconds_remaining = 10
        self.restart_show_start = False
        self._draw()
        self.restart_job = self.canvas.after(1000, self._countdown_step)

    def _countdown_step(self):
        self.restart_job = None
        if not self.game_over:
            return

        if self.restart_seconds_remaining is None:
            return

        if self.restart_seconds_remaining > 1:
            self.restart_seconds_remaining -= 1
            self._draw()
            self.restart_job = self.canvas.after(1000, self._countdown_step)
            return

        if self.restart_seconds_remaining == 1:
            self.restart_seconds_remaining = 0
            self.restart_show_start = True
            self._draw()
            self.restart_job = self.canvas.after(900, self._restart_game)

    def _restart_game(self):
        self.restart_job = None
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        self.game_over = False
        self.running = True
        self.score = 0
        self.tick_ms = self.base_tick_ms
        self.speed_level = 1
        self.cleared_lines_total = 0
        self.restart_seconds_remaining = None
        self.restart_show_start = False

        self._spawn_piece()
        self._draw()
        if not self.game_over:
            self.loop_job = self.canvas.after(self.tick_ms, self._tick)

    def _tick(self):
        if not self.running:
            return
        if self.game_over:
            self._draw()
            return

        self._move(0, 1)
        if self.running and not self.game_over:
            self.loop_job = self.canvas.after(self.tick_ms, self._tick)

    def _draw_block(self, col, row, color):
        x1 = self.offset_x + col * self.cell
        y1 = self.offset_y + row * self.cell
        x2 = x1 + self.cell
        y2 = y1 + self.cell
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a1a1a")

    def _draw(self):
        self.canvas.delete("all")
        self.canvas.configure(background="white", highlightbackground="white", highlightcolor="white")

        self.canvas.create_rectangle(
            self.offset_x - 2,
            self.offset_y - 2,
            self.offset_x + self.board_width + 2,
            self.offset_y + self.board_height + 2,
            fill="#000000",
            outline="#666666",
            width=2
        )

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board[row][col]
                if cell is not None:
                    self._draw_block(col, row, self.colors[cell])

        if not self.game_over and self.current_piece is not None:
            for dx, dy in self._shape_cells():
                self._draw_block(self.current_x + dx, self.current_y + dy, self.colors[self.current_piece])

        self.canvas.create_text(
            self.score_x,
            self.info_y,
            text=f"Skóre: {self.score}",
            fill="#111111",
            anchor="w",
            font=("Helvetica", 11, "bold")
        )

        self.canvas.create_text(
            self.speed_x,
            self.info_y,
            text=f"Rychlost: {self.speed_level}",
            fill="#222222",
            anchor="e",
            font=("Helvetica", 10, "bold")
        )

        self.canvas.create_text(
            self.width // 2,
            self.height - 4,
            text="[←] Vlevo   [→] Vpravo   [↑] Otočit   [↓] Dolů   [SPACE] Shodit",
            fill="#333333",
            anchor="s",
            font=("Helvetica", 11, "bold")
        )

        if self.game_over:
            self.canvas.create_rectangle(
                self.offset_x,
                self.offset_y + self.board_height // 2 - 26,
                self.offset_x + self.board_width,
                self.offset_y + self.board_height // 2 + 26,
                fill="#000000",
                outline=""
            )
            self.canvas.create_text(
                self.offset_x + self.board_width // 2,
                self.offset_y + self.board_height // 2,
                text="KONEC HRY",
                font=("Helvetica", 24, "bold"),
                fill="#ff4d4d"
            )

            countdown_text = ""
            if self.restart_show_start:
                countdown_text = "START"
            elif self.restart_seconds_remaining is not None:
                countdown_text = str(self.restart_seconds_remaining)

            if countdown_text:
                center_x = self.offset_x + self.board_width // 2
                center_y = self.offset_y + self.board_height // 2 + 42
                if countdown_text == "START":
                    countdown_label = "Spouštím..."
                else:
                    countdown_label = f"Restart za: {countdown_text}"

                text_id = self.canvas.create_text(
                    center_x,
                    center_y,
                    text=countdown_label,
                    font=("Helvetica", 20, "bold"),
                    fill="#ff4d4d"
                )
                x1, y1, x2, y2 = self.canvas.bbox(text_id)
                padding_x = 14
                padding_y = 8
                bg_id = self.canvas.create_rectangle(
                    x1 - padding_x,
                    y1 - padding_y,
                    x2 + padding_x,
                    y2 + padding_y,
                    fill="#000000",
                    outline=""
                )
                self.canvas.tag_raise(text_id, bg_id)

    def _recalculate_layout(self):
        horizontal_padding = max(8, int(self.width * 0.04))
        top_info_space = max(24, int(self.height * 0.1))
        top_padding = max(8, int(self.height * 0.03))
        controls_space = max(34, int(self.height * 0.11))

        usable_width = max(120, self.width - (2 * horizontal_padding))
        usable_height = max(120, self.height - top_padding - top_info_space - controls_space - 8)

        self.cell = max(8, min(usable_width // self.cols, usable_height // self.rows))
        self.board_width = self.cols * self.cell
        self.board_height = self.rows * self.cell

        self.offset_x = max(horizontal_padding, (self.width - self.board_width) // 2)
        self.offset_y = top_padding + top_info_space

        self.info_y = max(10, self.offset_y - 14)
        self.score_x = self.offset_x
        self.speed_x = self.offset_x + self.board_width
        self.controls_y = min(self.height - 4, self.offset_y + self.board_height + 8)

    def on_canvas_resize(self, event):
        new_width = max(100, event.width)
        new_height = max(100, event.height)
        if new_width == self.width and new_height == self.height:
            return

        self.width = new_width
        self.height = new_height
        self._recalculate_layout()
        self._draw()


class GameTest(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        canvas = Canvas(self, width=600, height=337, background="white", highlightbackground="white", highlightcolor="white")
        canvas.grid(row=0, column=0)

        self.game = Game(canvas, width=600, height=337)
        self.game.play()

    def stop(self):
        self.game.stop()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([GameTest])

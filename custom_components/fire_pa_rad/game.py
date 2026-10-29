"""Pure game logic for 4 på rad (Connect Four). No Home Assistant imports."""

from __future__ import annotations

ROWS = 6
COLS = 7
EMPTY = "."
PIECES = {1: "R", 2: "Y"}
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def new_board() -> str:
    """Return an empty board (row 0 is the top row)."""
    return EMPTY * (ROWS * COLS)


def landing_index(board: str, column: int) -> int | None:
    """Return the board index a piece dropped in column lands on, or None if full."""
    if not 0 <= column < COLS:
        return None
    for row in range(ROWS - 1, -1, -1):
        idx = row * COLS + column
        if board[idx] == EMPTY:
            return idx
    return None


def place(board: str, idx: int, piece: str) -> str:
    """Return a new board with piece placed at idx."""
    return board[:idx] + piece + board[idx + 1 :]


def winning_line(board: str, idx: int) -> list[int]:
    """Return the cells of a four-in-a-row through idx, or an empty list."""
    piece = board[idx]
    if piece == EMPTY:
        return []
    row, col = divmod(idx, COLS)
    for d_row, d_col in DIRECTIONS:
        cells = [idx]
        for sign in (1, -1):
            for step in range(1, 4):
                r, c = row + sign * step * d_row, col + sign * step * d_col
                if not (0 <= r < ROWS and 0 <= c < COLS) or board[r * COLS + c] != piece:
                    break
                cells.append(r * COLS + c)
        if len(cells) >= 4:
            return sorted(cells)
    return []


def is_full(board: str) -> bool:
    """Return True when no empty cells remain."""
    return EMPTY not in board

"""Tests for the pure game logic."""

from custom_components.fire_pa_rad import game as g


def board_with(cells: dict[tuple[int, int], str]) -> str:
    board = g.new_board()
    for (r, c), piece in cells.items():
        board = g.place(board, r * g.COLS + c, piece)
    return board


def test_landing_and_full_column():
    board = g.new_board()
    assert g.landing_index(board, 3) == 38
    for _ in range(6):
        board = g.place(board, g.landing_index(board, 0), "R")
    assert g.landing_index(board, 0) is None
    assert g.landing_index(board, 7) is None
    assert g.landing_index(board, -1) is None


def test_horizontal_vertical_and_diagonals():
    b = board_with({(5, 0): "R", (5, 1): "R", (5, 2): "R", (5, 3): "R"})
    assert g.winning_line(b, 38) == [35, 36, 37, 38]
    b = board_with({(5, 0): "R", (4, 0): "R", (3, 0): "R", (2, 0): "R"})
    assert g.winning_line(b, 14) == [14, 21, 28, 35]
    b = board_with({(5, 0): "Y", (4, 1): "Y", (3, 2): "Y", (2, 3): "Y"})
    assert g.winning_line(b, 17) == [17, 23, 29, 35]
    b = board_with({(5, 6): "Y", (4, 5): "Y", (3, 4): "Y", (2, 3): "Y"})
    assert g.winning_line(b, 17) == [17, 25, 33, 41]


def test_no_win_and_full_board():
    b = board_with({(5, 0): "R", (5, 1): "R", (5, 2): "R", (5, 4): "R"})
    assert g.winning_line(b, 37) == []
    assert not g.is_full(b)
    assert g.is_full("RY" * 21)

import logging
from pathlib import Path
from typing import List, Tuple, Optional, Set

import numpy as np


class Maze:
    """Klasa reprezentująca labirynt"""

    def __init__(self, width: int, height: int):
        """
        Inicjalizacja labiryntu
        :param width: szerokość labiryntu w komórkach
        :param height: wysokość labiryntu w komórkach
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.start_pos: Optional[Tuple[int, int]] = None
        self.end_pos: Optional[Tuple[int, int]] = None
        self.visited: Set[Tuple[int, int]] = set()
        self.path: List[Tuple[int, int]] = []

    def reset(self):
        """Resetuje stan labiryntu"""
        self.grid.fill(0)
        self.start_pos = None
        self.end_pos = None
        self.visited.clear()
        self.path.clear()

    def set_wall(self, x: int, y: int) -> bool:
        """
        Ustawia ścianę w danej pozycji
        :return: True, jeśli udało się ustawić ścianę
        """
        if not self.is_valid_position(x, y):
            return False
        # Nie pozwalamy na stawianie ścian na punktach start/koniec
        if (x, y) in [self.start_pos, self.end_pos]:
            return False
        self.grid[y][x] = 1
        return True

    def remove_wall(self, x: int, y: int) -> bool:
        """
        Usuwa ścianę z danej pozycji
        :return: True, jeśli udało się usunąć ścianę
        """
        if not self.is_valid_position(x, y):
            return False
        self.grid[y][x] = 0
        return True

    def set_start(self, x: int, y: int) -> bool:
        """
        Ustawia punkt startowy
        :return: True, jeśli udało się ustawić punkt startowy
        """
        if not self.is_valid_position(x, y) or self.is_wall(x, y):
            return False
        if (x, y) == self.end_pos:
            return False
        self.start_pos = (x, y)
        return True

    def set_end(self, x: int, y: int) -> bool:
        """
        Ustawia punkt końcowy
        :return: True, jeśli udało się ustawić punkt końcowy
        """
        if not self.is_valid_position(x, y) or self.is_wall(x, y):
            return False
        if (x, y) == self.start_pos:
            return False
        self.end_pos = (x, y)
        return True

    def is_wall(self, x: int, y: int) -> bool:
        """Sprawdza, czy w danej pozycji jest ściana"""
        if not self.is_valid_position(x, y):
            return True
        return self.grid[y][x] == 1

    def is_valid_position(self, x: int, y: int) -> bool:
        """Sprawdza, czy pozycja mieści się w granicach labiryntu"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Zwraca listę sąsiednich pozycji, do których można się przemieścić
        :return: Lista krotek (x, y) reprezentujących dostępne pozycje
        """
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # prawo, dół, lewo, góra
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y) and not self.is_wall(new_x, new_y):
                neighbors.append((new_x, new_y))
        return neighbors

    def is_complete(self) -> bool:
        """Sprawdza, czy labirynt jest gotowy do rozwiązania"""
        return self.start_pos is not None and self.end_pos is not None

    def clear_path(self):
        """Czyści ścieżkę i odwiedzone pola"""
        self.visited.clear()
        self.path.clear()

    def add_to_path(self, pos: Tuple[int, int]):
        """Dodaje pozycję do ścieżki"""
        self.path.append(pos)
        self.visited.add(pos)

    def remove_from_path(self, pos: Tuple[int, int]):
        """Usuwa pozycję ze ścieżki"""
        if pos in self.path:
            self.path.remove(pos)

import heapq
import random
from typing import List, Tuple, Set

from maze import Maze


class BaseSolver:
    """Bazowa klasa dla algorytmów rozwiązujących"""

    def __init__(self, maze: Maze):
        self.maze = maze
        self.path: List[Tuple[int, int]] = []
        self.visited: Set[Tuple[int, int]] = set()
        self.solved = False

    def reset(self):
        """Resetuje stan solvera"""
        self.path.clear()
        self.visited.clear()
        self.solved = False

    def step(self) -> bool:
        """
        Wykonuje jeden krok algorytmu
        :return: True jeśli należy kontynuować rozwiązywanie, False jeśli zakończono
        """
        raise NotImplementedError("Metoda step() musi być zaimplementowana w klasie pochodnej")


class RandomWalkSolver(BaseSolver):
    """Implementacja algorytmu Random Walk"""

    def __init__(self, maze: Maze):
        super().__init__(maze)
        self.max_steps = maze.width * maze.height * 2
        self.current_steps = 0

    def reset(self):
        """Resetuje stan solvera"""
        super().reset()
        self.current_steps = 0

    def step(self) -> bool:
        """
        Wykonuje jeden krok algorytmu Random Walk
        :return: True jeśli należy kontynuować rozwiązywanie, False jeśli zakończono
        """
        if not self.maze.is_complete() or self.solved:
            return False

        # Rozpocznij od punktu startowego jeśli ścieżka jest pusta
        if not self.path:
            self.path.append(self.maze.start_pos)
            self.visited.add(self.maze.start_pos)
            return True

        current = self.path[-1]

        # Sprawdź czy osiągnięto cel
        if current == self.maze.end_pos:
            self.solved = True
            return False

        # Sprawdź czy nie przekroczono maksymalnej liczby kroków
        if self.current_steps >= self.max_steps:
            self.reset()
            self.path.append(self.maze.start_pos)
            self.visited.add(self.maze.start_pos)
            return True

        # Znajdź dostępne sąsiednie pola
        neighbors = self.maze.get_neighbors(*current)
        unvisited = [n for n in neighbors if n not in self.visited]

        if unvisited:
            # Wybierz losowo następny krok
            next_pos = random.choice(unvisited)
            self.path.append(next_pos)
            self.visited.add(next_pos)
        else:
            # Cofnij się o jeden krok
            self.path.pop()
            if not self.path:
                self.reset()
                self.path.append(self.maze.start_pos)
                self.visited.add(self.maze.start_pos)

        self.current_steps += 1
        return True


class AStarSolver(BaseSolver):
    """Implementacja algorytmu A*"""

    def __init__(self, maze: Maze):
        super().__init__(maze)
        self.open_set: List[Tuple[float, int, Tuple[int, int]]] = []  # (f_score, counter, position)
        self.came_from: dict = {}
        self.g_score: dict = {}
        self.f_score: dict = {}
        self.counter = 0

    def heuristic(self, pos: Tuple[int, int]) -> float:
        """
        Funkcja heurystyczna (Manhattan distance)
        :return: Szacowana odległość do celu
        """
        if not self.maze.end_pos:
            return float('inf')
        x1, y1 = pos
        x2, y2 = self.maze.end_pos
        return abs(x1 - x2) + abs(y1 - y2)

    def reset(self):
        """Resetuje stan solvera"""
        super().reset()
        self.open_set.clear()
        self.came_from.clear()
        self.g_score.clear()
        self.f_score.clear()
        self.counter = 0

    def reconstruct_path(self, current: Tuple[int, int]):
        """Rekonstruuje ścieżkę od końca do początku"""
        total_path = [current]
        while current in self.came_from:
            current = self.came_from[current]
            total_path.append(current)
        total_path.reverse()
        self.path = total_path

    def step(self) -> bool:
        """
        Wykonuje jeden krok algorytmu A*
        :return: True, jeśli należy kontynuować rozwiązywanie, False, jeśli zakończono
        """
        if not self.maze.is_complete() or self.solved:
            return False

        # Inicjalizacja jeśli to pierwszy krok
        if not self.open_set:
            start = self.maze.start_pos
            self.g_score = {start: 0}
            self.f_score = {start: self.heuristic(start)}
            heapq.heappush(self.open_set, (self.f_score[start], self.counter, start))
            self.counter += 1
            return True

        # Jeśli open_set jest pusty, nie znaleziono ścieżki
        if not self.open_set:
            self.solved = True
            return False

        # Pobierz węzeł z najniższym f_score
        current = heapq.heappop(self.open_set)[2]
        self.visited.add(current)

        # Jeśli znaleziono cel, zrekonstruuj ścieżkę
        if current == self.maze.end_pos:
            self.reconstruct_path(current)
            self.solved = True
            return False

        # Sprawdź wszystkich sąsiadów
        for neighbor in self.maze.get_neighbors(*current):
            tentative_g_score = self.g_score[current] + 1

            if neighbor not in self.g_score or tentative_g_score < self.g_score[neighbor]:
                self.came_from[neighbor] = current
                self.g_score[neighbor] = tentative_g_score
                self.f_score[neighbor] = tentative_g_score + self.heuristic(neighbor)
                heapq.heappush(self.open_set, (self.f_score[neighbor], self.counter, neighbor))
                self.counter += 1

        return True

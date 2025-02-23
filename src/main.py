import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pygame

# Dodajemy ścieżkę źródłową do PYTHONPATH
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from utils.logger import CustomLogger
from maze import Maze
from solver import RandomWalkSolver, AStarSolver

# Konfiguracja loggera
logger = CustomLogger(
    name="maze_solver",
    log_file=str(Path(__file__).parent.parent / "logs" / "app.log"),
    log_level=logging.DEBUG
)


@dataclass
class Colors:
    """Klasa przechowująca kolory używane w aplikacji"""
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    GRAY: Tuple[int, int, int] = (128, 128, 128)
    RED: Tuple[int, int, int] = (255, 0, 0)
    GREEN: Tuple[int, int, int] = (0, 255, 0)
    BLUE: Tuple[int, int, int] = (0, 0, 255)
    YELLOW: Tuple[int, int, int] = (255, 255, 0)
    VISITED: Tuple[int, int, int] = (200, 200, 255)
    PATH: Tuple[int, int, int] = (255, 200, 200)


class MazeSolver:
    """Główna klasa aplikacji"""

    def __init__(self, width: int = 800, height: int = 600, cell_size: int = 20):
        logger.info("Inicjalizacja aplikacji MazeSolver")
        pygame.init()

        # Podstawowe ustawienia
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.colors = Colors()

        # Inicjalizacja okna
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Maze Solver")

        # Inicjalizacja siatki
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size

        # Inicjalizacja komponentów
        self.maze = Maze(self.grid_width, self.grid_height)
        self.random_walk_solver = RandomWalkSolver(self.maze)
        self.astar_solver = AStarSolver(self.maze)
        self.current_solver = self.random_walk_solver

        # Stan aplikacji
        self.current_algorithm = "random_walk"  # lub "astar"
        self.is_solving = False
        self.is_drawing = False
        self.is_erasing = False
        self.last_cell = None  # Ostatnio modyfikowana komórka

        logger.info(f"Utworzono siatkę o wymiarach {self.grid_width}x{self.grid_height}")

    def handle_events(self) -> bool:
        """Obsługa zdarzeń"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Zamykanie aplikacji")
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard(event)

        return True

    def handle_mouse_down(self, event: pygame.event.Event):
        """Obsługa wciśnięcia przycisku myszy"""
        x, y = self.get_grid_pos(event.pos)
        if not self.maze.is_valid_position(x, y):
            return

        if event.button == 1:  # Lewy przycisk
            self.is_drawing = True
            self.is_erasing = self.maze.is_wall(x, y)

            if self.is_erasing:
                self.maze.remove_wall(x, y)
                logger.info(f"Rozpoczęto usuwanie ścian od komórki ({x}, {y})")
            else:
                self.maze.set_wall(x, y)
                logger.info(f"Rozpoczęto rysowanie ścian od komórki ({x}, {y})")

            self.last_cell = (x, y)

        elif event.button == 3:  # Prawy przycisk
            if self.maze.start_pos is None:
                if not self.maze.is_wall(x, y) and (x, y) != self.maze.end_pos:
                    self.maze.set_start(x, y)
                    logger.info(f"Ustawiono punkt startowy w komórce ({x}, {y})")
            elif self.maze.end_pos is None:
                if not self.maze.is_wall(x, y) and (x, y) != self.maze.start_pos:
                    self.maze.set_end(x, y)
                    logger.info(f"Ustawiono punkt końcowy w komórce ({x}, {y})")
            else:
                old_start = self.maze.start_pos
                old_end = self.maze.end_pos
                self.maze.start_pos = None
                self.maze.end_pos = None
                logger.info(
                    f"Zresetowano punkty (start był w ({old_start[0]}, {old_start[1]}), koniec w ({old_end[0]}, {old_end[1]}))")
                if not self.maze.is_wall(x, y):
                    self.maze.set_start(x, y)
                    logger.info(f"Ustawiono nowy punkt startowy w komórce ({x}, {y})")

    def handle_mouse_motion(self, event: pygame.event.Event):
        """Obsługa ruchu myszy"""
        if self.is_drawing:
            x, y = self.get_grid_pos(event.pos)
            if self.maze.is_valid_position(x, y) and (x, y) != self.last_cell:
                if self.is_erasing:
                    self.maze.remove_wall(x, y)
                    logger.debug(f"Usunięto ścianę w komórce ({x}, {y})")
                else:
                    self.maze.set_wall(x, y)
                    logger.debug(f"Narysowano ścianę w komórce ({x}, {y})")
                self.last_cell = (x, y)

    def handle_mouse_up(self, event: pygame.event.Event):
        """Obsługa puszczenia przycisku myszy"""
        if event.button == 1:  # Lewy przycisk
            x, y = self.get_grid_pos(event.pos)
            self.is_drawing = False
            self.last_cell = None
            if self.is_erasing:
                logger.info(f"Zakończono usuwanie ścian na komórce ({x}, {y})")
            else:
                logger.info(f"Zakończono rysowanie ścian na komórce ({x}, {y})")
            self.is_erasing = False

    def handle_keyboard(self, event: pygame.event.Event):
        """Obsługa klawiatury"""
        if event.key == pygame.K_r:  # Reset
            logger.info("Resetowanie labiryntu - wszystkie ściany i punkty zostały usunięte")
            self.maze.reset()
            self.current_solver.reset()
            self.is_solving = False
        elif event.key == pygame.K_SPACE:  # Start/Stop rozwiązywania
            self.toggle_solving()
        elif event.key == pygame.K_a:  # Przełączanie algorytmu
            self.toggle_algorithm()

    def get_grid_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Konwersja pozycji ekranowej na pozycję w siatce"""
        x, y = pos
        return x // self.cell_size, y // self.cell_size

    def toggle_algorithm(self):
        """Przełączanie między algorytmami"""
        if self.current_algorithm == "random_walk":
            self.current_algorithm = "astar"
            self.current_solver = self.astar_solver
            logger.info("Przełączono na algorytm A*")
        else:
            self.current_algorithm = "random_walk"
            self.current_solver = self.random_walk_solver
            logger.info("Przełączono na algorytm Random Walk")

        self.current_solver.reset()
        self.is_solving = False

    def toggle_solving(self):
        """Przełączanie stanu rozwiązywania"""
        if self.maze.is_complete():
            self.is_solving = not self.is_solving
            if self.is_solving:
                self.current_solver.reset()
                logger.info(f"Rozpoczęto rozwiązywanie algorytmem {self.current_algorithm}")
            else:
                logger.info("Zatrzymano rozwiązywanie")
        else:
            logger.warning("Nie można rozpocząć rozwiązywania - brak punktu startowego lub końcowego")

    def update(self):
        """Aktualizacja stanu aplikacji"""
        if self.is_solving:
            if not self.current_solver.step():
                self.is_solving = False
                if self.current_solver.solved:
                    logger.info(f"Znaleziono rozwiązanie używając algorytmu {self.current_algorithm}")
                else:
                    logger.info(f"Nie znaleziono rozwiązania używając algorytmu {self.current_algorithm}")

    def draw(self):
        """Rysowanie interfejsu"""
        self.screen.fill(self.colors.WHITE)

        # Rysowanie siatki i ścian
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                # Rysowanie ścian
                if self.maze.is_wall(x, y):
                    pygame.draw.rect(self.screen, self.colors.BLACK, rect)
                # Rysowanie odwiedzonych pól
                elif (x, y) in self.current_solver.visited:
                    pygame.draw.rect(self.screen, self.colors.VISITED, rect)
                # Rysowanie ścieżki
                if (x, y) in self.current_solver.path:
                    pygame.draw.rect(self.screen, self.colors.PATH, rect)
                # Rysowanie siatki
                pygame.draw.rect(self.screen, self.colors.GRAY, rect, 1)

        # Rysowanie punktów startowego i końcowego
        if self.maze.start_pos:
            self.draw_point(self.maze.start_pos, self.colors.GREEN)
        if self.maze.end_pos:
            self.draw_point(self.maze.end_pos, self.colors.RED)

        pygame.display.flip()

    def draw_point(self, pos: Tuple[int, int], color: Tuple[int, int, int]):
        """Rysowanie punktu (startowego/końcowego)"""
        x, y = pos
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, color, rect)

    def run(self):
        """Główna pętla aplikacji"""
        logger.info("Rozpoczęcie głównej pętli aplikacji")
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

        logger.info("Zakończenie działania aplikacji")
        pygame.quit()


if __name__ == "__main__":
    try:
        app = MazeSolver()
        app.run()
    except Exception as e:
        logger.exception("Wystąpił nieoczekiwany błąd:")
        sys.exit(1)

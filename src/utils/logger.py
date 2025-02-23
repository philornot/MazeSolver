import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows support
colorama.init()


class ColoredFormatter(logging.Formatter):
    """
    Niestandardowy formatter dodający kolory do logów w konsoli.
    """
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }

    def format(self, record):
        # Dodaj kolor do nazwy poziomu logowania
        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


class CustomLogger:
    """
    Klasa zarządzająca logowaniem, obsługująca zarówno logi konsolowe, jak i plikowe.
    """

    def __init__(
            self,
            name: str,
            log_file: Optional[str] = None,
            log_level: int = logging.INFO,
            max_file_size: int = 5_242_880,  # 5MB
            backup_count: int = 3
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Upewnij się, że logger nie ma już handlerów
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Format dla logów
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler konsolowy
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Handler plikowy (opcjonalny)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def set_level(self, level: int):
        """Zmienia poziom logowania."""
        self.logger.setLevel(level)

    # Metody pomocnicze dla różnych poziomów logowania
    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def exception(self, message: str):
        self.logger.exception(message)


# Przykład użycia:
if __name__ == "__main__":
    # Inicjalizacja loggera
    logger = CustomLogger(
        name="example",
        log_file="logs/app.log",
        log_level=logging.DEBUG
    )

    # Przykładowe logi
    logger.debug("To jest komunikat debug")
    logger.info("To jest komunikat info")
    logger.warning("To jest ostrzeżenie")
    logger.error("To jest błąd")
    logger.critical("To jest błąd krytyczny!")

    try:
        raise ValueError("Przykładowy wyjątek")
    except Exception as e:
        logger.exception("Wystąpił wyjątek:")

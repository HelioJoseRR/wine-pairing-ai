"""
Sistema de logging estruturado
"""
import logging
import sys
from pathlib import Path

def setup_logger(name: str = "wine_pairing", level: int = logging.INFO) -> logging.Logger:
    """
    Configura e retorna um logger estruturado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formato detalhado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Handler para arquivo (opcional)
    log_dir = Path(__file__).parent.parent / "logs"
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "wine_pairing.log", encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # Se não conseguir criar logs, continua sem arquivo
    
    return logger

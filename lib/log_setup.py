import logging
import os

LOGGER_NAME = "TuxKatana"

# --- 1. Définition du niveau SYSEX ---
SYSEX = 5
logging.addLevelName(SYSEX, "SYSEX")

def sysex(self, message, *args, **kwargs):
    #if self.isEnabledFor(SYSEX):
    self._log(SYSEX, message, args, **kwargs)

logging.Logger.sysex = sysex   # ajouté une seule fois, globalement


# --- 2. Formatter par niveau ---
class LevelFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG:    "%(filename)s:%(lineno)d-%(funcName)s: %(message)s",
        logging.INFO:     "[INFO] %(message)s",
        logging.WARNING:  "⚠️ WARNING: %(message)s",
        logging.ERROR:    "❌ ERROR: %(message)s",
        logging.CRITICAL: "🔥 CRITICAL: %(message)s",
        SYSEX:            ">>> %(message)s",   # tu peux aussi mettre ton format SYSEX ici
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, "%(levelname)s: %(message)s")
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# --- 3. Filtres utiles ---
class ExcludeLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level
    def filter(self, record):
        return record.levelno != self.level

class ExactLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level
    def filter(self, record):
        return record.levelno == self.level


# --- 4. Configuration du logger ---
def setup_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        main_formatter = LevelFormatter()
        sysex_formatter = logging.Formatter(">>> %(message)s")

        # Handler fichier principal → tout sauf SYSEX
        fh_main = logging.FileHandler("logs/tuxkatana.log", mode="w", encoding="utf-8")
        fh_main.setLevel(logging.INFO)
        fh_main.setFormatter(main_formatter)
        fh_main.addFilter(ExcludeLevelFilter(SYSEX))
        logger.addHandler(fh_main)

        debug_handler = logging.StreamHandler()
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.addFilter(ExactLevelFilter(logging.DEBUG))
        debug_handler.setFormatter(logging.Formatter("%(filename)s:%(lineno)d-%(funcName)s: %(message)s"))
        logger.addHandler(debug_handler)

        # Handler fichier sysex → uniquement SYSEX
        fh_sysex = logging.FileHandler("logs/sysex.log", mode="w", encoding="utf-8")
        fh_sysex.setLevel(SYSEX)
        fh_sysex.setFormatter(sysex_formatter)
        fh_sysex.addFilter(ExactLevelFilter(SYSEX))
        logger.addHandler(fh_sysex)

        # Handler console → tout sauf SYSEX
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(main_formatter)
        sh.addFilter(ExcludeLevelFilter(SYSEX))
        sh.addFilter(ExcludeLevelFilter(logging.DEBUG))
        logger.addHandler(sh)

        logger.propagate = False
        logger.setLevel(logging.DEBUG)   # DEBUG capte tout >=5

    return logger
if __name__ == "__main__":
    log = setup_logger()

    log.debug("Un debug")
    log.sysex("Un message SYSEX")
    log.info("Un info")
    log.warning("Un warning")
    log.error("Une erreur")


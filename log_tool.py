import logging
import pathlib
import shutil

def rotate_log(new_name: str):
    logger = logging.getLogger("TuxKatana")

    # Trouver le FileHandler actif
    handler = None
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            handler = h
            break

    if handler is None:
        raise RuntimeError("No 'TuxKatana' FileHandler found")

    current_log = pathlib.Path(handler.baseFilename)
    rotated_log = current_log.with_name(f"{new_name}{current_log.suffix}")

    # Fermer le handler avant de manipuler le fichier
    logger.removeHandler(handler)
    handler.close()

    # Déplacer/renommer le fichier
    shutil.move(str(current_log), rotated_log)

    # Recréer un FileHandler vide
    new_handler = logging.FileHandler(current_log, mode="w")#, encoding="utf-8")
    fmt = logging.Formatter("[%(levelname)s] %(message)s")
    new_handler.setFormatter(fmt)
    logger.addHandler(new_handler)

    return rotated_log


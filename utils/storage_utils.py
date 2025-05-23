import os
import logging
import shutil

# Configura el logger
logger = logging.getLogger("storage")

# Ruta de respaldo local (por defecto, el directorio del proyecto)
INTERNAL_BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MIN_FREE_MB = 50
MEDIA_BASE_PATH = "/media/pi"

def find_mounted_usb(min_free_mb=MIN_FREE_MB):
    """
    Busca la primera USB montada que tenga al menos 'min_free_mb' megabytes disponibles.
    Si ninguna cumple, devuelve None.
    """
    try:
        logger.debug(f"Explorando dispositivos en {MEDIA_BASE_PATH}")
        candidates = [os.path.join(MEDIA_BASE_PATH, d) for d in os.listdir(MEDIA_BASE_PATH)]
        for path in candidates:
            logger.debug(f"Verificando dispositivo: {path}")
            if os.path.ismount(path) and os.access(path, os.W_OK):
                free_mb = shutil.disk_usage(path).free // (1024 * 1024)
                logger.debug(f"Espacio libre en {path}: {free_mb} MB")
                if free_mb >= min_free_mb:
                    logger.info(f"💾 USB válida detectada en {path} - {free_mb} MB libres")
                    return path
                else:
                    logger.warning(f"⚠️ Espacio insuficiente en {path} ({free_mb} MB)")
    except Exception as e:
        logger.warning(f"No se pudo explorar {MEDIA_BASE_PATH}: {e}")
    return None

def has_enough_space(path, min_mb=MIN_FREE_MB):
    """Verifica si el dispositivo tiene al menos 'min_mb' megabytes libres."""
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)
        logger.debug(f"Espacio libre en {path}: {free_mb} MB")
        return free_mb >= min_mb
    except Exception as e:
        logger.error(f"No se pudo verificar el espacio en {path}: {e}")
        return False

def get_storage_base():
    """Devuelve el directorio base de almacenamiento (USB o respaldo local)."""
    usb_path = find_mounted_usb()
    if usb_path and has_enough_space(usb_path):
        free_gb = shutil.disk_usage(usb_path).free / (1024 ** 3)
        logger.info(f"✅ Usando almacenamiento USB ({usb_path}) - Espacio libre: {free_gb:.2f} GB")
        return usb_path
    else:
        logger.warning("⚠️ No se detectó USB montada con espacio suficiente. Usando respaldo interno.")
        return INTERNAL_BACKUP_DIR

def get_dta_path(date_str):
    """Construye y asegura la ruta para guardar datos de lluvia según la fecha."""
    year, month, day = date_str.split('-')
    base = get_storage_base()
    path = os.path.join(base, "DTA", year, month, day)
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Ruta de almacenamiento creada/verificada: {path}")
    except Exception as e:
        logger.error(f"No se pudo crear la ruta de almacenamiento: {path} -> {e}")
        raise
    return path

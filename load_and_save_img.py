import os

from PIL import Image

def load_image(path: str) -> Image.Image:
    """
    Загружает изображение из файла.

    Args:
        path (str): Путь к изображению.

    Returns:
        Image.Image: Загруженное изображение.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Файл изображения не найден: {path}")
    try:
        image = Image.open(path)
        return image.convert("RGB")  # Убедимся, что у нас RGB
    except Exception as e:
        raise IOError(f"Не удалось загрузить изображение: {e}")


def save_image(image: Image.Image, path: str) -> None:
    """
    Сохраняет изображение в файл.

    Args:
        image (Image.Image): Изображение для сохранения.
        path (str): Путь для сохранения.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.save(path)
    except Exception as e:
        raise IOError(f"Не удалось сохранить изображение: {e}")

from PIL import Image
from typing import Tuple
import matplotlib.pyplot as plt

def pixelate_image(image: Image.Image, pixel_size: int) -> Image.Image:
    """
    Преобразует изображение в пиксель-арт.

    Args:
        image (Image.Image): Исходное изображение.
        pixel_size (int): Размер пикселя (сторона квадрата, усредняющего цвет).

    Returns:
        Image.Image: Пиксель-арт изображение.
    """
    if pixel_size <= 0:
        raise ValueError("pixel_size должен быть положительным целым числом")

    width, height = image.size
    # Уменьшаем изображение до размера сетки пикселей
    small_width = width // pixel_size
    small_height = height // pixel_size

    if small_width == 0 or small_height == 0:
        raise ValueError("pixel_size слишком велик для размера изображения")

    # Уменьшаем изображение с усреднением цветов
    resized = image.resize((small_width, small_height), Image.Resampling.NEAREST)
    # Увеличиваем обратно до исходного размера, получая пиксельный эффект
    pixelated = resized.resize((width, height), Image.Resampling.NEAREST)
    return pixelated


def get_image_size(image: Image.Image) -> Tuple[int, int]:
    """
    Возвращает размеры изображения.

    Args:
        image (Image.Image): Изображение.

    Returns:
        Tuple[int, int]: Ширина и высота изображения.
    """
    return image.size


def visualize_results(original: Image.Image, result: Image.Image) -> None:
    """
    Визуализирует исходное и результирующее изображения.

    Args:
        original (Image.Image): Исходное изображение.
        result (Image.Image): Результирующее изображение.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(original)
    axes[0].set_title("Исходное изображение")
    axes[0].axis('off')
    axes[1].imshow(result)
    axes[1].set_title("Пиксель-арт")
    axes[1].axis('off')
    plt.tight_layout()
    plt.show()
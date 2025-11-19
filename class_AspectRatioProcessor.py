from typing import List, Dict, Optional
from PIL import Image
import pandas as pd


def compute_aspect_ratio(image_path: str) -> Optional[float]:
    """
    Вычисляет отношение сторон (ширина / высота) изображения.

    Args:
        image_path (str): Путь к изображению.

    Returns:
        Optional[float]: Отношение сторон или None, если ошибка.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if height == 0:
                return float('inf')
            return width / height
    except Exception:
        return None


def assign_aspect_ratio_range(aspect_ratio: Optional[float], bins: List[float]) -> str:
    """
    Присваивает диапазон для заданного отношения сторон.

    Args:
        aspect_ratio (Optional[float]): Отношение сторон.
        bins (List[float]): Список границ диапазонов (например, [0.0, 1.0, 2.0]).

    Returns:
        str: Диапазон в формате "low-high" или "low+".
    """
    if aspect_ratio is None:
        return "invalid"
    for i in range(len(bins) - 1):
        low = bins[i]
        high = bins[i + 1]
        if low <= aspect_ratio < high:
            if high == float('inf'):
                return f"{low}+"
            else:
                return f"{low}-{high}"
    return "unknown"


class AspectRatioProcessor:
    """
    Класс для обработки отношений сторон изображений и добавления колонки в DataFrame.
    """
    def __init__(self, bins: List[float]):
        """
        Инициализирует процессор с заданными диапазонами.

        Args:
            bins (List[float]): Список границ диапазонов.
        """
        self.bins = bins

    def process_dataframe(self, csv_path: str) -> pd.DataFrame:
        """
        Загружает CSV и добавляет колонки с отношением сторон и диапазоном.

        Args:
            csv_path (str): Путь к CSV-файлу.

        Returns:
            pd.DataFrame: Обновлённый DataFrame.
        """
        df = pd.read_csv(csv_path)
        if "absolute_path" not in df.columns:
            raise ValueError("CSV должен содержать колонку 'absolute_path'")

        df["aspect_ratio"] = df["absolute_path"].apply(compute_aspect_ratio)
        df["aspect_ratio_range"] = df["aspect_ratio"].apply(
            lambda ar: assign_aspect_ratio_range(ar, self.bins)
        )
        return df


def sort_by_aspect_ratio_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Сортирует DataFrame по диапазону отношения сторон.

    Args:
        df (pd.DataFrame): DataFrame с колонкой 'aspect_ratio_range'.

    Returns:
        pd.DataFrame: Отсортированный DataFrame.
    """
    bins = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float('inf')]
    range_order: Dict[str, int] = {}
    for i in range(len(bins) - 1):
        low = bins[i]
        high = bins[i + 1]
        if high == float('inf'):
            key = f"{low}+"
        else:
            key = f"{low}-{high}"
        range_order[key] = i
    range_order["invalid"] = -1
    range_order["unknown"] = 999

    df["sort_key"] = df["aspect_ratio_range"].map(range_order)
    df_sorted = df.sort_values("sort_key").drop(columns=["sort_key"])
    return df_sorted
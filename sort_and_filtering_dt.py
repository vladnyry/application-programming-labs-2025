import pandas as pd
from typing import Dict


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

def filter_by_aspect_ratio_range(df: pd.DataFrame, target_range: str) -> pd.DataFrame:
    """
    Фильтрует DataFrame по заданному диапазону отношения сторон.

    Args:
        df (pd.DataFrame): Исходный DataFrame.
        target_range (str): Целевой диапазон (например, '1.0-1.5').

    Returns:
        pd.DataFrame: Отфильтрованный DataFrame.
    """
    return df[df["aspect_ratio_range"] == target_range].copy()
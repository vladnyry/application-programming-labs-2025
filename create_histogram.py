import pandas as pd
import matplotlib.pyplot as plt


def plot_aspect_ratio_histogram(df: pd.DataFrame, output_image_path: str) -> None:
    """
    Строит и сохраняет гистограмму распределения по диапазонам отношения сторон.

    Args:
        df (pd.DataFrame): DataFrame с колонкой 'aspect_ratio_range'.
        output_image_path (str): Путь для сохранения изображения.
    """
    bins = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float('inf')]
    labels = []
    for i in range(len(bins) - 1):
        low = bins[i]
        high = bins[i + 1]
        if high == float('inf'):
            labels.append(f"{low}+")
        else:
            labels.append(f"{low}-{high}")

    counts = []
    for label in labels:
        counts.append((df["aspect_ratio_range"] == label).sum())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color='skyblue', edgecolor='black')
    plt.xlabel("Диапазон отношения сторон (ширина / высота)")
    plt.ylabel("Количество изображений")
    plt.title("Гистограмма распределения отношения сторон изображений")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()
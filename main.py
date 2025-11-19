import argparse

from class_AspectRatioProcessor import *
from sort_and_filtering_dt import *
from create_histogram import *

def parser() -> argparse.Namespace:
    """
       Парсит аргументы командной строки.

       Returns:
           argparse.Namespace: Объект с аргументами.
       """
    parser = argparse.ArgumentParser(
        description="Анализ отношения сторон изображений из CSV-аннотации."
    )
    parser.add_argument(
        "--annotation_file",
        type=str,
        required=True,
        help="Путь к CSV-файлу с аннотацией (absolute_path, relative_path)",
    )
    parser.add_argument(
        "--output_csv",
        type=str,
        default="aspect_ratio_annotation.csv",
        help="Путь для сохранения обновлённого CSV",
    )
    parser.add_argument(
        "--output_plot",
        type=str,
        default="aspect_ratio_histogram.png",
        help="Путь для сохранения гистограммы",
    )
    return parser.parse_args()


def main() -> None:

    try:
        args = parser()

        # Инициализация процессора
        bins = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, float('inf')]
        processor = AspectRatioProcessor(bins)

        # Обработка
        df = processor.process_dataframe(args.annotation_file)

        # Сохранение CSV
        df.to_csv(args.output_csv, index=False, encoding="utf-8")
        print(f"Обновлённый DataFrame сохранён в: {args.output_csv}")

        # Сортировка
        df_sorted = sort_by_aspect_ratio_range(df)
        print("\nПример отсортированных данных (первые 5 строк):")
        print(df_sorted[["absolute_path", "aspect_ratio", "aspect_ratio_range"]].head())

        # Фильтрация
        square_images = filter_by_aspect_ratio_range(df, "1.0-1.5")
        print(f"\nКоличество изображений с соотношением 1.0-1.5: {len(square_images)}")

        # Гистограмма
        plot_aspect_ratio_histogram(df, args.output_plot)

    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден — {e}")
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()
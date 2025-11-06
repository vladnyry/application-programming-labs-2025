import argparse
import collections.abc
import csv
import threading
import time
import os
from typing import List, Tuple, Iterator
from icrawler.builtin import GoogleImageCrawler


"""
f для скачивания изображением по времени
"""


def validate_positive_int(value: int, name: str) -> None:
    """
    Проверяет, что значение является положительным целым числом.

    Args:
        value (int): Проверяемое значение.
        name (str): Название параметра для сообщения об ошибке.

    Raises:
        ValueError: Если значение <= 0.
    """
    if value <= 0:
        raise ValueError(f"Параметр '{name}' должен быть положительным, получено: {value}")


def _count_files_in_directory(directory: str) -> int:
    """
    Подсчитывает количество файлов в указанной директории.

    Args:
        directory (str): Путь к директории.

    Returns:
        int: Количество файлов.

    Raises:
        OSError: Если не удалось прочитать директорию.
    """
    try:
        return len([
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ])
    except OSError as e:
        raise OSError(f"Не удалось прочитать директорию '{directory}': {e}") from e


def download_img(
    keyword: str,
    out_dir: str,
    min_img: int = 50,
    dur: int = 60
) -> Tuple[int, float]:
    """
    Скачивает изображения по заданному ключевому слову с ограничением
    по минимальному количеству изображений или максимальному времени.

    Args:
        keyword (str): Ключевое слово для поиска изображений.
        out_dir (str): Директория для сохранения изображений.
        min_img (int): Минимальное количество изображений (по умолчанию 50).
        dur (int): Максимальное время скачивания в секундах (по умолчанию 60).

    Returns:
        Tuple[int, float]: Кортеж из (фактическое количество изображений, затраченное время в секундах).

    Raises:
        ValueError: Если min_img или dur <= 0.
        OSError: Если не удалось создать директорию или подсчитать файлы.
    """
    validate_positive_int(min_img, "min_img")
    validate_positive_int(dur, "dur")

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        raise OSError(f"Не удалось создать директорию '{out_dir}'") from e

    def crawler_task() -> None:
        """Задача для фонового потока: запуск краулера."""
        crawler = GoogleImageCrawler(storage={"root_dir": out_dir})
        crawler.crawl(keyword=keyword, max_num=10000)

    thread = threading.Thread(target=crawler_task)
    thread.daemon = True
    thread.start()

    start_time = time.time()
    print(f"Начало скачивания изображений по ключевому слову '{keyword}'...")
    print(f"Ограничения: минимум {min_img} изображений или максимум {dur} секунд.")

    while thread.is_alive():
        try:
            current_count = _count_files_in_directory(out_dir)
        except OSError:
            current_count = 0

        elapsed = time.time() - start_time

        if current_count >= min_img:
            print(f"Достигнуто требуемое количество изображений: {min_img}")
            break

        if elapsed >= dur:
            print("Время вышло. Остановка скачивания.")
            break

        time.sleep(0.5)

    total_time = time.time() - start_time
    try:
        final_count = _count_files_in_directory(out_dir)
    except OSError:
        final_count = 0

    return final_count, total_time



def create_csv(out_dir: str, path_to_csv: str) -> None:
    """
    Создаёт CSV-файл с абсолютными и относительными путями к файлам в директории.

    Args:
        out_dir (str): Директория с изображениями.
        path_to_csv (str): Путь к создаваемому CSV-файлу.

    Raises:
        OSError: Если не удалось прочитать директорию или записать CSV.
    """
    try:
        files = [
            f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))
        ]
    except OSError as e:
        raise OSError("беда, не смогли прочитать директорию")

    try:
        with open(path_to_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["absolute_path", "relative_path"])
            for filename in files:
                full_path = os.path.abspath(os.path.join(out_dir, filename))
                rel_path = os.path.relpath(full_path, start=os.getcwd())
                writer.writerow([full_path, rel_path])
    except OSError as e:
        raise OSError("не удалось записать в csv")


class ImgPathIterator:
    def __init__(self, source: str) -> None:
        """
        Инициализирует итератор.

        Args:
            source (str): Путь к CSV-файлу (.csv) или директории.

        Raises:
            ValueError: Если source не является CSV-файлом или директорией.
            OSError: При ошибках чтения файла или директории.
        """
        self.paths: list[str] = []
        self._index: int = 0

        if os.path.isfile(source) and source.endswith(".csv"):
            try:
                with open(source, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    if "absolute_path" not in reader.fieldnames:
                        raise ValueError("CSV должен содержать колонку 'absolute_path'")
                    self.paths = [row["absolute_path"] for row in reader]
            except (OSError, csv.Error) as e:
                raise OSError(f"Ошибка чтения CSV-файла '{source}': {e}")

        elif os.path.isdir(source):
            try:
                self.paths = [
                    os.path.abspath(os.path.join(source, f))
                    for f in os.listdir(source)
                    if os.path.isfile(os.path.join(source, f))
                ]
            except OSError as e:
                raise OSError(f"Ошибка чтения директории '{source}': {e}")

        else:
            raise ValueError(
                "Параметр 'source' должен быть либо CSV-файлом с расширением .csv, "
                "либо существующей директорией."
            )

    def __iter__(self) -> collections.abc.Iterable[str]:
        """Возвращает итератор по путям."""
        return iter(self.paths)

    def __len__(self) -> int:
        """Возвращает количество путей."""
        return len(self.paths)

    def __next__(self) -> str:
        """Возвращает следующий путь или вызывает StopIteration."""
        if self._index < len(self.paths):
            path = self.paths[self._index]
            self._index += 1
            return path
        raise StopIteration


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Скачивание изображений по ключевому слову с аннотацией и итератором."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Путь к папке для сохранения изображений",
    )
    parser.add_argument(
        "--annotation_file",
        type=str,
        required=True,
        help="Путь к CSV-файлу аннотации",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="pig",
        help="Ключевое слово для поиска изображений (по умолчанию: 'pig')",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Максимальное время скачивания в секундах (по умолчанию: 60)",
    )
    parser.add_argument(
        "--min_images",
        type=int,
        default=50,
        help="Минимальное количество изображений (по умолчанию: 50)",
    )

    try:
        args = parser.parse_args()

        # Скачивание
        count, elapsed = download_img(
            keyword=args.keyword,
            out_dir=args.output_dir,
            min_img=args.min_images,
            dur=args.duration
        )

        print(f"\nСкачано изображений: {count}")
        print(f"Затрачено времени: {elapsed:.2f} секунд")

        # Создание CSV
        create_csv(args.output_dir, args.annotation_file)
        print(f"\nАннотация сохранена в: {args.annotation_file}")

        # Демонстрация итератора
        print("\nПример использования итератора (первые 4 пути):")
        try:
            iterator = ImgPathIterator(args.annotation_file)
            for i in range(4):
                try:
                    path = next(iterator)
                    print(f"{i + 1}: {path}")
                except StopIteration:
                    print("(Больше путей нет)")
                    break
        except (OSError, ValueError) as e:
            print(f"Ошибка при использовании итератора: {e}")

    except (ValueError, OSError, KeyboardInterrupt) as e:
        print(f"Ошибка: {e}")
        exit(1)


if __name__ == "__main__":
    main()
import argparse
from processing_img import *
from load_and_save_img import *

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Преобразование изображения в пиксель-арт."
    )
    parser.add_argument(
        "--input_path",
        type=str,
        required=True,
        help="Путь к исходному изображению"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Путь для сохранения результата"
    )
    parser.add_argument(
        "--pixel_size",
        type=int,
        default=10,
        help="Размер пикселя для пиксель-арта (по умолчанию 10)"
    )

    try:
        args = parser.parse_args()

        # Загрузка изображения
        image = load_image(args.input_path)
        width, height = get_image_size(image)
        print(f"Размер исходного изображения: {width}x{height}")

        # Преобразование в пиксель-арт
        pixelated = pixelate_image(image, args.pixel_size)

        # Визуализация
        visualize_results(image, pixelated)

        # Сохранение результата
        save_image(pixelated, args.output_path)
        print(f"Результат сохранен в: {args.output_path}")

    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Ошибка: {e}")
        exit(1)


if __name__ == "__main__":
    main()
import typer

from nnix_xml_processor.zip_maker import ZipFilesMaker
from nnix_xml_processor.zip_reader import ZipReader

app = typer.Typer()


@app.command(name='create')
def make_zip(
    target: str = typer.Option(default='./zips', help='Директория выгрузки данных'),
    count_zip: int = typer.Option(default=50, min=1, max=5000, help='Количество zip файлов'),
    count_xml_in_zip: int = typer.Option(default=50, min=1, max=5000, help='Количество zip файлов'),
    random_string_len: int = typer.Option(default=50, help='Длина случайно генерируемой строки в object'),
    object_max_size: int = typer.Option(default=10, help='Максимальное количество объектов в objects'),
    max_levels: int = typer.Option(default=100, help='Максимальное число генерируемого уровня'),
) -> None:
    """
    Формирование файла
    """
    zip_maker = ZipFilesMaker(target, random_string_len, object_max_size, max_levels)
    zip_maker.make_zip_files(count=count_zip, count_xml_files=count_xml_in_zip)


@app.command(name='parse')
def read_xml(
    target: str = typer.Option(default='./zips', help='Директория с файлами zip'),
    levels_filename: str = typer.Option(default='levels.csv', help='Файл выгрузки уровней'),
    objects_filename: str = typer.Option(default='objects.csv', help='Файл выгрузки объектов'),
) -> None:
    """Парсинг xml из zip"""
    zip_reader = ZipReader(target)
    zip_reader.execute(levels_filename, objects_filename)


if __name__ == '__main__':
    app()

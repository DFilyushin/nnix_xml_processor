from os import chdir
from random import choices, randint
from string import ascii_uppercase
from uuid import uuid4
from zipfile import ZIP_BZIP2, ZipFile


class ZipFilesMaker:
    """
    Генерация zip-файлов
    """

    def __init__(
        self, target_dir: str, random_string_len: int = 50, object_tag_size: int = 10, random_levels_high: int = 100
    ) -> None:
        self._object_tag_size = object_tag_size
        self._target_dir = target_dir
        self._random_string_len = random_string_len
        self._random_levels_high = random_levels_high

    def _generate_random_filename(self, ext: str) -> str:
        """
        Генерация случайного имени файла
        :param ext: Расширение файла
        :return: Случайное имя файла
        """
        return f'{uuid4().hex}.{ext}'

    def _generate_random_string(self) -> str:
        """
        Генерация случайной строки
        :return: Случайная строка длины, определённой в классе
        """
        return ''.join(choices(ascii_uppercase, k=self._random_string_len))

    def _generate_xml_file_content(self) -> str:
        """
        Генерация xml-файла с условно случайным наполнением
        :return: Строка xml-файла
        """
        content = list()
        content.append('<root>')
        content.append(f'<var name="id" value="{uuid4().hex}"/>')
        content.append(f'<var name="level" value="{randint(1, self._random_levels_high)}"/>')
        content.append('<objects>')
        for _ in range(randint(1, self._object_tag_size)):
            content.append(f'<object name="{self._generate_random_string()}"/>')
        content.append('</objects>')
        content.append('</root>')

        return '\n'.join(content)

    def make_zip_file(self, count_xml_files: int = 100) -> None:
        """
        Создание zip-файла
        :param count_xml_files: Количество xml файлов внутри zip
        :return: None
        """
        with ZipFile(self._generate_random_filename('zip'), 'w', compression=ZIP_BZIP2) as zf:
            for _ in range(count_xml_files):
                content = self._generate_xml_file_content()
                zf.writestr(self._generate_random_filename('xml'), content)

    def make_zip_files(self, count: int = 50, count_xml_files: int = 100) -> None:
        """
        Создание zip-файлов
        :param count: Количество генерируемых zip файлов
        :param count_xml_files: Количество xml файлов внутри zip
        :return: None
        """
        try:
            chdir(self._target_dir)
        except FileNotFoundError:
            print(f'Directory {self._target_dir} not found!')
            return

        for _ in range(count):
            self.make_zip_file(count_xml_files)

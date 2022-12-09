import multiprocessing as mp
import time
import xml.dom.minidom
from os import listdir, path
from queue import Queue
from zipfile import ZipFile


class ZipProcessor:

    @staticmethod
    def get_objects_from_dom(element) -> tuple[str, int, list]:
        tags = element.getElementsByTagName('var')

        t = {}
        for tag in tags:
            t[tag.attributes['name'].value] = tag.attributes['value'].value

        uid = t['id']
        level = t['level']

        objects_element = element.getElementsByTagName('object')
        objects = [elem.attributes["name"].value for elem in objects_element]

        return uid, level, objects

    @staticmethod
    def runner(zip_filename: str, levels_queue: Queue, objects_queue: Queue) -> None:
        """
        Обработка zip-файла
        :param zip_filename: имя файла
        :param levels_queue: очередь для передачи уровней
        :param objects_queue: очередь для передачи объектов
        :return: None
        """
        start = time.time()
        with ZipFile(zip_filename, 'r') as zip_file:
            filenames = zip_file.namelist()
            for filename in filenames:
                with zip_file.open(filename) as arc_file:
                    try:
                        doc = xml.dom.minidom.parse(arc_file)
                        uid, level, objects = ZipProcessor.get_objects_from_dom(doc)

                        levels_queue.put(f'{uid},{level}')

                        for elem in objects:
                            object_line = f'{uid},{elem}'
                            objects_queue.put(object_line)
                    except Exception as exc:
                        print(f'Skipped file {filename}. Details: {str(exc)}')

        elapsed = time.time() - start
        print(f'Processing file: {zip_filename} by {elapsed}')


class ProcessObserver:
    """
    Обработчик очереди для записи в выходной файл
    """
    @staticmethod
    def runner(queue: Queue, output_filename: str) -> None:
        """
        Обработчик очереди
        :param queue: очередь для прослушивания
        :param output_filename: выходной файл
        :return: None
        """
        with open(output_filename, 'w') as f:
            while True:
                message = queue.get()
                if message == 'stop':
                    break
                f.write(message + '\n')
                f.flush()
                queue.task_done()


class ZipReader:
    """Класс чтения zip-файлов с последующим парсингом содержимого"""

    def __init__(self, target_dir: str) -> None:
        self._target_dir = target_dir
        self.manager = mp.Manager()
        self.pool = mp.Pool(mp.cpu_count() + 2)
        self.levels_queue = self.manager.Queue()
        self.objects_queue = self.manager.Queue()

    def execute(self, output_levels_filename: str = 'levels.csv', output_objects_filename: str = 'objects.csv') -> None:
        """
        Создание воркеров для обработки директорий
        :param output_levels_filename: имя файла для выгрузки уровней
        :param output_objects_filename: имя файла для выгрузки объектов
        :return:
        """
        self.pool.apply_async(
            ProcessObserver.runner,
            (
                self.levels_queue,
                output_levels_filename,
            ),
        )
        self.pool.apply_async(
            ProcessObserver.runner,
            (
                self.objects_queue,
                output_objects_filename,
            ),
        )

        jobs = []
        zip_files_in_target = []
        for filename in listdir(self._target_dir):
            filepath = path.join(self._target_dir, filename)
            if path.isfile(filepath):
                zip_files_in_target.append(filepath)

        for filename in zip_files_in_target:
            job = self.pool.apply_async(ZipProcessor.runner, (filename, self.levels_queue, self.objects_queue))
            jobs.append(job)

        for job in jobs:
            job.get()

        self.objects_queue.put('stop')
        self.levels_queue.put('stop')

        self.pool.close()
        self.pool.join()

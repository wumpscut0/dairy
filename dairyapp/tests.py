from platform import system
from subprocess import Popen, run, PIPE
from typing import Dict, Tuple, Iterable, List

from django.test import TestCase


def up_to_date_fixtures(map_: Dict[Tuple[str, str], Iterable]) -> List[str]:
    """
    Обновляет фикстуры данных для заданных моделей и источников.

    param:
    map_ (Dict[Tuple[str, str], Iterable[str]]): Словарь, где ключами являются кортежи из двух строк:
        - model_source: строка, представляющая источник модели (например, имя приложения).
        - test_app: строка, представляющая тестовое приложение, куда будут сохраняться фикстуры.
      Значениями являются итерации строк, каждая из которых представляет имя модели.

    return:
    List[str]: Список имён созданных файлов фикстур.
    """
    processes = []
    fixtures = []
    for source, models in map_.items():
        model_source, test_app = source
        for model in models:
            name = f"{model.lower()}.json"
            fixtures.append(name)
            p = Popen(
                f"python manage.py dumpdata {model_source}.{model.capitalize()} > ./{test_app}/fixtures/{name}",
                shell=True,
            )
            processes.append(p)
    for p in processes:
        p.wait(1)

    if system() == "Windows":
        result = run("chcp", shell=True, stdout=PIPE, text=True, timeout=1)
        code_encoding = result.stdout.split(":")[1].strip()
        if code_encoding != "65001":
            for f in fixtures:
                with open(f, "r", encoding=f"cp{code_encoding}") as old_file:
                    dump = old_file.read()
                with open(f, "w", encoding="utf-8") as new_file:
                    new_file.write(dump)

    print(fixtures)
    return fixtures

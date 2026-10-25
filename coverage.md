```
[run]
source = GPT_tasks   * проходится по указанной папке с модулями
omit =
    */venv/*
    */.venv/*
    */__init__.py
    */test_*.py

[report]
exclude_lines =
    pragma: no cover
    if __name__ == .__main__.:
```

* uv run coverage erase - удаляет старые данные о покрытии
* uv run coverage run -m pytest - новые данные о покрытии/запуск с покрытием
* uv run coverage -m  - вывод покрытия в консоль -m показывает не покрытые строки
* uv run coverage html - отчет в html файл
* uv run coverage debug config - просмотр параметров настроек
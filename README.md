# Blender Render Queue

🇷🇺 [Русский](#русский) · 🇬🇧 [English](#english)

---

## Русский

Простая программа с окном для Windows (работает и на macOS/Linux при запуске через Python): выбираешь несколько `.blend` проектов, нажимаешь **Старт** и идёшь спать. Проекты рендерятся по очереди, а в конце компьютер можно автоматически выключить.

### Возможности

- Очередь из любого числа `.blend` файлов, порядок можно менять
- Рендер анимации (весь диапазон кадров) или одного кадра
- Автоматический поиск установленного Blender
- Живой лог рендера прямо в окне
- Если один проект упал с ошибкой, остальные всё равно отрендерятся
- Кнопка **Остановить всё**: прерывает текущий рендер и отменяет очередь
- Автовыключение компьютера в конце с отсчётом 60 секунд (его можно отменить)

### Запуск

**Вариант 1. Через Python** (нужен Python 3, никаких дополнительных библиотек):

```
python render_queue.py
```

**Вариант 2. Собрать свой `.exe`** (Windows):

1. Установи Python с [python.org](https://www.python.org/) и отметь галочку **Add Python to PATH**
2. Дважды кликни по `build_exe.bat`
3. Готовый файл появится в `dist\BlenderRenderQueue.exe`

### Как пользоваться

1. Проверь, что путь к Blender указан верно (обычно находится сам)
2. Нажми **Добавить .blend…** и выбери проекты
3. Выбери, что рендерить: анимацию или один кадр
4. Оставь или сними галочку **Выключить компьютер в конце**
5. Нажми **▶ Старт**

### Важно

- Настройки рендера (движок, разрешение, диапазон кадров, папка и формат вывода) берутся **из самих `.blend` файлов**. Заранее проверь, что в *Output Properties* указана папка для сохранения.
- Для анимации лучше использовать PNG-последовательность, а не видеоформат: если что-то упадёт, готовые кадры сохранятся.
- Отключи спящий режим на время рендера и не закрывай окно программы.
- Перед первым ночным рендером проверь всё на коротком тесте (2–3 кадра).
- Blender запускается в фоновом режиме (`blender -b`), без интерфейса.

### Лицензия

MIT. См. файл [LICENSE](LICENSE).

---

## English

A simple windowed tool for Windows (also works on macOS/Linux when run via Python): pick several `.blend` projects, hit **Start** and go to sleep. The projects are rendered one after another, and the computer can shut itself down at the end.

### Features

- A queue of any number of `.blend` files, with reorderable items
- Render an animation (full frame range) or a single frame
- Automatic detection of an installed Blender
- Live render log inside the window
- If one project fails, the rest are still rendered
- **Stop all** button: aborts the current render and cancels the queue
- Optional automatic shutdown at the end with a 60-second countdown (cancellable)

### Running

**Option 1. With Python** (Python 3 required, no extra libraries):

```
python render_queue.py
```

**Option 2. Build your own `.exe`** (Windows):

1. Install Python from [python.org](https://www.python.org/) and tick **Add Python to PATH**
2. Double-click `build_exe.bat`
3. Your file will appear at `dist\BlenderRenderQueue.exe`

### Usage

1. Make sure the Blender path is correct (it is usually detected automatically)
2. Click **Добавить .blend…** (Add .blend) and choose your projects
3. Choose what to render: animation or a single frame
4. Keep or clear the **shutdown at the end** checkbox
5. Click **▶ Старт** (Start)

### Notes

- Render settings (engine, resolution, frame range, output folder and format) are taken **from the `.blend` files themselves**. Make sure an output folder is set in *Output Properties* beforehand.
- For animations, prefer an image sequence (e.g. PNG) over a video format: if something crashes, the finished frames are kept.
- Disable sleep mode while rendering and do not close the program window.
- Before your first overnight run, test everything on a short render (2–3 frames).
- Blender runs in background mode (`blender -b`), without its UI.

### License

MIT. See the [LICENSE](LICENSE) file.

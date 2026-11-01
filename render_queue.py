#!/usr/bin/env python3
"""
Очередь рендера Blender: выбери .blend файлы, нажми "Старт" и иди спать.
Рендерит проекты по очереди, а в конце (по желанию) выключает компьютер.

Запуск:  python render_queue.py
Нужен только Python 3 (tkinter входит в стандартную установку).
"""

import glob
import os
import platform
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

SYSTEM = platform.system()


def find_blender():
    """Пытается найти blender автоматически."""
    if SYSTEM == "Windows":
        paths = glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe")
        if paths:
            return sorted(paths)[-1]  # самая новая версия
    elif SYSTEM == "Darwin":
        p = "/Applications/Blender.app/Contents/MacOS/Blender"
        if os.path.exists(p):
            return p
    found = shutil.which("blender")
    return found or ""


def shutdown_now():
    if SYSTEM == "Windows":
        subprocess.Popen(["shutdown", "/s", "/t", "0"])
    elif SYSTEM == "Darwin":
        subprocess.Popen(["osascript", "-e", 'tell app "System Events" to shut down'])
    else:
        subprocess.Popen(["systemctl", "poweroff"])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blender — очередь рендера")
        self.geometry("760x620")
        self.cancel_flag = False
        self.proc = None
        self.running = False
        self.countdown_job = None

        # --- путь к Blender ---
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Blender:").pack(side="left")
        self.blender_var = tk.StringVar(value=find_blender())
        ttk.Entry(top, textvariable=self.blender_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="Обзор…", command=self.pick_blender).pack(side="left")

        # --- список проектов ---
        mid = ttk.Frame(self, padding=(8, 0))
        mid.pack(fill="both", expand=False)
        self.listbox = tk.Listbox(mid, height=8, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        btns = ttk.Frame(mid)
        btns.pack(side="left", padx=6, fill="y")
        for text, cmd in [
            ("Добавить .blend…", self.add_files),
            ("Убрать", self.remove_selected),
            ("Вверх", lambda: self.move(-1)),
            ("Вниз", lambda: self.move(1)),
        ]:
            ttk.Button(btns, text=text, command=cmd).pack(fill="x", pady=2)

        # --- опции ---
        opt = ttk.Frame(self, padding=8)
        opt.pack(fill="x")
        ttk.Label(opt, text="Что рендерить:").pack(side="left")
        self.mode_var = tk.StringVar(value="Анимацию (весь диапазон кадров)")
        ttk.Combobox(
            opt,
            textvariable=self.mode_var,
            state="readonly",
            width=34,
            values=["Анимацию (весь диапазон кадров)", "Один кадр (текущий в файле)"],
        ).pack(side="left", padx=6)
        self.shutdown_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Выключить компьютер в конце", variable=self.shutdown_var).pack(side="left", padx=12)

        # --- кнопки управления ---
        ctl = ttk.Frame(self, padding=(8, 0))
        ctl.pack(fill="x")
        self.start_btn = ttk.Button(ctl, text="▶ Старт", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(ctl, text="■ Остановить всё", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        self.status_var = tk.StringVar(value="Ожидание")
        ttk.Label(ctl, textvariable=self.status_var).pack(side="left", padx=12)

        # --- лог ---
        self.log = scrolledtext.ScrolledText(self, height=18, state="disabled", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI helpers ----------
    def write(self, text):
        def _w():
            self.log.configure(state="normal")
            self.log.insert("end", text)
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _w)

    def set_status(self, text):
        self.after(0, lambda: self.status_var.set(text))

    def pick_blender(self):
        p = filedialog.askopenfilename(title="Укажи blender.exe / blender")
        if p:
            self.blender_var.set(p)

    def add_files(self):
        files = filedialog.askopenfilenames(title="Выбери .blend проекты", filetypes=[("Blender", "*.blend")])
        existing = set(self.listbox.get(0, "end"))
        for f in files:
            if f not in existing:
                self.listbox.insert("end", f)

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)

    def move(self, d):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        i = sel[0]
        j = i + d
        if 0 <= j < self.listbox.size():
            item = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(j, item)
            self.listbox.selection_set(j)

    # ---------- логика ----------
    def start(self):
        blender = self.blender_var.get().strip()
        files = list(self.listbox.get(0, "end"))
        if not blender or not os.path.exists(blender):
            messagebox.showerror("Ошибка", "Не найден Blender. Укажи путь к blender.exe.")
            return
        if not files:
            messagebox.showerror("Ошибка", "Добавь хотя бы один .blend файл.")
            return
        self.cancel_flag = False
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self.worker, args=(blender, files), daemon=True).start()

    def stop(self):
        self.cancel_flag = True
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        if self.countdown_job:
            self.after_cancel(self.countdown_job)
            self.countdown_job = None
            self.write("\nВыключение отменено.\n")
            self.set_status("Отменено")

    def worker(self, blender, files):
        animation = self.mode_var.get().startswith("Анимацию")
        total = len(files)
        results = []
        for n, f in enumerate(files, 1):
            if self.cancel_flag:
                break
            self.set_status(f"Рендер {n}/{total}: {os.path.basename(f)}")
            self.write(f"\n===== [{n}/{total}] {f} =====\n")
            cmd = [blender, "-b", f, "-a"] if animation else [blender, "-b", f, "-f", "0"]
            if not animation:
                # -f 0 заменяем на "текущий кадр файла": используем скрипт-эквивалент
                cmd = [blender, "-b", f, "--python-expr",
                       "import bpy; bpy.ops.render.render(write_still=True)"]
            try:
                self.proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                )
                for line in self.proc.stdout:
                    self.write(line)
                code = self.proc.wait()
            except Exception as e:  # noqa: BLE001
                self.write(f"Не удалось запустить: {e}\n")
                code = -1
            ok = code == 0 and not self.cancel_flag
            results.append((f, ok))
            self.write(f"--> {'ГОТОВО' if ok else 'ОШИБКА / ПРЕРВАНО'} (код {code})\n")

        self.running = False
        self.after(0, self.finish, results)

    def finish(self, results):
        self.start_btn.configure(state="normal")
        ok_count = sum(1 for _, ok in results if ok)
        self.write(f"\n===== Итог: успешно {ok_count} из {len(results)} =====\n")
        for f, ok in results:
            self.write(f"  {'✔' if ok else '✘'} {os.path.basename(f)}\n")

        if self.cancel_flag:
            self.stop_btn.configure(state="disabled")
            self.set_status("Остановлено")
            return
        if self.shutdown_var.get():
            self.remaining = 60
            self.write("\nКомпьютер выключится через 60 секунд. Нажми «Остановить всё», чтобы отменить.\n")
            self.tick()
        else:
            self.stop_btn.configure(state="disabled")
            self.set_status("Всё готово")

    def tick(self):
        if self.remaining <= 0:
            self.write("Выключаюсь…\n")
            shutdown_now()
            return
        self.set_status(f"Выключение через {self.remaining} с")
        self.remaining -= 1
        self.countdown_job = self.after(1000, self.tick)

    def on_close(self):
        if self.running and not messagebox.askyesno("Выход", "Рендер ещё идёт. Всё равно закрыть?"):
            return
        self.cancel_flag = True
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading


class DanrexSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Danrex Sorter - Профессиональная сортировка файлов")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Устанавливаем иконку (опционально, если есть файл)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Переменные
        self.selected_folder = ""
        self.is_sorting = False

        # Категории файлов
        self.categories = {
            "🖼️ Изображения": ['.jpg', '.jpeg', '.jpe', '.jfif', '.jif', '.jp2', '.j2k', '.jpx', '.jpm', '.mj2',
                               '.png', '.apng', '.gif', '.bmp', '.dib', '.webp', '.svg', '.svgz', '.ico', '.tiff',
                               '.tif', '.heic', '.heif', '.avif', '.raw', '.cr2', '.cr3', '.nef', '.arw', '.orf',
                               '.rw2', '.dng', '.psd', '.psb', '.ai', '.eps', '.cdr', '.xcf', '.pcx', '.tga', '.icns',
                               '.hdr', '.exr', '.ppm', '.pgm', '.pbm', '.pnm'],

            "📄 Документы": ['.pdf', '.doc', '.docx', '.docm', '.dot', '.dotx', '.odt', '.rtf', '.txt', '.text',
                            '.md', '.markdown', '.csv', '.tsv', '.xls', '.xlsx', '.xlsm', '.xlt', '.xltx', '.ods',
                            '.ppt', '.pptx', '.pptm', '.pot', '.potx', '.odp', '.odg', '.pages', '.numbers', '.key',
                            '.tex', '.bib', '.log', '.ini', '.cfg', '.conf', '.yaml', '.yml', '.json', '.xml', '.html',
                            '.htm', '.xhtml', '.epub', '.mobi', '.azw', '.fb2', '.djvu', '.chm', '.wps', '.wpd'],

            "🎬 Видео": ['.mp4', '.m4v', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.f4v', '.webm', '.mpg', '.mpeg',
                        '.mpe', '.m2v', '.m4p', '.m4b', '.3gp', '.3g2', '.ogv', '.ogg', '.rm', '.rmvb', '.asf',
                        '.vob', '.ts', '.mts', '.m2ts', '.divx', '.xvid'],

            "🎵 Аудио": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.oga', '.wma', '.m4a', '.opus', '.aiff', '.aif',
                        '.ape', '.alac', '.ac3', '.dts', '.amr', '.mid', '.midi', '.mka', '.ra', '.au', '.pcm'],

            "🗜️ Архивы": ['.zip', '.zipx', '.rar', '.7z', '.tar', '.gz', '.gzip', '.bz2', '.bzip2', '.xz', '.lz',
                          '.lzma', '.z', '.cab', '.iso', '.dmg', '.tgz', '.tbz2', '.txz', '.tar.gz', '.tar.bz2',
                          '.tar.xz'],

            "⚙️ Программы и скрипты": ['.exe', '.msi', '.apk', '.app', '.bat', '.cmd', '.sh', '.ps1', '.py', '.js',
                                       '.ts', '.java', '.class', '.jar', '.c', '.cpp', '.h', '.hpp', '.cs', '.rb',
                                       '.go', '.rs', '.swift', '.kt', '.php', '.pl', '.r', '.lua', '.sql', '.ipynb'],

            "🔤 Шрифты": ['.ttf', '.otf', '.woff', '.woff2', '.eot', '.ttc', '.dfont', '.pfa', '.pfb'],

            "🗄️ Базы данных": ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.frm', '.ibd', '.myd', '.myi']
        }

        # Стилизуем приложение
        self.setup_styles()
        self.create_widgets()

        # Центрируем окно
        self.center_window()

    def setup_styles(self):
        """Настройка цветовой схемы и стилей"""
        # Цветовая схема
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4CAF50',
            'accent_hover': '#45a049',
            'button_bg': '#3c3c3c',
            'button_hover': '#4a4a4a',
            'entry_bg': '#3c3c3c',
            'progress_bg': '#555555'
        }

        self.root.configure(bg=self.colors['bg'])

        # Настройка стилей для ttk
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button_bg'], foreground=self.colors['fg'])
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='white')
        style.configure('TProgressbar', background=self.colors['accent'], troughcolor=self.colors['progress_bg'])

        # Настройка цветов для обычных кнопок tk
        self.button_style = {
            'bg': self.colors['button_bg'],
            'fg': self.colors['fg'],
            'activebackground': self.colors['button_hover'],
            'activeforeground': 'white',
            'font': ('Segoe UI', 10),
            'relief': tk.FLAT,
            'bd': 0,
            'padx': 20,
            'pady': 10
        }

    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Заголовок
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 30))

        title_label = tk.Label(title_frame, text="📁 Danrex Sorter",
                               font=('Segoe UI', 24, 'bold'),
                               bg=self.colors['bg'], fg=self.colors['accent'])
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="Профессиональная сортировка файлов по категориям",
                                  font=('Segoe UI', 10),
                                  bg=self.colors['bg'], fg=self.colors['fg'])
        subtitle_label.pack()

        # Блок выбора папки
        select_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        select_frame.pack(fill=tk.X, pady=(0, 20))

        self.select_btn = tk.Button(select_frame, text="📂 Выбрать папку",
                                    command=self.select_folder_threaded,
                                    cursor="hand2", **self.button_style)
        self.select_btn.pack()

        self.folder_label = tk.Label(select_frame, text="Папка не выбрана",
                                     font=('Segoe UI', 9),
                                     bg=self.colors['bg'], fg='#888888')
        self.folder_label.pack(pady=(10, 0))

        # Блок со статистикой
        stats_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief=tk.RIDGE, bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        self.stats_label = tk.Label(stats_frame, text="Статистика: ожидание выбора папки...",
                                    font=('Segoe UI', 9),
                                    bg=self.colors['bg'], fg=self.colors['fg'],
                                    wraplength=500, justify=tk.LEFT)
        self.stats_label.pack(padx=15, pady=15)

        # Прогресс-бар
        self.progress_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=400)
        self.progress_bar.pack()

        self.progress_label = tk.Label(self.progress_frame, text="",
                                       font=('Segoe UI', 8),
                                       bg=self.colors['bg'], fg='#888888')
        self.progress_label.pack(pady=(5, 0))

        # Кнопка сортировки
        self.sort_btn = tk.Button(main_frame, text="🚀 Начать сортировку",
                                  command=self.sort_files_threaded,
                                  state=tk.DISABLED, cursor="hand2",
                                  bg=self.colors['accent'], fg='white',
                                  activebackground=self.colors['accent_hover'],
                                  activeforeground='white',
                                  font=('Segoe UI', 12, 'bold'),
                                  relief=tk.FLAT, bd=0, padx=30, pady=12)
        self.sort_btn.pack(pady=(0, 20))

        # Статус
        self.status_label = tk.Label(main_frame, text="✅ Готов к работе",
                                     font=('Segoe UI', 9),
                                     bg=self.colors['bg'], fg=self.colors['accent'])
        self.status_label.pack()

        # Информация о категориях
        info_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        info_frame.pack(fill=tk.X, pady=(20, 0))

        info_text = "Категории: Изображения | Документы | Видео | Аудио | Архивы | Программы | Шрифты | Базы данных | Остальное"
        info_label = tk.Label(info_frame, text=info_text,
                              font=('Segoe UI', 7),
                              bg=self.colors['bg'], fg='#666666',
                              wraplength=550)
        info_label.pack()

    def select_folder_threaded(self):
        """Запуск выбора папки в отдельном потоке"""
        thread = threading.Thread(target=self.select_folder)
        thread.daemon = True
        thread.start()

    def select_folder(self):
        """Выбор папки и сканирование"""
        self.select_btn.config(state=tk.DISABLED)
        self.status_label.config(text="⏳ Выбор папки...", fg='orange')
        self.root.update()

        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=f"📁 {os.path.basename(folder)}", fg=self.colors['accent'])
            self.sort_btn.config(state=tk.NORMAL)
            self.status_label.config(text="✅ Папка выбрана, готов к сортировке", fg=self.colors['accent'])

            # Сканируем и показываем статистику
            self.scan_folder_stats()
        else:
            self.status_label.config(text="⚠️ Выбор папки отменен", fg='orange')

        self.select_btn.config(state=tk.NORMAL)

    def scan_folder_stats(self):
        """Сканирование папки и отображение статистики"""
        try:
            stats = {category: 0 for category in self.categories.keys()}
            stats["Остальное"] = 0
            total_files = 0

            for filename in os.listdir(self.selected_folder):
                file_path = os.path.join(self.selected_folder, filename)
                if os.path.isfile(file_path):
                    total_files += 1
                    _, ext = os.path.splitext(filename)
                    category = self.get_category(ext)
                    stats[category] = stats.get(category, 0) + 1

            if total_files > 0:
                stats_text = f"📊 Найдено файлов: {total_files}\n"
                for cat, count in stats.items():
                    if count > 0:
                        stats_text += f"   {cat}: {count}\n"
                self.stats_label.config(text=stats_text)
            else:
                self.stats_label.config(text="📊 В выбранной папке нет файлов для сортировки")

        except Exception as e:
            self.stats_label.config(text=f"❌ Ошибка сканирования: {str(e)}")

    def get_category(self, ext):
        """Определяет категорию файла по расширению"""
        ext_lower = ext.lower()
        for category, extensions in self.categories.items():
            if ext_lower in extensions:
                return category
        return "Остальное"

    def get_unique_filename(self, folder, filename):
        """Генерирует уникальное имя файла, если файл уже существует"""
        name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename

        while os.path.exists(os.path.join(folder, new_filename)):
            new_filename = f"{name}_{counter}{ext}"
            counter += 1

        return new_filename

    def sort_files_threaded(self):
        """Запуск сортировки в отдельном потоке"""
        if self.is_sorting:
            return

        thread = threading.Thread(target=self.sort_files)
        thread.daemon = True
        thread.start()

    def sort_files(self):
        """Основная логика сортировки файлов"""
        if not self.selected_folder:
            messagebox.showwarning("Предупреждение", "Сначала выберите папку!")
            return

        self.is_sorting = True
        self.sort_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)
        self.status_label.config(text="🔄 Сортировка выполняется...", fg='orange')
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Подготовка...")
        self.root.update()

        moved_count = 0
        skipped_count = 0
        error_count = 0

        try:
            # Получаем список всех файлов
            files = [f for f in os.listdir(self.selected_folder)
                     if os.path.isfile(os.path.join(self.selected_folder, f))]
            total_files = len(files)

            if total_files == 0:
                messagebox.showinfo("Информация", "В выбранной папке нет файлов для сортировки!")
                self.status_label.config(text="✅ Нет файлов для сортировки", fg=self.colors['accent'])
                return

            for i, filename in enumerate(files):
                file_path = os.path.join(self.selected_folder, filename)

                # Обновляем прогресс
                progress = (i + 1) / total_files * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Обработка: {i + 1}/{total_files} - {filename[:50]}")
                self.root.update()

                # Получаем расширение файла
                _, ext = os.path.splitext(filename)

                # Определяем категорию
                category = self.get_category(ext)

                # Создаем папку категории если её нет
                category_path = os.path.join(self.selected_folder, category)
                if not os.path.exists(category_path):
                    os.makedirs(category_path)

                # Получаем уникальное имя файла в целевой папке
                unique_filename = self.get_unique_filename(category_path, filename)
                new_file_path = os.path.join(category_path, unique_filename)

                try:
                    # Перемещаем файл
                    shutil.move(file_path, new_file_path)
                    moved_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Ошибка при перемещении {filename}: {e}")

            # Выводим результат
            result_msg = f"✅ Сортировка завершена!\n\n📊 Перемещено файлов: {moved_count}"
            if error_count > 0:
                result_msg += f"\n⚠️ Ошибок: {error_count}"
            if skipped_count > 0:
                result_msg += f"\n⏭️ Пропущено: {skipped_count}"

            result_msg += f"\n\n📁 Папка: {self.selected_folder}"

            messagebox.showinfo("Результат сортировки", result_msg)
            self.status_label.config(text=f"✅ Завершено. Перемещено: {moved_count}", fg=self.colors['accent'])

            # Обновляем статистику
            self.scan_folder_stats()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_label.config(text="❌ Ошибка при сортировке", fg='red')
        finally:
            self.is_sorting = False
            self.sort_btn.config(state=tk.NORMAL)
            self.select_btn.config(state=tk.NORMAL)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="")


def main():
    root = tk.Tk()
    app = DanrexSorter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
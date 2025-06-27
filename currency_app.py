import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime
import csv

class CurrencyApp:
    def __init__(self, root):
        """Инициализация главного окна приложения"""
        self.root = root
        self.root.title("Курсы валют ЦБ РФ")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Настройка стилей
        self.setup_styles()
        
        # Основные данные
        self.currencies = {
            'USD': {'name': 'Доллар США', 'rate': 0},
            'EUR': {'name': 'Евро', 'rate': 0},
            'CNY': {'name': 'Китайский юань', 'rate': 0}
        }
        
        # Создание интерфейса
        self.create_widgets()
        
        # Первая загрузка данных
        self.load_currency_rates()

    def setup_styles(self):
        """Настройка внешнего вида элементов"""
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        header = ttk.Label(
            self.root,
            text="Актуальные курсы валют",
            style='Header.TLabel'
        )
        header.pack(pady=10)

        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        
        self.refresh_btn = ttk.Button(
            button_frame,
            text="Обновить данные",
            command=self.load_currency_rates
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            button_frame,
            text="Сохранить в CSV",
            command=self.save_to_csv
        )
        self.save_btn.pack(side=tk.LEFT)

        # Таблица с курсами
        self.create_rates_table()

        # Статус бар
        self.status = ttk.Label(
            self.root,
            text="Готов к работе",
            relief=tk.SUNKEN,
            padding=5
        )
        self.status.pack(fill=tk.X, pady=5)

    def create_rates_table(self):
        """Создание таблицы для отображения курсов"""
        self.rates_table = ttk.Treeview(
            self.root,
            columns=('currency', 'rate', 'date'),
            show='headings',
            height=5
        )
        
        # Настройка столбцов
        self.rates_table.heading('currency', text='Валюта')
        self.rates_table.heading('rate', text='Курс (руб)')
        self.rates_table.heading('date', text='Дата обновления')
        
        self.rates_table.column('currency', width=150, anchor='center')
        self.rates_table.column('rate', width=150, anchor='center')
        self.rates_table.column('date', width=150, anchor='center')
        
        self.rates_table.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def load_currency_rates(self):
        """Загрузка актуальных курсов с API ЦБ РФ"""
        try:
            self.status.config(text="Загрузка данных...")
            self.root.update()  # Обновляем интерфейс
            
            # Получаем данные с API
            api_url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()  # Проверка ошибок
            
            data = response.json()
            
            # Обновляем курсы
            for currency_code in self.currencies:
                self.currencies[currency_code]['rate'] = data['Valute'][currency_code]['Value']
            
            # Обновляем таблицу
            self.update_rates_table()
            
            self.status.config(text=f"Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка соединения",
                f"Не удалось получить данные:\n{str(e)}"
            )
            self.status.config(text="Ошибка загрузки данных")
        except Exception as e:
            messagebox.showerror(
                "Неизвестная ошибка",
                f"Произошла непредвиденная ошибка:\n{str(e)}"
            )

    def update_rates_table(self):
        """Обновление данных в таблице"""
        # Очищаем старые данные
        for row in self.rates_table.get_children():
            self.rates_table.delete(row)
        
        # Добавляем новые данные
        for currency_code, currency_data in self.currencies.items():
            self.rates_table.insert(
                '',
                tk.END,
                values=(
                    currency_data['name'],
                    f"{currency_data['rate']:.2f}",
                    datetime.now().strftime("%d.%m.%Y")
                )
            )

    def save_to_csv(self):
        """Сохранение курсов в CSV файл"""
        try:
            # Выбираем место для сохранения
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV файлы", "*.csv")],
                title="Сохранить курсы валют",
                initialfile=f"currency_rates_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if not filepath:  # Если пользователь отменил сохранение
                return
                
            # Записываем данные в файл
            with open(filepath, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Валюта', 'Курс (руб)', 'Дата'])
                for currency_data in self.currencies.values():
                    writer.writerow([
                        currency_data['name'],
                        currency_data['rate'],
                        datetime.now().strftime("%Y-%m-%d")
                    ])
            
            messagebox.showinfo(
                "Сохранено",
                f"Курсы валют успешно сохранены в файл:\n{filepath}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить файл:\n{str(e)}"
            )

if __name__ == "__main__":
    # Создаем и запускаем приложение
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()

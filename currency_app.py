import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime
import csv
class CurrencyParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер курсов ЦБ РФ")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Стиль
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # Данные
        self.currencies = {
            "USD": {"name": "Доллар США", "rate": 0},
            "EUR": {"name": "Евро", "rate": 0},
            "CNY": {"name": "Китайский юань", "rate": 0}
        }
        
        # GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель
        header = ttk.Label(
            self.root, 
            text="Курсы валют ЦБ РФ", 
            style="Header.TLabel"
        )
        header.pack(pady=10)
        
        # Фрейм для кнопок
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.btn_refresh = ttk.Button(
            btn_frame, 
            text="Обновить данные", 
            command=self.fetch_data
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = ttk.Button(
            btn_frame,
            text="Сохранить в CSV",
            command=self.save_to_csv
        )
        self.btn_save.pack(side=tk.LEFT)
        
        # Таблица
        self.tree = ttk.Treeview(
            self.root,
            columns=("currency", "rate", "date"),
            show="headings",
            height=5
        )
        self.tree.heading("currency", text="Валюта")
        self.tree.heading("rate", text="Курс (руб)")
        self.tree.heading("date", text="Дата")
        self.tree.column("currency", width=150, anchor="center")
        self.tree.column("rate", width=150, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.status = ttk.Label(
            self.root, 
            text="Нажмите 'Обновить данные'", 
            relief=tk.SUNKEN,
            padding=5
        )
        self.status.pack(fill=tk.X, pady=5)
        
        # Первоначальная загрузка данных
        self.fetch_data()
    
    def fetch_data(self):
        #Получение данных с API ЦБ РФ
        try:
            self.status.config(text="Загрузка данных...")
            self.root.update()  # Обновляем интерфейс
            
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Обновляем данные
            for code in self.currencies.keys():
                self.currencies[code]["rate"] = data["Valute"][code]["Value"]
            
            # Обновляем таблицу
            self.update_table()
            self.status.config(text=f"Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
            self.status.config(text="Ошибка загрузки")
    
    def update_table(self):
        """Обновление данных в таблице"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for code, currency in self.currencies.items():
            self.tree.insert("", tk.END, values=(
                currency["name"],
                f"{currency['rate']:.2f}",
                datetime.now().strftime("%d.%m.%Y")
            ))
    
    def save_to_csv(self):
        """Сохранение данных в CSV"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile=f"currency_rates_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if not filepath:  # Если пользователь отменил
                return
                
            with open(filepath, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Валюта", "Курс (руб)", "Дата"])
                for currency in self.currencies.values():
                    writer.writerow([
                        currency["name"],
                        currency["rate"],
                        datetime.now().strftime("%Y-%m-%d")
                    ])
            
            messagebox.showinfo("Успех", f"Данные сохранены в:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyParserApp(root)
    root.mainloop()

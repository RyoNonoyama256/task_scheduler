import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import datetime
import os

class CSVManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Manager")
        self.create_widgets()
        self.timer_running = False
        self.start_time = None
        self.current_date = None
        self.file_path = None

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("ProjectID", "Type", "Title", "Start", "End", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=0, width=100, stretch=tk.NO)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        today = datetime.date.today()
        self.year_var = tk.StringVar(value=today.year)
        self.month_var = tk.StringVar(value=today.month)
        self.day_var = tk.StringVar(value=today.day)

        tk.Label(btn_frame, text="Year").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Entry(btn_frame, textvariable=self.year_var, width=5).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(btn_frame, text="Month").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Entry(btn_frame, textvariable=self.month_var, width=3).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(btn_frame, text="Day").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Entry(btn_frame, textvariable=self.day_var, width=3).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_btn = tk.Button(btn_frame, text="Load", command=self.load_csv)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_btn = tk.Button(btn_frame, text="Add", command=lambda: self.add_task("planned"))
        self.edit_btn = tk.Button(btn_frame, text="Edit", command=self.edit_task)
        self.delete_btn = tk.Button(btn_frame, text="Delete", command=self.delete_task)
        self.start_timer_btn = tk.Button(btn_frame, text="Start Timer", command=self.start_timer)
        self.stop_timer_btn = tk.Button(btn_frame, text="Stop Timer", command=self.stop_timer)

        self.add_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.edit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.start_timer_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.stop_timer_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.timer_label = tk.Label(self.root, text="00:00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=10)

    def get_current_date(self):
        year = self.year_var.get()
        month = self.month_var.get()
        day = self.day_var.get()
        try:
            current_date = datetime.date(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid date")
            return None
        return current_date

    def add_task(self, default_type):
        self.current_date = self.get_current_date()
        if not self.current_date:
            return
        self.file_path = f"{self.current_date}.csv"
        if os.path.exists(self.file_path):
            self.load_csv()  # 既存ファイルをロード
        self.open_task_window(default_type=default_type)

    def edit_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Edit Task", "Please select a task to edit")
            return

        item = self.tree.item(selected_item)
        task_data = item["values"]
        self.open_task_window(task_data=task_data, item_id=selected_item)

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Delete Task", "Please select a task to delete")
            return

        self.tree.delete(selected_item)
        self.save_csv()

    def save_csv(self):
        if not self.file_path:
            self.current_date = self.get_current_date()
            if not self.current_date:
                messagebox.showwarning("Save CSV", "No date selected")
                return
            self.file_path = f"{self.current_date}.csv"
        
        data = []
        for row_id in self.tree.get_children():
            row = self.tree.item(row_id)["values"]
            data.append([self.current_date] + list(row))

        df = pd.DataFrame(data, columns=["Date", "ProjectID", "Type", "Title", "Start", "End", "Status"])
        df = df.sort_values(by="Start")
        df.to_csv(self.file_path, index=False)

    def load_csv(self):
        current_date = self.get_current_date()
        if not current_date:
            return

        self.current_date = current_date
        self.file_path = f"{self.current_date}.csv"

        try:
            df = pd.read_csv(self.file_path)
            df = df.sort_values(by="Start")
            self.tree.delete(*self.tree.get_children())
            for _, row in df.iterrows():
                self.tree.insert("", tk.END, values=row[1:].tolist())  # 日付列を除いて追加
        except FileNotFoundError:
            self.tree.delete(*self.tree.get_children())
            messagebox.showinfo("Load CSV", f"No existing data for {self.current_date}. A new file will be created upon saving.")

    def start_timer(self):
        if self.timer_running:
            messagebox.showwarning("Timer", "Timer is already running")
            return

        self.start_time = datetime.datetime.now()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        if not self.timer_running:
            messagebox.showwarning("Timer", "No timer running")
            return

        end_time = datetime.datetime.now()
        elapsed_time = end_time - self.start_time
        start_str = self.start_time.strftime("%H:%M")
        end_str = (self.start_time + elapsed_time).strftime("%H:%M")
        self.open_task_window(default_type="actual", task_data=["", "actual", "", start_str, end_str, "active"])
        self.timer_running = False
        self.timer_label.config(text="00:00:00")

    def update_timer(self):
        if self.timer_running:
            elapsed_time = datetime.datetime.now() - self.start_time
            hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
            self.root.after(1000, self.update_timer)

    def open_task_window(self, default_type="planned", task_data=None, item_id=None):
        window = tk.Toplevel(self.root)
        window.title("Task")

        tk.Label(window, text="Project ID").grid(row=0, column=0)
        tk.Label(window, text="Type").grid(row=1, column=0)
        tk.Label(window, text="Title").grid(row=2, column=0)
        tk.Label(window, text="Start (HH:MM)").grid(row=3, column=0)
        tk.Label(window, text="End (HH:MM)").grid(row=4, column=0)
        tk.Label(window, text="Status").grid(row=5, column=0)

        project_id_entry = tk.Entry(window)
        type_var = tk.StringVar(value=default_type)
        title_entry = tk.Entry(window)
        start_hour_entry = tk.Entry(window, width=3)
        start_minute_entry = tk.Entry(window, width=3)
        end_hour_entry = tk.Entry(window, width=3)
        end_minute_entry = tk.Entry(window, width=3)
        status_var = tk.StringVar(value="active")
        
        project_id_entry.grid(row=0, column=1, columnspan=2)
        tk.Radiobutton(window, text="Planned", variable=type_var, value="planned").grid(row=1, column=1)
        tk.Radiobutton(window, text="Actual", variable=type_var, value="actual").grid(row=1, column=2)

        title_entry.grid(row=2, column=1, columnspan=2)
        start_hour_entry.grid(row=3, column=1, sticky="E")
        tk.Label(window, text=":").grid(row=3, column=2, sticky="W")
        start_minute_entry.grid(row=3, column=3, sticky="W")
        end_hour_entry.grid(row=4, column=1, sticky="E")
        tk.Label(window, text=":").grid(row=4, column=2, sticky="W")
        end_minute_entry.grid(row=4, column=3, sticky="W")

        status_menu = tk.OptionMenu(window, status_var, "done", "active", "crit", "milestone")
        status_menu.grid(row=5, column=1, columnspan=2)

        if task_data:
            project_id_entry.insert(0, task_data[0])
            type_var.set(task_data[1])
            title_entry.insert(0, task_data[2])
            start_hour, start_minute = task_data[3].split(":")
            end_hour, end_minute = task_data[4].split(":")
            start_hour_entry.insert(0, start_hour)
            start_minute_entry.insert(0, start_minute)
            end_hour_entry.insert(0, end_hour)
            end_minute_entry.insert(0, end_minute)
            status_var.set(task_data[5])

        def is_valid_time(hour, minute):
            if not (hour.isdigit() and minute.isdigit()):
                return False
            hour, minute = int(hour), int(minute)
            return 0 <= hour < 24 and 0 <= minute < 60

        def save_task():
            project_id = project_id_entry.get()
            type_ = type_var.get()
            title = title_entry.get()
            start_hour = start_hour_entry.get()
            start_minute = start_minute_entry.get()
            end_hour = end_hour_entry.get()
            end_minute = end_minute_entry.get()
            start = f"{start_hour}:{start_minute}"
            end = f"{end_hour}:{end_minute}"
            status = status_var.get()

            if not (project_id and type_ and title and start and end and status):
                messagebox.showwarning("Save Task", "All fields are required")
                return

            if not (is_valid_time(start_hour, start_minute) and is_valid_time(end_hour, end_minute)):
                messagebox.showwarning("Save Task", "Invalid time format")
                return

            if item_id:
                self.tree.item(item_id, values=(project_id, type_, title, start, end, status))
            else:
                self.tree.insert("", tk.END, values=(project_id, type_, title, start, end, status))

            self.save_csv()
            self.sort_treeview()
            window.destroy()

        tk.Button(window, text="Save", command=save_task).grid(row=6, column=0, columnspan=3)

    def sort_treeview(self):
        items = [(self.tree.set(k, "Start"), k) for k in self.tree.get_children()]
        items.sort()
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVManagerApp(root)
    root.mainloop()

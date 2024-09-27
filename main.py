import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

# Default expiration times for common food items
default_expiration_times = {
    "apple": "14d",
    "avocado": "6d",
    "banana": "10d",
    "beef": "5d",
    "bread": "3d",
    "broccoli": "7d",
    "butter": "60d",
    "cabbage": "21d",
    "carrot": "30d",
    "cheese": "21d",
    "chicken": "2d",
    "chocolate": "365d",
    "coffee": "365d",
    "cucumber": "7d",
    "egg": "28d",
    "fish": "2d",
    "grape": "10d",
    "ham": "7d",
    "lettuce": "7d",
    "mayonnaise": "90d",
    "milk": "5d",
    "mushroom": "5d",
    "onion": "30d",
    "orange": "21d",
    "pear": "14d",
    "pepper": "10d",
    "pork": "3d",
    "potatoe": "30d",
    "salmon": "2d",
    "sausage": "10d",
    "shrimp": "3d",
    "spinach": "5d",
    "strawberry": "5d",
    "tomato": "5d",
    "watermelon": "7d",
    "wine": "730d",
    "yogurt": "10d",
    "zucchini": "7d",
}

DATA_FILE = "data.json"
SETTINGS_FILE = "settings.json"


def parse_time_string(time_str):
    # Convert input expiration time to timedelta
    time_str = time_str.lower()
    if time_str == "inf":
        return "inf"
    elif time_str.endswith("d"):
        return timedelta(days=int(time_str[:-1]))
    elif time_str.endswith("w"):
        return timedelta(weeks=int(time_str[:-1]))
    elif time_str.endswith("h"):
        return timedelta(hours=int(time_str[:-1]))
    elif time_str.endswith("m"):
        return timedelta(days=int(time_str[:-1]) * 30)
    elif time_str.endswith("y"):
        return timedelta(days=int(time_str[:-1]) * 365)
    else:
        return timedelta(days=int(time_str))  # Default to days if no unit is specified


# File operations for saving and loading data
def save_items(items):
    with open(DATA_FILE, "w") as file:
        json.dump(items, file)

def load_items():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_settings(geometry):
    with open(SETTINGS_FILE, "w") as file:
        json.dump({"geometry": geometry}, file)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {}

class ExpirationTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expiration Tracker")

        # Load stored window settings and items
        settings = load_settings()
        geometry = settings.get("geometry", "430x360+100+100")
        self.root.geometry(geometry)
        self.root.minsize(430, 360)
        self.items = load_items()

        # Set up the main UI components
        self.setup_ui()

        # Display the initial items
        self.refresh_items()

        # Configure the scroll region
        self.item_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Save window settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Create scrollable frame for items
        self.scrollable_frame = tk.Frame(self.root)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scroll_canvas = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_canvas.set)

        self.scroll_canvas.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.item_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.item_frame, anchor="nw")

        # Bind mouse wheel scrolling
        self.scrollable_frame.bind("<Enter>", lambda e: self.scrollable_frame.bind_all("<MouseWheel>", self.on_mouse_wheel))
        self.scrollable_frame.bind("<Leave>", lambda e: self.scrollable_frame.unbind_all("<MouseWheel>"))

        # Create button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Add buttons
        self.copy_button = tk.Button(button_frame, text="Copy Items", command=self.copy_items_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(button_frame, text="Add Item", command=self.open_add_item_window)
        self.add_button.config(width=20)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Expired", command=self.delete_expired_items)
        self.delete_button.pack(side=tk.LEFT, padx=5)

    def refresh_items(self):
        # Sort items by expiration time
        self.items.sort(key=lambda item: (item['expiration_time'] == "inf", item['expiration_time']))

        # Clear and recreate the item list
        for widget in self.item_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.items):
            self.create_item_row(item, idx)

    def create_item_row(self, item, idx):
        # Create a row for each item in the list
        item_row = tk.Frame(self.item_frame, bd=1, relief=tk.SOLID)
        item_row.pack(fill=tk.X, pady=5)

        expiration_time_str = item['expiration_time']

        if expiration_time_str == "inf":
            remaining_time_text = "Never"
            text_color = "black"
        else:
            expiration_time = datetime.strptime(expiration_time_str, '%Y-%m-%d %H:%M:%S')
            remaining_time = expiration_time - datetime.now()

            days, hours = self.calculate_time_left(remaining_time)
            if remaining_time.total_seconds() < 0:
                remaining_time_text = "Expired"
                text_color = "red"
            else:
                remaining_time_text = f"{days}d {hours}h"
                text_color = "black" if remaining_time.total_seconds() >= 86400 else "red"

        # Create item content
        item_content = tk.Frame(item_row)
        item_content.pack(side=tk.LEFT, fill=tk.X, expand=True)

        item_label = tk.Label(item_content, text=f"{item['name']} - Expires in {remaining_time_text}", fg=text_color)
        item_label.pack(side=tk.LEFT, padx=(0, 150))

        # Add edit and delete buttons
        edit_icon = tk.PhotoImage(file="edit.png")
        edit_button = tk.Button(item_row, image=edit_icon, command=lambda: self.open_edit_item_window(item, idx), bd=0)
        edit_button.image = edit_icon
        edit_button.pack(side=tk.RIGHT)

        trash_icon = tk.PhotoImage(file="trash.png")
        delete_button = tk.Button(item_row, image=trash_icon, command=lambda: self.delete_item(idx), bd=0)
        delete_button.image = trash_icon
        delete_button.pack(side=tk.RIGHT)

    def open_add_item_window(self):
        # Create a window for adding new items
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Item")
        add_window.geometry("250x120")
        add_window.resizable(False, False)

        self.center_window(add_window)

        # Create input fields
        name_label = tk.Label(add_window, text="Item Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)
        time_label = tk.Label(add_window, text="Expiration Time:")
        time_label.grid(row=1, column=0, padx=5, pady=5)

        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        time_entry = tk.Entry(add_window)
        time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Add button
        add_button = tk.Button(add_window, text="Add",
                               command=lambda: self.add_item(name_entry.get(), time_entry.get(), add_window))
        add_button.grid(row=2, column=0, columnspan=2, pady=10)
        add_button.config(width=10)

        # Bind Enter key to add_item method
        add_window.bind('<Return>', lambda event: self.add_item(name_entry.get(), time_entry.get(), add_window))

        add_window.protocol("WM_DELETE_WINDOW", lambda: add_window.destroy())

    def open_edit_item_window(self, item, idx):
        # Create a window for editing existing items
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Item")
        edit_window.geometry("250x120")
        edit_window.resizable(False, False)

        self.center_window(edit_window)

        # Create input fields
        name_label = tk.Label(edit_window, text="Item Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)
        time_label = tk.Label(edit_window, text="Expiration Time:")
        time_label.grid(row=1, column=0, padx=5, pady=5)

        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, item['name'])
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        time_entry = tk.Entry(edit_window)
        time_entry.insert(0, item['expiration_time'])
        time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Update button
        update_button = tk.Button(edit_window, text="Update",
                                  command=lambda: self.update_item(name_entry.get(), time_entry.get(), edit_window, idx))
        update_button.grid(row=2, column=0, columnspan=2, pady=10)
        update_button.config(width=10)

        # Bind Enter key to update_item method
        edit_window.bind('<Return>', lambda event: self.update_item(name_entry.get(), time_entry.get(), edit_window, idx))

        edit_window.protocol("WM_DELETE_WINDOW", lambda: edit_window.destroy())

    def add_item(self, name, expiration_time, window):
        # Add a new item to the tracker
        if not name:
            messagebox.showwarning("Warning", "Please fill in the item name.")
            return

        if not expiration_time:
            expiration_time = default_expiration_times.get(name.lower(), None)
            if expiration_time is None:
                messagebox.showwarning("Warning", "Please provide an expiration time for this item.")
                return

        try:
            if expiration_time.lower() == "inf":
                expiration_time_str = "inf"
            else:
                expiration_time_obj = datetime.now() + parse_time_string(expiration_time.lower())
                expiration_time_str = expiration_time_obj.strftime('%Y-%m-%d %H:%M:%S')

            self.items.append({
                'name': name,
                'expiration_time': expiration_time_str
            })

            save_items(self.items)
            self.refresh_items()
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expiration time. Error: {e}")

    def update_item(self, name, expiration_time, window, idx):
        # Update an existing item in the tracker
        if not name or not expiration_time:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        try:
            if expiration_time.lower() == "inf":
                expiration_time_str = "inf"
            else:
                try:
                    # First, try to parse as a date
                    expiration_time_obj = datetime.strptime(expiration_time, '%Y-%m-%d %H:%M:%S')
                    expiration_time_str = expiration_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # If date parsing fails, try to parse as a time string
                    try:
                        time_delta = parse_time_string(expiration_time)
                        if time_delta == "inf":
                            expiration_time_str = "inf"
                        else:
                            expiration_time_obj = datetime.now() + time_delta
                            expiration_time_str = expiration_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValueError(
                            "Invalid expiration time format. Please use 'YYYY-MM-DD HH:MM:SS' or a valid time string (e.g., '7d', '2w', '1m').")

            self.items[idx]['name'] = name
            self.items[idx]['expiration_time'] = expiration_time_str

            save_items(self.items)
            self.refresh_items()
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_item(self, idx):
        # Delete an item from the tracker
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.items[idx]['name']}?"):
            del self.items[idx]
            save_items(self.items)
            self.refresh_items()

    def on_mouse_wheel(self, event):
        # Handle mouse wheel scrolling
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def calculate_time_left(self, remaining_time):
        # Calculate days and hours left until expiration
        days = remaining_time.days
        hours = remaining_time.seconds // 3600
        return days, hours

    def center_window(self, window):
        # Center a window on the screen
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def copy_items_to_clipboard(self):
        # Copy all item names to the clipboard
        item_names = [item['name'] for item in self.items]
        names_str = ", ".join(item_names)
        self.root.clipboard_clear()
        self.root.clipboard_append(names_str)
        messagebox.showinfo("Success", "Items copied to clipboard!")

    def delete_expired_items(self):
        # Delete all expired items from the tracker
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all expired items?"):
            return

        current_time = datetime.now()
        non_expired_items = []

        for item in self.items:
            expiration_time_str = item['expiration_time']
            if expiration_time_str != "inf":
                try:
                    expiration_time = datetime.strptime(expiration_time_str, '%Y-%m-%d %H:%M:%S')
                    if expiration_time > current_time:
                        non_expired_items.append(item)
                except ValueError:
                    non_expired_items.append(item)
            else:
                non_expired_items.append(item)

        self.items = non_expired_items
        save_items(self.items)
        self.refresh_items()
        messagebox.showinfo("Success", "Expired items deleted!")

    def on_close(self):
        # Save window settings and close the application
        geometry = self.root.geometry()
        save_settings(geometry)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpirationTrackerApp(root)
    root.mainloop()

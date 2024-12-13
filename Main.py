import tkinter as tk
from tkinter import filedialog
from charset_normalizer import detect


class MistrPrstu:
    def __init__(self, master):
        self.master = master
        self.master.title("Mistr Prstů")
        self.text = ""
        self.current_index = 0
        self.errors = 0
        self.next_expected_char = ""

        # Česká QWERTZ klávesnice
        self.keyboard_layout = [
            [";", "+", "ě", "š", "č", "ř", "ž", "ý", "á", "í", "é", "=", "´", "Backspace"],
            ["Tab", "q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ú", ")"],
            ["CapsLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", "ů", "§", "¨"],
            ["LShift", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "RShift"],
            ["Ctrl", "Win", "Alt", "Space", "AltGr", "Win", "Fn", "Ctrl"]
        ]
        self.key_buttons = {}

        # Vytvoření GUI
        self.label = tk.Label(master, text="Vyberte soubor", font=("Helvetica", 16))
        self.label.pack()

        self.text_box = tk.Text(master, height=5, width=100, font=("Helvetica", 14))
        self.text_box.pack()

        self.user_text_box = tk.Text(master, height=5, width=100, font=("Helvetica", 14), state="disabled") 
        self.user_text_box.pack()

        self.canvas = tk.Canvas(master, width=1100, height=400, bg="white")
        self.canvas.pack()

        self.load_button = tk.Button(master, text="Vybrat .txt soubor", command=self.load_file)
        self.load_button.pack()

        self.master.bind("<KeyPress>", self.on_key_press)

        self.create_keyboard()
    
    def detect_encoding(self, file_path):
        """Detekuje kódování souboru."""
        with open(file_path, "rb") as file:
            raw_data = file.read()
            result = detect(raw_data)
            return result["encoding"]
    

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            encoding = self.detect_encoding(file_path)  # Detekuje kódování
            if not encoding:
                self.label.config(text="Nepodařilo se zjistit kódování")
                return

            try:
                with open(file_path, "r", encoding=encoding) as file:
                    self.text = file.read()
            except Exception as e:
                self.label.config(text=f"Chyba při načítání souboru: {e}")
                return

            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, self.text)
            self.current_index = 0
            self.errors = 0
            self.label.config(text="Začněte psát...")

            self.highlight_text()

    def create_keyboard(self):
        """Vytvoří české QWERTZ rozložení na canvasu."""
        x_start, y_start = 20, 20
        key_width, key_height = 60, 60
        gap = 10

        # Specifikace šířek kláves (v násobcích základní šířky)
        special_keys = {
            "Backspace": 2,
            "Tab": 1.5,
            "CapsLock": 1.75,
            "LShift": 2.25,
            "RShift": 2.75,
            "Space": 6,
            "Ctrl": 1.5,
            "Win": 1.5,
            "Alt": 1.5,
            "AltGr": 1.5,
            "Fn": 1.5
        }

        for row_index, row in enumerate(self.keyboard_layout):
            x_offset = x_start
            for key in row:
                width_multiplier = special_keys.get(key, 1)
                x1 = x_offset
                y1 = y_start + row_index * (key_height + gap)
                x2 = x1 + key_width * width_multiplier
                y2 = y1 + key_height

                # Vytvoření klávesy
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray", outline="black")
                text = self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=key, font=("Helvetica", 12))

                self.key_buttons[key] = (rect, text)

                # Posun na další klávesu
                x_offset += key_width * width_multiplier + gap

    def highlight_key(self, key, color):
        """Rozsvítí klávesu na klávesnici."""
        if key in self.key_buttons:
            rect, _ = self.key_buttons[key]
            self.canvas.itemconfig(rect, fill=color)
        

    def reset_keyboard(self):
        """Resetuje barvu všech kláves."""
        for rect, _ in self.key_buttons.values():
            self.canvas.itemconfig(rect, fill="lightgray")
    
    def highlight_text(self):
     """Zvýrazní aktuální znak v textu a následující očekávaný znak."""
     self.text_box.config(state="normal")
     self.text_box.tag_remove("highlight", "1.0", tk.END)  # Odstraní předchozí zvýraznění
     if self.current_index < len(self.text):
        start_index = f"1.{self.current_index}"
        end_index = f"1.{self.current_index + 1}"
        self.text_box.tag_add("highlight", start_index, end_index)
        self.text_box.tag_config("highlight", background="yellow")
     self.text_box.config(state="disabled")

    # Zvýraznění následujícího očekávaného znaku na klávesnici
     if self.current_index < len(self.text):
        self.next_expected_char = self.text[self.current_index]
        if self.next_expected_char == " ":
            self.highlight_key("Space", "yellow")
        elif self.next_expected_char.isupper():
         self.highlight_key("LShift", "yellow")
         self.highlight_key("RShift", "yellow")
         self.highlight_key(self.next_expected_char.lower(), "yellow")
        else:
            self.highlight_key(self.next_expected_char, "yellow")


    def update_user_text(self, char):
     """Aktualizuje text napsaný uživatelem."""
     self.user_text_box.config(state="normal")
     self.user_text_box.insert(tk.END, char)
     self.user_text_box.config(state="disabled")


    def on_key_press(self, event):
     if self.current_index >= len(self.text):
        return

     expected_char = self.text[self.current_index]
     typed_char = event.char
      
     

     if typed_char == expected_char:
        self.current_index += 1
        self.reset_keyboard()
        self.highlight_text()  # Zvýrazní další znak
        # Aktualizuje text napsaný uživatelem
        self.update_user_text(typed_char)
         
     
     elif typed_char == "\b":  # Backspace
        if self.user_text_box.get("1.0", tk.END).strip():  # Kontrola, že není prázdné
            self.user_text_box.config(state="normal")
            current_text = self.user_text_box.get("1.0", tk.END).strip()
            self.user_text_box.delete("1.0", tk.END)
            self.user_text_box.insert(tk.END, current_text[:-1])  # Odstranění posledního znaku
            self.user_text_box.config(state="disabled")
            return
        self.reset_keyboard()
        self.highlight_text()  
     if typed_char != expected_char:
        self.user_text_box.config(state="disabled")
        if self.next_expected_char.isupper():
         self.user_text_box.config(state="normal")
         self.highlight_key("LShift", "yellow")
         self.highlight_key(expected_char.lower(), "yellow")
        else:
         self.errors += 1
         self.highlight_key("Backspace", "red")
         self.update_user_text(typed_char)
         self.user_text_box.config(state="disabled")
         return

     if self.current_index == len(self.text):
        self.show_results()


    def show_results(self):
        """Zobrazí výsledky po dokončení."""
        total_chars = len(self.text)
        error_rate = (self.errors / total_chars) * 100
        self.label.config(text=f"Dokončeno! Chyby: {self.errors} Chybovost: {error_rate:.2f} %")


# Spuštění aplikace
if __name__ == "__main__":
    root = tk.Tk()
    app = MistrPrstu(root)
    root.mainloop()

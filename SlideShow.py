import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class SlideshowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Slideshow App")
        self.geometry("1000x600")
        self.minsize(1000, 600)  # Set minimum window size
        self.configure(background='black')

        self.image_files = []
        self.image_index = 0
        self.paused = True
        self.fullscreen = False
        self.delay = 3000  # Default delay (3 seconds)
        self.current_image = None
        self.photo = None
        self.slideshow_job = None  # Job reference for scheduled slideshow task
        self.symbol_job = None  # Job reference for the play symbol
        self.pause_symbol_job = None  # Job reference for the pause symbol

        self.create_widgets()
        self.setup_bindings()

    def create_widgets(self):
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create image display label
        self.image_label = tk.Label(self, bg='black')
        self.image_label.grid(row=0, column=0, sticky='nsew')

        # Create control frame
        self.control_frame = tk.Frame(self, bg='#202020')
        self.control_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # Center the buttons within the control frame
        self.button_frame = tk.Frame(self.control_frame, bg='#202020')
        self.button_frame.pack(anchor=tk.CENTER)

        # Create and pack buttons
        self.select_folder_btn = tk.Button(self.button_frame, text="Select Folder", command=self.select_folder, bg='#202020', fg='white', font=("Helvetica", 14), width=15, height=2)
        self.select_folder_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.select_files_btn = tk.Button(self.button_frame, text="Select Image", command=self.select_files, bg='#202020', fg='white', font=("Helvetica", 14), width=15, height=2)
        self.select_files_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.fullscreen_btn = tk.Button(self.button_frame, text="Fullscreen", command=self.toggle_fullscreen, bg='#202020', fg='white', font=("Helvetica", 14), width=15, height=2)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Create slider for delay adjustment
        self.slider_frame = tk.Frame(self.button_frame, bg='#202020')
        self.slider_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.slider_label = tk.Label(self.slider_frame, text="Press spacebar for play", bg='#202020', fg='white', font=("Helvetica", 12))
        self.slider_label.pack(side=tk.TOP)

        self.slider = tk.Scale(self.slider_frame, from_=3, to=30, orient=tk.HORIZONTAL, command=self.update_delay, bg='black', fg='white', troughcolor='gray', showvalue=False, length=300)
        self.slider.set(3)
        self.slider.pack(side=tk.LEFT)

        self.delay_label = tk.Label(self.slider_frame, text="3 s", bg='#202020', fg='white', font=("Helvetica", 14))
        self.delay_label.pack(side=tk.LEFT, padx=5)

        # Create play symbol label
        self.symbol_label = tk.Label(self, text="▶️", fg="white", bg="black", font=("Helvetica", 50))
        self.symbol_label.place(x=25, y=0)
        self.symbol_label.place_forget()

        # Create pause symbol label
        self.pause_symbol_label = tk.Label(self, text="⏸️", fg="white", bg="black", font=("Helvetica", 35))
        self.pause_symbol_label.place(x=10, y=10)
        self.pause_symbol_label.place_forget()

    def setup_bindings(self):
        self.bind("<space>", self.toggle_pause)
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Configure>", self.on_resize)
        self.bind("<Left>", self.show_previous_image)
        self.bind("<Right>", self.show_next_image)
        self.start_slideshow()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
            self.image_index = 0
            if self.image_files:
                self.show_next_image()

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_paths:
            self.image_files = list(file_paths)
            self.image_index = 0
            if self.image_files:
                self.show_next_image()

    def start_slideshow(self):
        if not self.paused and self.image_files:
            self.slideshow_job = self.after(self.delay, self.show_next_image)

    def show_next_image(self, event=None):
        if self.image_files:
            self.image_index = (self.image_index + 1) % len(self.image_files)
            image_path = self.image_files[self.image_index]
            self.current_image = Image.open(image_path)
            self.display_image(self.current_image)
            self.reset_slideshow_timer()  # Schedule next image display

    def show_previous_image(self, event=None):
        if self.image_files:
            self.image_index = (self.image_index - 1) % len(self.image_files)
            image_path = self.image_files[self.image_index]
            self.current_image = Image.open(image_path)
            self.display_image(self.current_image)
            self.reset_slideshow_timer()  # Schedule next image display

    def display_image(self, image):
        if image:
            image = self.resize_image(image)
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo

    def resize_image(self, image):
        screen_width = self.winfo_width()
        screen_height = self.winfo_height()
        img_width, img_height = image.size

        # Maintain aspect ratio
        if img_width / img_height > screen_width / screen_height:
            new_width = screen_width
            new_height = int(screen_width * img_height / img_width)
        else:
            new_height = screen_height
            new_width = int(screen_height * img_width / img_height)

        return image.resize((new_width, new_height), Image.LANCZOS)

    def update_delay(self, value):
        self.delay = int(value) * 1000
        self.delay_label.config(text=f"{value} s")

    def toggle_pause(self, event=None):
        self.paused = not self.paused
        if self.paused:
            if self.slideshow_job:
                self.after_cancel(self.slideshow_job)
            self.control_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
            self.show_pause_symbol()
        else:
            self.control_frame.place_forget()
            self.start_slideshow()
            self.show_play_symbol()

    def show_play_symbol(self):
        self.pause_symbol_label.place_forget()
        self.symbol_label.place(x=25, y=0)
        if self.symbol_job:
            self.after_cancel(self.symbol_job)
        self.symbol_job = self.after(3000, self.hide_play_symbol)  # Show play symbol for 3 seconds

    def hide_play_symbol(self):
        self.symbol_label.place_forget()

    def show_pause_symbol(self):
        self.symbol_label.place_forget()
        self.pause_symbol_label.place(x=10, y=10)
        if self.pause_symbol_job:
            self.after_cancel(self.pause_symbol_job)
        self.pause_symbol_job = self.after(3000, self.hide_pause_symbol)  # Show pause symbol for 3 seconds

    def hide_pause_symbol(self):
        self.pause_symbol_label.place_forget()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        if not self.fullscreen:
            self.geometry("1000x600")

    def exit_fullscreen(self, event=None):
        if self.fullscreen:
            self.toggle_fullscreen()

    def on_resize(self, event):
        if self.current_image:
            self.display_image(self.current_image)

    def reset_slideshow_timer(self):
        if not self.paused:
            if self.slideshow_job:
                self.after_cancel(self.slideshow_job)
            self.start_slideshow()

if __name__ == "__main__":
    app = SlideshowApp()
    app.mainloop()
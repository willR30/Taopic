import os
from tkinter import Tk, Label, Entry, StringVar, IntVar, Frame, filedialog, colorchooser, messagebox
from tkinter import ttk
from PIL import Image, ImageOps

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

input_folder_path = ""
output_folder_path = ""

# === FUNCTIONS ===
def choose_input_folder():
    global input_folder_path
    input_folder_path = filedialog.askdirectory(title="Select Input Folder")
    if input_folder_path:
        input_folder_label.config(text=f"Input: {os.path.basename(input_folder_path)}", foreground="#00ff99")

def choose_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory(title="Select Output Folder")
    if output_folder_path:
        output_folder_label.config(text=f"Output: {os.path.basename(output_folder_path)}", foreground="#00ff99")

def choose_background_color():
    color = colorchooser.askcolor(title="Choose Background Color")
    if color and color[0]:
        background_color_entry.delete(0, 'end')
        background_color_entry.insert(0, ','.join(map(str, color[0])))

def has_transparency(img):
    """Detecta si la imagen tiene canal alfa o transparencia."""
    if img.mode in ("RGBA", "LA"):
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    elif img.info.get("transparency", None) is not None:
        return True
    return False

def remove_background(img):
    """Elimina el fondo usando rembg si está disponible, de lo contrario intenta método básico."""
    if REMBG_AVAILABLE:
        return Image.open(
            remove(img.tobytes(), alpha_matting=True, alpha_matting_foreground_threshold=240)
        ).convert("RGBA")
    else:
        # Método básico: convertir a RGBA y quitar fondo blanco/casi blanco
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        return img

def process_images():
    global input_folder_path, output_folder_path

    if not input_folder_path:
        messagebox.showerror("Error", "Please select an input folder.")
        return
    if not output_folder_path:
        messagebox.showerror("Error", "Please select an output folder.")
        return
    try:
        background_color = tuple(map(int, background_color_entry.get().split(',')))
        if len(background_color) != 3:
            raise ValueError
    except:
        messagebox.showerror("Error", "Background color must be 3 comma-separated integers (R,G,B).")
        return
    try:
        target_width = int(width_entry.get())
        target_height = int(height_entry.get())
        padding = int(padding_entry.get())
        if target_width <= 0 or target_height <= 0 or padding < 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Width, Height must be positive integers and Padding must be zero or positive integer.")
        return

    input_format = input_format_var.get()
    file_format = file_format_var_output.get()
    compression_algorithm = compression_var.get()
    apply_lossless = lossless_var.get()
    apply_bg_removal = remove_bg_var.get()

    files_to_process = []
    for root, _, files in os.walk(input_folder_path):
        for file in files:
            if file.lower().endswith(input_format):
                files_to_process.append(os.path.join(root, file))
    if not files_to_process:
        messagebox.showerror("Error", f"No files with extension '{input_format}' found in input folder.")
        return

    os.makedirs(output_folder_path, exist_ok=True)

    total = len(files_to_process)
    current = 0

    for file_path in files_to_process:
        img = Image.open(file_path)

        # === Nueva lógica: quitar fondo si el usuario lo pidió ===
        if apply_bg_removal and has_transparency(img):
            img = remove_background(img)

        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            background = Image.new("RGBA", img.size, background_color + (255,))
            img = Image.alpha_composite(background, img).convert("RGB")
        else:
            img = img.convert("RGB")

        target_size = (target_width, target_height)
        img_resized = ImageOps.pad(img, target_size, color=background_color, centering=(0.5, 0.5))
        img_resized = ImageOps.expand(img_resized, padding, fill=background_color)

        new_file_path = os.path.join(output_folder_path, os.path.splitext(os.path.basename(file_path))[0] + file_format)

        if compression_algorithm == "JPEG":
            img_resized.save(new_file_path, "JPEG", optimize=True, quality=75 if apply_lossless else 85)
        elif compression_algorithm == "PNG":
            img_resized.save(new_file_path, "PNG", optimize=True, compress_level=9)
        elif compression_algorithm == "WebP":
            img_resized.save(new_file_path, "WEBP", lossless=bool(apply_lossless), quality=75 if apply_lossless else 85)
        elif compression_algorithm == "AVIF":
            img_resized.save(new_file_path, "AVIF", lossless=bool(apply_lossless), quality=75 if apply_lossless else 85)

        current += 1
        progress_bar['value'] = (current / total) * 100
        window.update_idletasks()

    message_label.config(text="✅ Processing Complete!", foreground="#00ff99")
    messagebox.showinfo("Success", "Processing complete!")

# === DARK THEME CONFIG ===
BG_COLOR = "#121212"
FG_COLOR = "#FFFFFF"
ENTRY_BG = "#1E1E1E"
ACCENT_COLOR = "#00C9A7"
FONT = ("Segoe UI", 10)

# === WINDOW ===
window = Tk()
window.title("Taopic - Modern UI")
window.geometry("500x850")
window.configure(bg=BG_COLOR)
window.resizable(width=True, height=False)

style = ttk.Style(window)
style.theme_use("clam")
style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
style.configure("TButton", background=ENTRY_BG, foreground=FG_COLOR, font=FONT)
style.map("TButton", background=[("active", ACCENT_COLOR)], foreground=[("active", "#000")])
style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT)

def section(parent, title):
    section_frame = Frame(parent, bg=BG_COLOR)
    Label(section_frame, text=title, font=("Segoe UI", 12, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(10, 5))
    return section_frame

def dark_entry(parent):
    entry = Entry(parent, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat", font=FONT)
    entry.pack(fill="x", padx=10, pady=4)
    return entry

# === BUILD UI ===
main_frame = Frame(window, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

folder_section = section(main_frame, "📁 Select Folders")
folder_section.pack(fill="x")
ttk.Button(folder_section, text="Input Folder", command=choose_input_folder).pack(pady=2)
input_folder_label = ttk.Label(folder_section, text="No folder selected")
input_folder_label.pack()
ttk.Button(folder_section, text="Output Folder", command=choose_output_folder).pack(pady=2)
output_folder_label = ttk.Label(folder_section, text="No folder selected")
output_folder_label.pack()

format_section = section(main_frame, "🖼️ Format & Compression")
format_section.pack(fill="x")
input_format_var = StringVar(value=".png")
ttk.Label(format_section, text="Input Format").pack(anchor="w")
ttk.OptionMenu(format_section, input_format_var, ".png", ".png", ".jpg", ".jpeg", ".webp", ".avif").pack(fill="x")
file_format_var_output = StringVar(value=".jpg")
ttk.Label(format_section, text="Output Format").pack(anchor="w")
ttk.OptionMenu(format_section, file_format_var_output, ".jpg", ".jpg", ".png", ".webp", ".avif").pack(fill="x")
compression_var = StringVar(value="JPEG")
ttk.Label(format_section, text="Compression Algorithm").pack(anchor="w")
ttk.OptionMenu(format_section, compression_var, "JPEG", "JPEG", "PNG", "WebP", "AVIF").pack(fill="x")
lossless_var = IntVar()
ttk.Checkbutton(format_section, text="Apply Lossless Compression", variable=lossless_var).pack(anchor="w", pady=5)

# === NUEVO: opción para quitar fondo ===
remove_bg_var = IntVar()
ttk.Checkbutton(format_section, text="Remove Background if Present", variable=remove_bg_var).pack(anchor="w", pady=5)

settings_section = section(main_frame, "🎨 Dimensions & Background")
settings_section.pack(fill="x")
ttk.Label(settings_section, text="Background Color (R,G,B)").pack(anchor="w")
background_color_entry = dark_entry(settings_section)
ttk.Button(settings_section, text="Pick Color", command=choose_background_color).pack(pady=2)
width_entry = dark_entry(settings_section)
width_entry.insert(0, "Width")
height_entry = dark_entry(settings_section)
height_entry.insert(0, "Height")
padding_entry = dark_entry(settings_section)
padding_entry.insert(0, "Padding")

progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
progress_bar.pack(pady=10)
ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
ttk.Button(main_frame, text="🚀 Process Images", command=process_images).pack(pady=10)
message_label = ttk.Label(main_frame, text="")
message_label.pack()

window.mainloop()
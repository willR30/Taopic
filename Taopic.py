import os
from tkinter import Tk, Label, Button, filedialog, OptionMenu, StringVar, Entry, colorchooser, Checkbutton, IntVar
from PIL import Image, ImageOps

input_folder_path = ""
output_folder_path = ""


def choose_input_folder():
    global input_folder_path
    input_folder_path = filedialog.askdirectory(title="Seleccione la carpeta de entrada")
    if input_folder_path:
        input_folder_label.config(text="Carpeta de entrada seleccionada")


def choose_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory(title="Seleccione la carpeta de destino")
    if output_folder_path:
        output_folder_label.config(text="Carpeta de destino seleccionada")


def choose_background_color():
    color = colorchooser.askcolor(title="Seleccione un color")
    if color:
        background_color_entry.delete(0, 'end')
        background_color_entry.insert(0, ','.join(map(str, color[0])))


def process_images():
    global input_folder_path, output_folder_path

    if input_folder_path and output_folder_path:
        os.makedirs(output_folder_path, exist_ok=True)

        input_format = input_format_var.get()
        file_format = file_format_var_output.get()
        compression_algorithm = compression_var.get()
        background_color = tuple(map(int, background_color_entry.get().split(',')))
        target_width = int(width_entry.get())
        target_height = int(height_entry.get())
        padding = int(padding_entry.get())
        apply_lossless = lossless_var.get()

        for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.lower().endswith(input_format):
                    file_path = os.path.join(root, file)
                    img = Image.open(file_path)

                    # Detectar si tiene canal alfa (transparencia)
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        img = img.convert("RGBA")
                        background = Image.new("RGBA", img.size, background_color + (255,))
                        img = Image.alpha_composite(background, img).convert("RGB")
                    else:
                        img = img.convert("RGB")

                    # Redimensionar y aplicar padding
                    target_size = (target_width, target_height)
                    img_resized = ImageOps.pad(img, target_size, color=background_color, centering=(0.5, 0.5))
                    img_resized = ImageOps.expand(img_resized, padding, fill=background_color)

                    # Construir ruta de salida
                    new_file_path = os.path.join(output_folder_path, os.path.splitext(file)[0] + file_format)

                    # Guardar con compresión correspondiente
                    if compression_algorithm == "JPEG":
                        img_resized.save(new_file_path, "JPEG", optimize=True, quality=75 if apply_lossless else 85)
                    elif compression_algorithm == "PNG":
                        img_resized.save(new_file_path, "PNG", optimize=True, compress_level=9)
                    elif compression_algorithm == "WebP":
                        img_resized.save(new_file_path, "WEBP", lossless=bool(apply_lossless), quality=75 if apply_lossless else 85)
                    elif compression_algorithm == "AVIF":
                        img_resized.save(new_file_path, "AVIF", lossless=bool(apply_lossless), quality=75 if apply_lossless else 85)

        message_label.config(text="¡Procesamiento completado!")


# Crear la ventana principal
window = Tk()
window.title("Taopic")
window.geometry("400x800")

# Etiqueta y botón para seleccionar la carpeta de entrada
input_folder_label = Label(window, text="Select the input folder")
input_folder_label.pack(pady=10)
input_folder_button = Button(window, text="Select the input folder", command=choose_input_folder)
input_folder_button.pack()

# Etiqueta y botón para seleccionar la carpeta de destino
output_folder_label = Label(window, text="Select the output folder")
output_folder_label.pack(pady=10)
output_folder_button = Button(window, text="Select the output folder", command=choose_output_folder)
output_folder_button.pack()

# Menú para seleccionar formato de entrada
input_format_label = Label(window, text="Input image format")
input_format_label.pack(pady=10)
input_formats = [".png", ".jpg", ".jpeg", ".webp", ".avif"]
input_format_var = StringVar(window)
input_format_var.set(input_formats[0])  # Formato por defecto
input_format_dropdown = OptionMenu(window, input_format_var, *input_formats)
input_format_dropdown.pack()

# Etiqueta para formato de salida
output_format_label = Label(window, text="Output image format")
output_format_label.pack(pady=10)
file_output_formats_select = [".jpg", ".png", ".webp", ".avif"]
file_format_var_output = StringVar(window)
file_format_var_output.set(file_output_formats_select[0])
file_format_dropdown_output = OptionMenu(window, file_format_var_output, *file_output_formats_select)
file_format_dropdown_output.pack()

# Menú para seleccionar algoritmo de compresión
compression_label = Label(window, text="Select compression algorithm")
compression_label.pack(pady=10)
compression_algorithms = ["JPEG", "PNG", "WebP", "AVIF"]
compression_var = StringVar(window)
compression_var.set(compression_algorithms[0])
compression_dropdown = OptionMenu(window, compression_var, *compression_algorithms)
compression_dropdown.pack()

# Checkbox para compresión sin pérdida
lossless_var = IntVar()
lossless_checkbox = Checkbutton(window, text="Apply lossless compression", variable=lossless_var)
lossless_checkbox.pack(pady=5)

# Color de fondo
background_color_label = Label(window, text="Background color")
background_color_label.pack()
background_color_entry = Entry(window)
background_color_entry.pack()
choose_color_button = Button(window, text="Select", command=choose_background_color)
choose_color_button.pack()

# Dimensiones y padding
width_label = Label(window, text="Objective width:")
width_label.pack()
width_entry = Entry(window)
width_entry.pack()

height_label = Label(window, text="Objective height:")
height_label.pack()
height_entry = Entry(window)
height_entry.pack()

padding_label = Label(window, text="Padding:")
padding_label.pack()
padding_entry = Entry(window)
padding_entry.pack()

# Botón para procesar imágenes
process_button = Button(window, text="Process images", command=process_images)
process_button.pack(pady=10)

# Mensaje de estado
message_label = Label(window, text="")
message_label.pack()

# Ejecutar la interfaz
window.mainloop()

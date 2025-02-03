import pyfiglet
import os
from datetime import datetime

def get_banner_with_info(text):
    # Detectar automáticamente la ruta del archivo y el nombre del archivo
    file_path = os.path.abspath(__file__)
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear el banner con el texto - ajustar el ancho para que no se comprima
    banner = pyfiglet.figlet_format(text, font="big", width=100,justify="left")  # Ancho fijo de 80 caracteres
    
    # Convertir a HTML preservando espaciado exacto
    output = f"""
    <div style='white-space: pre; font-family: "Roboto Mono", monospace; font-size: 12px; line-height: 1;'>
    Compiler v.1.0 - {file_dir} - {file_name} - {current_date}
    {banner}
    {'-' * 1800}
    </div>
    """
    return output



# Y en initUI modificar:
# self.terminal.setHtml(banner_text)  # Usar setHtml en lugar de setPlainText

# import art
# def get_banner_with_info(text):
#     banner = art.text2art(text)
#     return banner

# # Llamada a la función para obtener el formato completo
# formatted_banner = get_banner_with_info("Hello World")
# print(formatted_banner)
from PIL import Image

def invertir_color_iconos(ruta_entrada, ruta_salida):
    """
    Invierte el color de los iconos con fondo transparente y contorno negro a blanco.
    
    :param ruta_entrada: Carpeta donde están los iconos en negro.
    :param ruta_salida: Carpeta donde se guardarán los iconos en blanco.
    """
    import os

    if not os.path.exists(ruta_salida):
        os.makedirs(ruta_salida)

    for archivo in os.listdir(ruta_entrada):
        if archivo.endswith(".png"):
            ruta_archivo = os.path.join(ruta_entrada, archivo)
            imagen = Image.open(ruta_archivo).convert("RGBA")

            # Obtener los píxeles de la imagen
            pixeles = imagen.load()
            ancho, alto = imagen.size

            for x in range(ancho):
                for y in range(alto):
                    r, g, b, a = pixeles[x, y]

                    # Si el color es negro (o casi negro), cambiarlo a blanco
                    if r < 50 and g < 50 and b < 50:  # Rango para considerar negros
                        pixeles[x, y] = (255, 255, 255, a)  # Cambia a blanco, mantiene la transparencia

            # Guardar la imagen invertida
            ruta_guardado = os.path.join(ruta_salida, archivo)
            imagen.save(ruta_guardado)
            print(f"Imagen invertida guardada en: {ruta_guardado}")

# Ejemplo de uso
invertir_color_iconos("resources\img", "resources\img\inverted")

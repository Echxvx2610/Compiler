def verificar_llaves(codigo):
    """
    Función para verificar si las llaves de un código C están correctamente balanceadas.
    Ahora informa la línea exacta donde empieza el error.
    """
    pila = []  # Utilizamos una pila para controlar las llaves de apertura y cierre
    lineas = codigo.splitlines()  # Dividimos el código por líneas

    for num_linea, linea in enumerate(lineas, 1):
        for char in linea:
            if char == '{':  # Detecta llave de apertura
                pila.append(num_linea)  # Almacena la línea de apertura
            elif char == '}':  # Detecta llave de cierre
                if not pila:  # Si no hay una llave de apertura correspondiente
                    print(f"Error: Llave de cierre en la línea {num_linea} sin apertura correspondiente.")
                    return False
                else:
                    pila.pop()  # Elimina la llave de apertura correspondiente

    if pila:  # Si quedan llaves de apertura sin cerrar
        print(f"Error: Llave de apertura en la línea {pila[-1]} sin cierre correspondiente.")
        return False

    print("El código tiene las llaves balanceadas correctamente.")
    return True

# Función para leer el archivo y analizar el código
def analizar_codigo_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as file:
            codigo = file.read()  # Leemos el contenido completo del archivo

        # Llamamos a la función para verificar las llaves
        verificar_llaves(codigo)

    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")

if __name__ == "__main__":
    # Aquí puedes cambiar el nombre del archivo C que quieras analizar
    archivo_codigo = 'hello.c'  # Asegúrate de que este archivo esté en el mismo directorio o proporciónale la ruta correcta
    analizar_codigo_desde_archivo(archivo_codigo)

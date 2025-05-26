    Propiedades del lenguaje a analizar ( C )

    1.- Analizar texto cargado, linea por linea,caracter por caracter
                - Indentificadores:
                    + reglas de escritura:

    |<----------|
                    --- Letra ---- Letras ------>
                                |           |
                                |--Digitos--|

    - Palabras reservadas
                    - igual que identificador pero esta se encuentra en una lista de palabras reservadas

    |<----------|
                    --- Letra ---- Letras ------>
                                |           |
                                |--Digitos--|

    - Identificador de funciones
                    - igual que identificador pero este tiene () al final

    |<----------|
                    --- Letra ---- Letras ------> ( )
                                |           |
                                |--Digitos--|

    - Identificador de libreria
                    - igual que identificador pero este tiene () al final

    |<----------|
                    --- Letra ---- Letras ------| punto | --- | h | --->
                                |           |
                                |--Digitos--|

    - Simbolos
                    + reglas
                        |---  #  --|
                        |---  !  --^
                        |---  +  --^
                        |---  <  --^
                        |---  >  --^
                        |---  =  --^

    - Numeros
                    + reglas:
                        Enteros:

    |----------|
                        |---|   Digito  |--->

    Decimales:D

    |<----------|              |<----------|
                        |---|   Digito  |---> punto ---|   Digito  |--->

    - Comentario
                    + regla:
                                            |<---------------|
                    -----| / |-----| / |----| Caracter ASCII | ---->

    - Cadena

    +regla:
-----| " |-----| indentificador o conjunto de caracteres |----| " | ---->

    - Caracter

+regla:
-----| ' |-----| indentificador o conjunto de caracteres |----| ' | ---->

    ** Generar un archivo aparte con la traducion del archivo cargado

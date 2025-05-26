import ply.lex as lex
import ply.yacc as yacc

# --- Análisis Léxico (Lexer) ---

# Palabras reservadas
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'int': 'INT',
    'char': 'CHAR',
    'float': 'FLOAT',
    'double': 'DOUBLE',
    'void': 'VOID',
    'return': 'RETURN',
    'include': 'INCLUDE',
    'stdio': 'STDIO' # Para el ejemplo, podríamos ser más genéricos con 'IDENTIFIER' pero para 'stdio.h' es útil.
}

# Tokens
tokens = [
    'ID',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUALS',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'GREATER',
    'LESS',
    'STRING_LITERAL',
    'HASH',
    'DOT' # Para 'stdio.h'
] + list(reserved.values())

# Reglas de expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_SEMICOLON = r';'
t_GREATER = r'>'
t_LESS = r'<'
t_HASH = r'\#'
t_DOT = r'\.'
t_STRING_LITERAL = r'\".*?\"'

# Un token para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica si es palabra reservada
    return t

# Un token para números enteros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# --- Análisis Sintáctico (Parser) ---

# Precedencia de operadores (si fuera necesario para expresiones más complejas)
# precedence = (
#     ('left', 'PLUS', 'MINUS'),
#     ('left', 'TIMES', 'DIVIDE'),
# )

# Reglas de la gramática
def p_program(p):
    '''
    program : includes program_elements
            | program_elements
    '''
    p[0] = ('program', p[1])

def p_includes(p):
    '''
    includes : include_directive
             | includes include_directive
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_include_directive(p):
    'include_directive : HASH INCLUDE LESS STDIO DOT ID GREATER'
    p[0] = ('include', f"<{p[4]}{p[5]}{p[6]}{p[7]}") # Reconstruye para 'stdio.h'

def p_program_elements(p):
    '''
    program_elements : function_definition
                     | program_elements function_definition
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_function_definition(p):
    '''
    function_definition : type ID LPAREN RPAREN LBRACE statements RBRACE
    '''
    p[0] = ('function_definition', p[1], p[2], p[6])

def p_type(p):
    '''
    type : INT
         | CHAR
         | FLOAT
         | DOUBLE
         | VOID
    '''
    p[0] = p[1]

def p_statements(p):
    '''
    statements : statement
               | statements statement
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''
    statement : declaration_statement
              | assignment_statement SEMICOLON
              | if_statement
              | for_statement
              | while_statement
              | return_statement
              | function_call SEMICOLON
    '''
    p[0] = p[1]

def p_declaration_statement(p):
    '''
    declaration_statement : type ID SEMICOLON
                          | type ID EQUALS expression SEMICOLON
    '''
    if len(p) == 4:
        p[0] = ('declaration', p[1], p[2])
    else:
        p[0] = ('declaration_init', p[1], p[2], p[4])


def p_assignment_statement(p):
    '''
    assignment_statement : ID EQUALS expression
    '''
    p[0] = ('assignment', p[1], p[3])

def p_expression(p):
    '''
    expression : NUMBER
               | ID
               | STRING_LITERAL
               | expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | LPAREN expression RPAREN
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = (p[2], p[1], p[3])

def p_if_statement(p):
    '''
    if_statement : IF LPAREN condition RPAREN LBRACE statements RBRACE
                 | IF LPAREN condition RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE
    '''
    if len(p) == 8:
        p[0] = ('if_statement', p[3], p[6])
    else:
        p[0] = ('if_else_statement', p[3], p[6], p[10])

def p_for_statement(p):
    '''
    for_statement : FOR LPAREN for_init SEMICOLON condition SEMICOLON for_update RPAREN LBRACE statements RBRACE
    '''
    p[0] = ('for_statement', p[3], p[5], p[7], p[10])

def p_for_init(p):
    '''
    for_init : declaration_statement
             | assignment_statement
             | empty
    '''
    p[0] = p[1]

def p_for_update(p):
    '''
    for_update : assignment_statement
               | function_call
               | empty
    '''
    p[0] = p[1]

def p_while_statement(p):
    '''
    while_statement : WHILE LPAREN condition RPAREN LBRACE statements RBRACE
    '''
    p[0] = ('while_statement', p[3], p[6])

def p_condition(p):
    '''
    condition : expression GREATER expression
              | expression LESS expression
              | expression
    '''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_return_statement(p):
    '''
    return_statement : RETURN expression SEMICOLON
    '''
    p[0] = ('return', p[2])

def p_function_call(p):
    '''
    function_call : ID LPAREN STRING_LITERAL RPAREN
    '''
    p[0] = ('function_call', p[1], p[3])


def p_empty(p):
    'empty :'
    pass

# Manejo de errores sintácticos
def p_error(p):
    if p:
        error_msg = f"Syntax error at '{p.value}' (type: {p.type}) at line {p.lineno}"
        print(error_msg)
    else:
        print("Syntax error: unexpected end of input.")


# Construir el parser
parser = yacc.yacc()

# --- Función de análisis ---

def analyze_content(content):
    errors = []
    detected_elements = {
        "funciones_mal_escritas": [],
        "estructuras_de_control": [],
        "asignacion_de_variables": []
    }

    lexer.lineno = 1
    lexer.input(content)

    try:
        # Intenta parsear el contenido
        parsed_tree = parser.parse(content, lexer=lexer)

        if parsed_tree:
            def traverse_tree(node):
                if isinstance(node, tuple):
                    node_type = node[0]

                    if node_type == 'function_definition':
                        func_name = node[2]
                        statements = node[3]
                        # Si no hay statements, podrías marcarla como sospechosa
                        if not statements:
                            detected_elements["funciones_mal_escritas"].append(f"{func_name} sin cuerpo")
                    elif node_type in ('if_statement', 'if_else_statement'):
                        detected_elements["estructuras_de_control"].append("if")
                    elif node_type == 'for_statement':
                        detected_elements["estructuras_de_control"].append("for")
                    elif node_type == 'while_statement':
                        detected_elements["estructuras_de_control"].append("while")
                    elif node_type == 'assignment':
                        detected_elements["asignacion_de_variables"].append(f"{node[1]} = {node[2]}")
                    
                    for item in node[1:]:
                        traverse_tree(item)

                elif isinstance(node, list):
                    for item in node:
                        traverse_tree(item)

            traverse_tree(parsed_tree)

    except Exception as e:
        errors.append(str(e))

    # Análisis textual adicional para errores que el parser no reporta detalladamente
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        # Detecta función mal escrita sin paréntesis (ej: main {})
        if "main" in line and "main(" not in line and "main " in line:
            errors.append(f"Línea {i}: posible función 'main' mal escrita (faltan paréntesis).")

        # Detecta declaraciones fuera de funciones (heurístico)
        if any(kw in line for kw in ['int ', 'char ', 'float ', 'double ', 'void ']) and line.strip().endswith(';') and "main" not in content:
            errors.append(f"Línea {i}: declaración posiblemente fuera de función.")

    return errors, detected_elements


    # Ahora, vamos a la parte de detectar errores de funciones mal escritas *específicamente*
    # fuera del parser de PLY para los casos que PLY no captura como "error de sintaxis"
    # pero que tú consideras "mal escritos".
    # En PLY, si la sintaxis no coincide, simplemente arroja un error.
    # Por ejemplo, si faltan (), la regla de p_function_definition no coincidirá y se generará un error.
    # Si faltan {}, la misma situación.

    # Para demostrar cómo podrías detectar esto si la gramática fuera más permisiva o si quisieras un mensaje más específico:
    # Si quieres detectar una función `main` sin `()`:
    if "main" in content and "main()" not in content:
        # Esto es una detección más simple basada en texto, no en el AST,
        # para ilustrar cómo podrías atrapar algo que el parser podría no marcar exactamente como "función mal escrita"
        # pero sí como un error de sintaxis general.
        errors.append("Error: función 'main' mal escrita (faltan paréntesis '()').")

    # Si quieres detectar bloques de código sin '{' o '}'
    # Esta es una detección más compleja ya que PLY ya manejaría esto como un error de sintaxis.
    # Si `if` no tiene `{`, la regla `if_statement` no coincidirá.
    # Si la definición de función no tiene `{`, la regla `function_definition` no coincidirá.

    if not errors and not detected_elements["estructuras_de_control"] and not detected_elements["asignacion_de_variables"]:
         # Aquí podrías añadir una comprobación más robusta si el árbol no se formó correctamente
         # y no hubo un error explícito del parser.
         # Por ejemplo, si el contenido es vacío o no tiene estructura C reconocible.
        pass # Si no hay errores reportados por PLY y no se detectó nada, podría significar un input inválido.


    return errors, detected_elements

# --- Ejemplo de uso con tu código C ---

if __name__ == "__main__":
    with open('hello.c', 'r') as file:
        codigo_c = file.read()
    print("Contenido del archivo hello.c:")
    print(codigo_c)
    # Simula la obtención del contenido de tu text edit
    # self.textEdit.toPlainText()
    contenido_text_edit = codigo_c

    print("--- Analizando el código C ---")
    errores_detectados, elementos_detectados = analyze_content(contenido_text_edit)

    if errores_detectados:
        print("Errores detectados:")
        for error in errores_detectados:
            print(f"- {error}")
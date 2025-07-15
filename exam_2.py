# ----------------- EJERCICIO 1 -----------------
# Este bloque resuelve el problema de la sopa de letras.
# Se define una clase con métodos para buscar palabras en todas las direcciones posibles dentro de una matriz de letras.

from typing import List, Tuple, Optional
from rich.console import Console      # Para imprimir en consola con formato y colores
from rich.table import Table          # Para mostrar tablas bonitas en consola
import pyodbc

# Creamos un objeto Console de rich para imprimir bonito en consola
console = Console()

class StringCleaner:
    @staticmethod
    def find_word_in_grid(grid: List[List[str]], word: str) -> Optional[List[Tuple[int, int]]]:
        """
        Busca una palabra en la sopa de letras en todas las direcciones posibles.
        Parámetros:
            grid: matriz de letras (lista de listas de strings, cada string es una letra)
            word: palabra a buscar (string)
        Retorna:
            Lista de coordenadas [(fila, columna), ...] si la palabra se encuentra,
            o None si no se encuentra.
        """
        # Definimos las 8 direcciones posibles: derecha, izquierda, abajo, arriba y diagonales
        directions = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if not (dx == 0 and dy == 0)]
        rows, cols = len(grid), len(grid[0]) if grid else 0
        word = word.lower()  # Convertimos la palabra a minúsculas para comparar sin importar mayúsculas

        # Recorremos cada celda de la matriz y cada dirección
        for i in range(rows):
            for j in range(cols):
                for dx, dy in directions:
                    coords = []
                    for k in range(len(word)):
                        # Calculamos la posición siguiente en la dirección (dx, dy)
                        x, y = i + dx * k, j + dy * k
                        # Verificamos que la posición esté dentro de la matriz y que la letra coincida
                        if 0 <= x < rows and 0 <= y < cols and grid[x][y].lower() == word[k]:
                            coords.append((x, y))
                        else:
                            break
                    if len(coords) == len(word):
                        # Si encontramos la palabra completa, devolvemos las coordenadas
                        return coords
        # Si no se encontró la palabra en ninguna dirección, devolvemos None
        return None

    @staticmethod
    def find_all_words_in_grid(grid: List[List[str]], word_list: List[str]) -> List[Tuple[str, Optional[List[Tuple[int, int]]]]]:
        """
        Busca todas las palabras de word_list en la sopa de letras.
        Parámetros:
            grid: matriz de letras
            word_list: lista de palabras a buscar
        Retorna:
            Lista de tuplas (palabra, coordenadas o None)
        """
        # Para cada palabra, busca su posición usando find_word_in_grid
        return [(word, StringCleaner.find_word_in_grid(grid, word)) for word in word_list]

# ----------------- EJERCICIO 2 -----------------
def obtener_palabras_sqlserver():
    # Conexión usando autenticación de Windows (Trusted_Connection)
    server = r'DESKTOP-AB8SO3I\SQLEXPRESS'
    database = 'examen2'
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM palabras")
    fila = cursor.fetchone()
    lenguajes = ["PYTHON", "Python 3.10", "Python", "PYTHON", " Python ","pyThOn", "PYtonh", "pytHon", "python3", "PYTHONISTA" ]

    # Creamos una tabla rich para mostrar los resultados
    result_table = Table(title="Resultados de palabras desde SQL Server", show_lines=True)
    result_table.add_column("Texto original", style="bold")
    result_table.add_column("Tipo de detección", style="bold green")
    result_table.add_column("Detalle", style="cyan")

    while fila:
        palabra = fila.texto if hasattr(fila, 'texto') else fila[0]
        tipo = ""
        detalle = ""

        # Detecta 'gato' con espacio adelante
        if palabra.lstrip().lower() == "gato" and palabra != "gato":
            tipo = "Espacio adelante"
            detalle = f"La encontré con espacio adelante: '{palabra}'"

        # Detecta lenguajes similares a Python y los convierte a 'PYTHON'
        elif any(palabra.strip().lower().startswith(lang.lower().replace(" ", "")) for lang in lenguajes):
            tipo = "Lenguaje similar a Python"
            detalle = f"Lenguaje similar detectado: '{palabra}' → 'PYTHON'"

        # Verifica si puede ser interpretado como número (sin convertirlo)
        elif palabra.isdigit():
            tipo = "Número"
            detalle = f"Valor numérico detectado: '{palabra}'"

        # Detecta palabra relacionada con agua (solo imprime 'clara' si aparece 'agua clara')
        elif palabra.lower() == "agua clara":
            tipo = "Agua"
            detalle = "Palabra relacionada con agua encontrada: 'clara'"

        # Detecta frase pacífica y alterna mayúsculas/minúsculas para dar efecto opuesto
        elif "cielo azul" in palabra.lower():
            tipo = "Frase pacífica"
            frase_opuesta = ""
            mayus = True
            for letra in palabra:
                if letra.isalpha():
                    frase_opuesta += letra.upper() if mayus else letra.lower()
                    mayus = not mayus
                else:
                    frase_opuesta += letra
            detalle = f"Frase pacífica transformada a efecto opuesto: '{frase_opuesta}'"

        # Detecta mención de dividir cadenas con "Función split()"
        elif "función split()" in palabra.lower():
            tipo = "Dividir cadenas"
            pos = palabra.lower().find("función split()")
            detalle = f"Mención de dividir cadenas encontrada en la posición {pos}: '{palabra}'"

        # Detecta frase "final" con residuos al final y los elimina
        elif palabra.lower().lstrip().startswith("final") and palabra.rstrip().lower() != "final":
            tipo = "Final con residuos"
            limpia = palabra.strip()
            detalle = f"Palabra final limpia y sin espacios al final: '{limpia}'"

        # Detecta la palabra "código limpio" con espacio al principio y la presenta como texto relevante
        elif palabra.strip().lower() == "código limpio" and palabra.startswith(" "):
            tipo = "Código limpio"
            texto_limpio = palabra.strip()
            detalle = f"Texto que parece vacío pero con info relevante escondida al principio: '{texto_limpio}'"

        else:
            tipo = "Sin detección especial"
            detalle = "-"

        result_table.add_row(palabra, tipo, detalle)
        fila = cursor.fetchone()
    conn.close()
    console.print(result_table)

if __name__ == "__main__":
    # ----------------- EJERCICIO 1 -----------------
    # Definimos la sopa de letras como una matriz de letras (copiada de la imagen del examen)
    grid = [
        ['f', 'j', 'f', 'b', 'm', 'x', 'o', 'm', 'n', 'u'],
        ['j', 'h', 's', 'x', 'a', 'o', 'n', 'r', 'o', 't'],
        ['j', 'u', 'n', 'h', 'r', 's', 'y', 'g', 'h', 'b'],
        ['b', 'w', 'l', 'e', 't', 'r', 'y', 'h', 't', 'v'],
        ['b', 'i', 'n', 'g', 'e', 'q', 'j', 'e', 'y', 'v'],
        ['x', 'x', 'w', 'u', 'l', 'a', 'q', 'x', 'p', 'l'],
        ['r', 'e', 'c', 'o', 'n', 'r', 'a', 'd', 'a', 'r'],
        ['o', 'n', 'c', 'e', 'l', 'o', 'f', 'y', 'j', 'n'],
        ['e', 'p', 'y', 't', 'r', 'e', 't', 'o', 'z', 'f'],
        ['o', 'z', 'u', 'l', 'c', 'l', 'a', 's', 'e', 'f'],
    ]

    # Lista de palabras a buscar en la sopa de letras
    palabras = "LETRA LUZ RETO CLASE RADAR PYTHON".split()

    # Mostramos la sopa de letras en formato tabla usando rich
    console.rule("[bold blue]EJERCICIO 1: Sopa de letras")
    table = Table(title="Sopa de Letras")
    for col in range(len(grid[0])):
        table.add_column(str(col), justify="center")
    for row in grid:
        table.add_row(*row)
    console.print(table)

    # Buscamos todas las palabras y mostramos si aparecen o no en una tabla
    result_table = Table(title="\nResultados de búsqueda", show_lines=True)
    result_table.add_column("Palabra", style="bold")
    result_table.add_column("¿Aparece?", style="bold green")
    result_table.add_column("Coordenadas", style="cyan")
    for palabra, _ in StringCleaner.find_all_words_in_grid(grid, palabras):
        palabra_sin_espacios = palabra.replace(" ", "")
        tiene_espacios = palabra != palabra_sin_espacios
        coords = StringCleaner.find_word_in_grid(grid, palabra_sin_espacios)
        # Mostrar específicamente la palabra 'gato' aunque tenga espacios
        if palabra_sin_espacios.lower() == "gato":
            if coords:
                result_table.add_row(
                    palabra,
                    "[green]SÍ (GATO)[/green]",
                    str(coords)
                )
                console.print(f"[yellow]Palabra original: '{palabra}'[/yellow]")
                console.print(f"[yellow]Palabra sin espacios: '{palabra_sin_espacios}'[/yellow]")
                console.print(f"[yellow]Coordenadas: {coords}[/yellow]")
            else:
                result_table.add_row(palabra, "[red]NO (GATO)[/red]", "-")
                console.print(f"[red]La palabra 'gato' no fue encontrada.[/red]")
        else:
            if coords:
                if tiene_espacios:
                    result_table.add_row(
                        palabra,
                        "[green]SÍ (con espacios en blanco)[/green]",
                        str(coords)
                    )
                    console.print(f"[yellow]Palabra original: '{palabra}'[/yellow]")
                    console.print(f"[yellow]Palabra sin espacios: '{palabra_sin_espacios}'[/yellow]")
                    console.print(f"[yellow]Coordenadas: {coords}[/yellow]")
                else:
                    result_table.add_row(palabra, "[green]SÍ[/green]", str(coords))
                    console.print(f"[green]Palabra encontrada: '{palabra}' en {coords}[/green]")
            else:
                result_table.add_row(palabra, "[red]NO[/red]", "-")
    console.print(result_table)

    # Permite búsqueda interactiva: el usuario puede escribir cualquier palabra para buscar en la sopa de letras
    while True:
        buscar = console.input("\n[bold yellow]Escribe una palabra para buscar en la sopa de letras (o 'salir' para terminar y pasar al ejercicio 2): [/]").strip()
        if buscar.lower() == "salir":
            print("\nSaliendo del EJERCICIO 1 y pasando al EJERCICIO 2...\n")
            break
        coords = StringCleaner.find_word_in_grid(grid, buscar)
        if coords:
            console.print(f"[green]La palabra '{buscar}' SÍ aparece en la sopa de letras en las posiciones: {coords}[/green]")
        else:
            console.print(f"[red]La palabra '{buscar}' NO aparece en la sopa de letras.[/red]")

    # ----------------- EJERCICIO 2 -----------------
    # Consulta y muestra las palabras de la base de datos SQL Server
    console.rule("[bold blue]EJERCICIO 2: Palabras desde SQL Server")
    try:
        obtener_palabras_sqlserver()  # Solo llama, no asignes a una variable
    except Exception as e:
        console.print(f"[red]Error al consultar la base de datos: {e}[/red]")
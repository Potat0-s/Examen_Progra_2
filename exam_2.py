# Importaciones necesarias para el funcionamiento del programa
from typing import List, Tuple, Optional
from rich.console import Console      # Para imprimir en consola con formato y colores
from rich.table import Table          # Para mostrar tablas bonitas en consola
import pyodbc                         # Para conectarse a bases de datos SQL Server

# Creamos un objeto Console de rich para imprimir bonito en consola
console = Console()

# ----------------- CLASE PARA SOPA DE LETRAS -----------------
class StringCleaner:
    def __init__(self):
        # Constructor vacío, se puede usar para inicializar atributos si se requiere en el futuro
        pass

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

# ----------------- CLASE PARA MANEJO DE SQL SERVER -----------------
class SQLServerManager:
    def __init__(self, server, database):
        # Constructor que recibe el servidor y la base de datos
        self.server = server
        self.database = database
        self.conn = None  # Aquí se guardará la conexión

    def conectar(self):
        # Realiza la conexión a SQL Server usando pyodbc
        self.conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'
        )
        return self.conn

    def obtener_palabras(self):
        # Obtiene todas las palabras de la tabla 'palabras'
        if not self.conn:
            self.conectar()
        cursor = self.conn.cursor()
        cursor.execute("SELECT texto FROM palabras")
        return cursor

    def cerrar(self):
        # Cierra la conexión si está abierta
        if self.conn:
            self.conn.close()

# ----------------- FUNCIÓN PARA PROCESAR PALABRAS DE SQL SERVER -----------------
def obtener_palabras_sqlserver():
    # Configuración de conexión
    server = r'DESKTOP-AB8SO3I\SQLEXPRESS'
    database = 'examen2'
    manager = SQLServerManager(server, database)
    cursor = manager.obtener_palabras()
    fila = cursor.fetchone()
    # Lista de variantes de "Python" para detectar similitudes
    lenguajes = ["PYTHON", "Python 3.10", "Python", "PYTHON", " Python ","pyThOn", "PYtonh", "pytHon", "python3", "PYTHONISTA" ]

    # Creamos una tabla rich para mostrar los resultados
    result_table = Table(title="Resultados de palabras desde SQL Server", show_lines=True)
    result_table.add_column("Texto original", style="bold")
    result_table.add_column("Tipo de detección", style="bold green")
    result_table.add_column("Detalle", style="cyan")

    # Procesamos cada fila obtenida de la base de datos
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

        # Detecta palabra relacionada con agua (solo imprime la palabra que sigue a 'agua')
        elif palabra.lower().startswith("agua "):
            tipo = "Agua"
            # Divide la frase y toma solo la palabra que sigue a "agua"
            segunda_palabra = palabra.strip().split(" ", 1)[1] if len(palabra.strip().split(" ", 1)) > 1 else ""
            detalle = f"Palabra relacionada con agua encontrada: '{segunda_palabra}'"

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
            # Si no se detecta ningún caso especial
            tipo = "Sin detección especial"
            detalle = "-"

        # Agrega la fila a la tabla de resultados
        result_table.add_row(palabra, tipo, detalle)
        fila = cursor.fetchone()
    # Cierra la conexión y muestra la tabla
    manager.cerrar()
    console.print(result_table)

# ----------------- CLASE PARA EL MENÚ PRINCIPAL -----------------
class MainMenu:
    def __init__(self):
        # Constructor que inicializa el objeto console
        self.console = console

    def mostrar(self):
        # Muestra el menú principal y gestiona la selección del usuario
        while True:
            self.console.rule("[bold blue]MENÚ PRINCIPAL")
            opcion = self.console.input(
                "[bold yellow]Selecciona una opción:\n"
                "1. Ejercicio 1: Sopa de letras\n"
                "2. Ejercicio 2: Palabras desde SQL Server\n"
                "3. Salir\n"
                "Opción: "
            ).strip()
            if opcion == "1":
                self.ejercicio1()
            elif opcion == "2":
                self.ejercicio2()
            elif opcion == "3":
                self.console.print("[bold green]¡Hasta luego![/bold green]")
                break
            else:
                self.console.print("[red]Opción no válida. Intenta de nuevo.[/red]")

    def ejercicio1(self):
        # Lógica para el ejercicio 1: Sopa de letras
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
        palabras = "LETRA LUZ RETO CLASE RADAR PYTHON".split()
        self.console.rule("[bold blue]EJERCICIO 1: Sopa de letras")
        table = Table(title="Sopa de Letras")
        # Agrega columnas a la tabla según el número de columnas en la sopa
        for col in range(len(grid[0])):
            table.add_column(str(col), justify="center")
        # Agrega cada fila de la sopa de letras a la tabla
        for row in grid:
            table.add_row(*row)
        self.console.print(table)
        # Tabla para mostrar los resultados de la búsqueda
        result_table = Table(title="\nResultados de búsqueda", show_lines=True)
        result_table.add_column("Palabra", style="bold")
        result_table.add_column("¿Aparece?", style="bold green")
        result_table.add_column("Coordenadas", style="cyan")
        # Busca cada palabra y muestra si aparece y sus coordenadas
        for palabra, _ in StringCleaner.find_all_words_in_grid(grid, palabras):
            palabra_sin_espacios = palabra.replace(" ", "")
            tiene_espacios = palabra != palabra_sin_espacios
            coords = StringCleaner.find_word_in_grid(grid, palabra_sin_espacios)
            if palabra_sin_espacios.lower() == "gato":
                if coords:
                    result_table.add_row(
                        palabra,
                        "[green]SÍ (GATO)[/green]",
                        str(coords)
                    )
                    self.console.print(f"[yellow]Palabra original: '{palabra}'[/yellow]")
                    self.console.print(f"[yellow]Palabra sin espacios: '{palabra_sin_espacios}'[/yellow]")
                    self.console.print(f"[yellow]Coordenadas: {coords}[/yellow]")
                else:
                    result_table.add_row(palabra, "[red]NO (GATO)[/red]", "-")
                    self.console.print(f"[red]La palabra 'gato' no fue encontrada.[/red]")
            else:
                if coords:
                    if tiene_espacios:
                        result_table.add_row(
                            palabra,
                            "[green]SÍ (con espacios en blanco)[/green]",
                            str(coords)
                        )
                        self.console.print(f"[yellow]Palabra original: '{palabra}'[/yellow]")
                        self.console.print(f"[yellow]Palabra sin espacios: '{palabra_sin_espacios}'[/yellow]")
                        self.console.print(f"[yellow]Coordenadas: {coords}[/yellow]")
                    else:
                        result_table.add_row(palabra, "[green]SÍ[/green]", str(coords))
                        self.console.print(f"[green]Palabra encontrada: '{palabra}' en {coords}[/green]")
                else:
                    result_table.add_row(palabra, "[red]NO[/red]", "-")
        self.console.print(result_table)
        # Permite al usuario buscar palabras adicionales en la sopa de letras
        while True:
            buscar = self.console.input("\n[bold yellow]Escribe una palabra para buscar en la sopa de letras (o 'salir' para regresar al menú): [/]").strip()
            if buscar.lower() == "salir":
                break
            coords = StringCleaner.find_word_in_grid(grid, buscar)
            if coords:
                self.console.print(f"[green]La palabra '{buscar}' SÍ aparece en la sopa de letras en las posiciones: {coords}[/green]")
            else:
                self.console.print(f"[red]La palabra '{buscar}' NO aparece en la sopa de letras.[/red]")

    def ejercicio2(self):
        # Lógica para el ejercicio 2: Consulta y procesamiento de palabras desde SQL Server
        self.console.rule("[bold blue]EJERCICIO 2: Palabras desde SQL Server")
        try:
            obtener_palabras_sqlserver()
        except Exception as e:
            self.console.print(f"[red]Error al consultar la base de datos: {e}[/red]")

# ----------------- BLOQUE PRINCIPAL -----------------
if __name__ == "__main__":
    # Crea el menú principal y lo muestra al usuario
    menu = MainMenu()
    menu.mostrar()

import random

# ─────────────────────────────────────────
#  SÍMBOLOS DEL MAPA
# # ─────────────────────────────────────────

S = 'S'   # Start  — punto de inicio
G = 'G'   # Goal   — meta a alcanzar
F = 'F'   # Frozen — celda caminable (hielo)
H = 'H'   # Hole   — hoyo, celda bloqueada

# ─────────────────────────────────────────
#  CONFIGURACIÓN DEL LABERINTO
# ─────────────────────────────────────────
FILAS            = 8
COLUMNAS         = 8
PROBABILIDAD_HOYO = 0.25   # 25 % de celdas libres se vuelven hoyos


class FrozenLake:
    """
    Entorno del laberinto Frozen Lake.

    Responsabilidades:
      - Generar un grid aleatorio de FILAS × COLUMNAS
      - Garantizar que siempre exista al menos un camino S → G
      - Exponer métodos que los algoritmos de búsqueda necesitan
        (get_neighbors, is_goal, get_start, get_goal)

    El entorno NO conoce BFS ni DFS; solo describe el mundo.
    """

    def __init__(self):
        self.filas    = FILAS
        self.columnas = COLUMNAS
        self.mapa     = []          # Lista de listas de caracteres
        self.inicio   = None        # Tupla (fila, col)
        self.meta     = None        # Tupla (fila, col)
        self.camino_garantizado = set()   # Celdas del camino base

        self._generar_mapa()        # Se construye al instanciar

    # ─────────────────────────────────────
    #  GENERACIÓN DEL MAPA
    # ─────────────────────────────────────

    def _generar_mapa(self):
        """
        Construye el laberinto en cuatro pasos:
          1. Grid vacío (todo F)
          2. Posicionar S (arriba-izq) y G (abajo-der) con variación aleatoria
          3. Trazar un camino garantizado S → G
          4. Rellenar el resto con H aleatoriamente (sin tocar el camino)
        """
        # Paso 1 — Grid lleno de celdas caminables
        self.mapa = [
            [F for _ in range(self.columnas)]
            for _ in range(self.filas)
        ]

        # Paso 2 — Posiciones de inicio y meta
        fila_s = random.randint(0, 1)
        col_s  = random.randint(0, 1)
        fila_g = random.randint(self.filas    - 2, self.filas    - 1)
        col_g  = random.randint(self.columnas - 2, self.columnas - 1)

        self.inicio = (fila_s, col_s)
        self.meta   = (fila_g, col_g)

        # Paso 3 — Camino garantizado (solo avanza ↓ o →)
        self._crear_camino_garantizado()

        # Paso 4 — Hoyos aleatorios fuera del camino
        self._rellenar_hoyos()

        # Paso 5 — Marcar S y G sobre el mapa ya construido
        self.mapa[fila_s][col_s] = S
        self.mapa[fila_g][col_g] = G

    def _crear_camino_garantizado(self):
        """
        Traza un camino aleatorio de inicio a meta
        moviéndose únicamente hacia abajo (↓) o hacia la derecha (→).

        Esto garantiza que el recorrido siempre progresa y llega a G
        sin bucles infinitos. La aleatoriedad en cada paso hace que
        el camino sea diferente en cada ejecución.
        """
        fila, col     = self.inicio
        fila_g, col_g = self.meta

        self.camino_garantizado = set()
        self.camino_garantizado.add((fila, col))

        while (fila, col) != (fila_g, col_g):
            movimientos_posibles = []

            if fila < fila_g:   # Todavía hay filas por bajar
                movimientos_posibles.append('abajo')
            if col < col_g:     # Todavía hay columnas por avanzar
                movimientos_posibles.append('derecha')

            movimiento = random.choice(movimientos_posibles)

            if movimiento == 'abajo':
                fila += 1
            else:
                col  += 1

            self.camino_garantizado.add((fila, col))

    def _rellenar_hoyos(self):
        """
        Recorre cada celda del grid y, con probabilidad
        PROBABILIDAD_HOYO, la convierte en hoyo (H).

        Reglas de protección:
          - Nunca se toca el camino garantizado
          - Nunca se toca el inicio ni la meta
        """
        for fila in range(self.filas):
            for col in range(self.columnas):
                # Proteger camino, inicio y meta
                if (fila, col) in self.camino_garantizado:
                    continue
                if (fila, col) in (self.inicio, self.meta):
                    continue

                if random.random() < PROBABILIDAD_HOYO:
                    self.mapa[fila][col] = H

    # ─────────────────────────────────────
    #  INTERFAZ PARA LOS ALGORITMOS
    # ─────────────────────────────────────

    def get_start(self):
        """Retorna la posición inicial como tupla (fila, col)."""
        return self.inicio

    def get_goal(self):
        """Retorna la posición de la meta como tupla (fila, col)."""
        return self.meta

    def is_goal(self, pos):
        """Retorna True si 'pos' es la celda meta."""
        return pos == self.meta

    def get_neighbors(self, pos):
        """
        Retorna la lista de vecinos válidos de 'pos'.

        Un vecino es válido si:
          - Está dentro de los límites del grid
          - No es un hoyo (H)

        Movimientos permitidos: ↑ ↓ ← →  (4 direcciones)
        """
        fila, col = pos
        vecinos   = []

        # (delta_fila, delta_col) para cada dirección
        direcciones = [
            (-1,  0),   # arriba
            ( 1,  0),   # abajo
            ( 0, -1),   # izquierda
            ( 0,  1),   # derecha
        ]

        for df, dc in direcciones:
            nf = fila + df
            nc = col  + dc

            # Dentro del grid
            if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                # No es un hoyo
                if self.mapa[nf][nc] != H:
                    vecinos.append((nf, nc))

        return vecinos

    def get_mapa(self):
        """
        Retorna una copia profunda del mapa.
        Se usa 'copia' para que los algoritmos no modifiquen
        accidentalmente el estado interno del entorno.
        """
        return [fila[:] for fila in self.mapa]

    # ─────────────────────────────────────
    #  UTILIDAD DE DEPURACIÓN
    # ─────────────────────────────────────

    def imprimir_mapa(self):
        """Imprime el mapa en consola (útil para depurar)."""
        for fila in self.mapa:
            print(' '.join(fila))
        print(f"\nInicio: {self.inicio}  |  Meta: {self.meta}")
        print(f"Celdas en camino garantizado: {len(self.camino_garantizado)}")


# ─────────────────────────────────────────
#  PRUEBA RÁPIDA (ejecutar solo este archivo)
# ─────────────────────────────────────────
if __name__ == "__main__":
    lago = FrozenLake()
    lago.imprimir_mapa()

    print("\nVecinos de la celda inicio:")
    for v in lago.get_neighbors(lago.get_start()):
        print(" ", v)
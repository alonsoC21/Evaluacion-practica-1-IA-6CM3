class Sokoban:
    """
    Entorno del puzzle Sokoban.

    Nivel predefinido 8x8:
      # = pared, espacio = suelo, . = meta, $ = caja, @ = jugador

    El estado es una tupla (pos_jugador, frozenset_cajas) — hashable y
    compatible con heapq a través de un contador de desempate.
    """

    _NIVEL = [
        "########",
        "#      #",
        "# . .  #",
        "# $ $  #",
        "#  @   #",
        "#      #",
        "#      #",
        "########",
    ]

    def __init__(self):
        self.nivel_base      = []
        self.metas           = frozenset()
        self.inicio_jugador  = None
        self.inicio_cajas    = frozenset()
        self._parsear_nivel()

    # ─────────────────────────────────────
    #  CONSTRUCCIÓN DEL MAPA
    # ─────────────────────────────────────

    def _parsear_nivel(self):
        cajas = []
        metas = []

        for r, fila in enumerate(self._NIVEL):
            fila_base = []
            for c, ch in enumerate(fila):
                if ch == '#':
                    fila_base.append('#')
                elif ch in ('.', '+', '*'):
                    fila_base.append('.')
                    metas.append((r, c))
                else:
                    fila_base.append(' ')

                if ch in ('@', '+'):
                    self.inicio_jugador = (r, c)
                if ch in ('$', '*'):
                    cajas.append((r, c))

            self.nivel_base.append(fila_base)

        self.metas          = frozenset(metas)
        self.inicio_cajas   = frozenset(cajas)
        self.filas          = len(self.nivel_base)
        self.columnas       = len(self.nivel_base[0])

    # ─────────────────────────────────────
    #  INTERFAZ PARA LOS ALGORITMOS
    # ─────────────────────────────────────

    def get_initial_state(self):
        """Estado inicial: (pos_jugador, frozenset_cajas)."""
        return (self.inicio_jugador, self.inicio_cajas)

    def is_goal(self, state):
        """Todas las cajas están sobre sus metas."""
        _, cajas = state
        return cajas == self.metas

    def heuristica(self, state):
        """
        Suma de distancias Manhattan de cada caja a su meta más cercana.
        Heurística admisible: nunca sobreestima el costo real.
        """
        _, cajas = state
        total = 0
        for caja in cajas:
            min_dist = min(
                abs(caja[0] - m[0]) + abs(caja[1] - m[1])
                for m in self.metas
            )
            total += min_dist
        return total

    def _es_deadlock_esquina(self, pos_caja):
        """
        Detecta si una caja recién empujada quedó atrapada en una esquina
        sin estar sobre ninguna meta (deadlock permanente).
        """
        if pos_caja in self.metas:
            return False
        r, c = pos_caja
        pared_arr = (r == 0) or (self.nivel_base[r - 1][c] == '#')
        pared_aba = (r == self.filas - 1) or (self.nivel_base[r + 1][c] == '#')
        pared_izq = (c == 0) or (self.nivel_base[r][c - 1] == '#')
        pared_der = (c == self.columnas - 1) or (self.nivel_base[r][c + 1] == '#')
        return (
            (pared_arr and pared_izq) or
            (pared_arr and pared_der) or
            (pared_aba and pared_izq) or
            (pared_aba and pared_der)
        )

    def get_neighbors(self, state):
        """
        Retorna lista de (nuevo_estado, costo=1) para cada movimiento válido.
        Maneja el empuje de cajas y descarta deadlocks de esquina.
        """
        jugador, cajas = state
        vecinos = []

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc       = jugador[0] + dr, jugador[1] + dc
            nueva_pos_j  = (nr, nc)

            if not (0 <= nr < self.filas and 0 <= nc < self.columnas):
                continue
            if self.nivel_base[nr][nc] == '#':
                continue

            if nueva_pos_j in cajas:
                # Intento de empujar la caja
                nr2, nc2      = nr + dr, nc + dc
                nueva_pos_c   = (nr2, nc2)

                if not (0 <= nr2 < self.filas and 0 <= nc2 < self.columnas):
                    continue
                if self.nivel_base[nr2][nc2] == '#':
                    continue
                if nueva_pos_c in cajas:
                    continue
                if self._es_deadlock_esquina(nueva_pos_c):
                    continue

                nuevas_cajas = frozenset((cajas - {nueva_pos_j}) | {nueva_pos_c})
                vecinos.append(((nueva_pos_j, nuevas_cajas), 1))
            else:
                vecinos.append(((nueva_pos_j, cajas), 1))

        return vecinos

    def get_nivel_base(self):
        """Devuelve una copia del mapa estático (paredes, suelos, metas)."""
        return [fila[:] for fila in self.nivel_base]

    def get_metas(self):
        return self.metas

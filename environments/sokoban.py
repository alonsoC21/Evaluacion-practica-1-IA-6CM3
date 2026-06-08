class Sokoban:
    """
    Nivel clásico de Sokoban 8x8.
    Estado: (posicion_jugador, frozenset(posiciones_cajas))
    """

    WALL  = '#'
    FLOOR = ' '
    GOAL  = '.'
    PLAYER = '@'
    BOX    = '$'
    BOX_ON_GOAL = '*'
    PLAYER_ON_GOAL = '+'

    # Mapa base (8 filas x 8 cols)
    # 3 cajas ($) en fila 3, 3 metas (.) en fila 2.
    # Jugador (@) en (4,2), ya alineado con la caja izquierda.
    # Solucion optima: U D R U D R U  (7 movimientos)
    # A* resuelve en ~101 iteraciones, Greedy en ~113.
    LEVEL = [
        "########",
        "#      #",
        "# ...  #",
        "# $$$  #",
        "# @    #",
        "#      #",
        "#      #",
        "########",
    ]

    DIRECTIONS = {
        'U': (-1,  0),
        'D': ( 1,  0),
        'L': ( 0, -1),
        'R': ( 0,  1),
    }

    def __init__(self):
        self.grid = [list(row) for row in self.LEVEL]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.walls  = frozenset()
        self.goals  = frozenset()
        self._initial_player = None
        self._initial_boxes  = frozenset()
        self._parse_level()

    def _parse_level(self):
        walls, goals, boxes = set(), set(), set()
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                if ch == self.WALL:
                    walls.add((r, c))
                elif ch in (self.GOAL, self.BOX_ON_GOAL, self.PLAYER_ON_GOAL):
                    goals.add((r, c))
                if ch in (self.PLAYER, self.PLAYER_ON_GOAL):
                    self._initial_player = (r, c)
                if ch in (self.BOX, self.BOX_ON_GOAL):
                    boxes.add((r, c))
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)
        self._initial_boxes = frozenset(boxes)

    def get_initial_state(self):
        return (self._initial_player, self._initial_boxes)

    def is_goal(self, state):
        _, boxes = state
        return boxes == self.goals

    def heuristic(self, state):
        """h(n): suma de distancia Manhattan minima de cada caja a su meta mas cercana."""
        _, boxes = state
        total = 0
        for box in boxes:
            if box not in self.goals:
                min_dist = min(
                    abs(box[0] - g[0]) + abs(box[1] - g[1])
                    for g in self.goals
                )
                total += min_dist
        return total

    def get_successors(self, state):
        """Devuelve lista de (nuevo_estado, costo_paso, accion)."""
        player, boxes = state
        successors = []
        for action, (dr, dc) in self.DIRECTIONS.items():
            nr, nc = player[0] + dr, player[1] + dc
            new_player = (nr, nc)
            if new_player in self.walls:
                continue
            if new_player in boxes:
                br, bc = nr + dr, nc + dc
                new_box_pos = (br, bc)
                if new_box_pos in self.walls or new_box_pos in boxes:
                    continue
                new_boxes = (boxes - {new_player}) | {new_box_pos}
                successors.append(((new_player, frozenset(new_boxes)), 1, action))
            else:
                successors.append(((new_player, boxes), 1, action))
        return successors

    def render_state(self, state):
        """Retorna la cuadricula como lista de listas de chars para dibujar."""
        player, boxes = state
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                pos = (r, c)
                if pos in self.walls:
                    row.append(self.WALL)
                elif pos == player:
                    row.append(self.PLAYER_ON_GOAL if pos in self.goals else self.PLAYER)
                elif pos in boxes:
                    row.append(self.BOX_ON_GOAL if pos in self.goals else self.BOX)
                elif pos in self.goals:
                    row.append(self.GOAL)
                else:
                    row.append(self.FLOOR)
            grid.append(row)
        return grid

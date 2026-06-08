import heapq


# ───────────────────────────────────────────────────────────────
#  A* — A-ESTRELLA  (Búsqueda informada óptima)
# ───────────────────────────────────────────────────────────────
def a_star(problema):
    """
    A* Search: expande nodos en orden de f(n) = g(n) + h(n).
    Garantiza el camino de costo mínimo si la heurística es admisible.

    Parámetro:
        problema — instancia de Sokoban

    Yields:
        Diccionario con estado visual en cada paso.
    """
    estado_inicial = problema.get_initial_state()
    nivel_base     = problema.get_nivel_base()
    metas          = problema.get_metas()

    h0       = problema.heuristica(estado_inicial)
    contador = 0                                       # Desempate en heapq
    # (f, id_único, g, estado)
    heap     = [(h0, contador, 0, estado_inicial)]
    visitados = {}                                     # estado → g mínimo
    pasos    = 0

    while heap:
        _, _, g, estado = heapq.heappop(heap)

        # Si ya procesamos este estado con igual o menor costo, saltarlo
        if estado in visitados:
            continue
        visitados[estado] = g
        pasos += 1

        jugador, cajas = estado
        h = problema.heuristica(estado)

        # ── ¿Meta alcanzada?
        if problema.is_goal(estado):
            yield {
                "nivel":      nivel_base,
                "jugador":    jugador,
                "cajas":      cajas,
                "metas":      metas,
                "visitados":  len(visitados),
                "frontera":   len(heap),
                "costo":      g,
                "heuristica": 0,
                "pasos":      pasos,
                "encontrado": True,
                "mensaje":    f"¡Solucion A*! Movs: {g} | Nodos: {len(visitados)}",
            }
            return

        # ── Yield: mostrar estado actual en pantalla
        yield {
            "nivel":      nivel_base,
            "jugador":    jugador,
            "cajas":      cajas,
            "metas":      metas,
            "visitados":  len(visitados),
            "frontera":   len(heap),
            "costo":      g,
            "heuristica": h,
            "pasos":      pasos,
            "encontrado": False,
            "mensaje":    f"A*: g={g} | h={h} | f={g + h}",
        }

        # ── Expandir vecinos
        for nuevo_estado, costo_mov in problema.get_neighbors(estado):
            if nuevo_estado not in visitados:
                nuevo_g = g + costo_mov
                nuevo_h = problema.heuristica(nuevo_estado)
                contador += 1
                heapq.heappush(heap, (nuevo_g + nuevo_h, contador, nuevo_g, nuevo_estado))

    # Cola vacía sin haber encontrado la meta
    jugador, cajas = estado_inicial
    yield {
        "nivel":      nivel_base,
        "jugador":    jugador,
        "cajas":      cajas,
        "metas":      metas,
        "visitados":  len(visitados),
        "frontera":   0,
        "costo":      0,
        "heuristica": h0,
        "pasos":      pasos,
        "encontrado": False,
        "mensaje":    "A*: No se encontro solucion.",
    }


# ───────────────────────────────────────────────────────────────
#  GREEDY — BÚSQUEDA VORAZ  (Mejor-primero por heurística)
# ───────────────────────────────────────────────────────────────
def greedy(problema):
    """
    Greedy Best-First Search: expande nodos en orden de h(n) únicamente.
    No garantiza optimalidad, pero suele ser más rápido que A*.

    Parámetro:
        problema — instancia de Sokoban

    Yields:
        Diccionario con estado visual en cada paso.
    """
    estado_inicial = problema.get_initial_state()
    nivel_base     = problema.get_nivel_base()
    metas          = problema.get_metas()

    h0       = problema.heuristica(estado_inicial)
    contador = 0
    # (h, id_único, estado)
    heap     = [(h0, contador, estado_inicial)]
    visitados = set()
    pasos    = 0

    while heap:
        h, _, estado = heapq.heappop(heap)

        if estado in visitados:
            continue
        visitados.add(estado)
        pasos += 1

        jugador, cajas = estado

        # ── ¿Meta alcanzada?
        if problema.is_goal(estado):
            yield {
                "nivel":      nivel_base,
                "jugador":    jugador,
                "cajas":      cajas,
                "metas":      metas,
                "visitados":  len(visitados),
                "frontera":   len(heap),
                "costo":      pasos,
                "heuristica": 0,
                "pasos":      pasos,
                "encontrado": True,
                "mensaje":    f"¡Solucion Voraz! Nodos: {len(visitados)}",
            }
            return

        # ── Yield: mostrar estado actual en pantalla
        yield {
            "nivel":      nivel_base,
            "jugador":    jugador,
            "cajas":      cajas,
            "metas":      metas,
            "visitados":  len(visitados),
            "frontera":   len(heap),
            "costo":      pasos,
            "heuristica": h,
            "pasos":      pasos,
            "encontrado": False,
            "mensaje":    f"Voraz: h={h} (solo heuristica)",
        }

        # ── Expandir vecinos (sin considerar g)
        for nuevo_estado, _ in problema.get_neighbors(estado):
            if nuevo_estado not in visitados:
                nuevo_h = problema.heuristica(nuevo_estado)
                contador += 1
                heapq.heappush(heap, (nuevo_h, contador, nuevo_estado))

    # Cola vacía sin solución
    jugador, cajas = estado_inicial
    yield {
        "nivel":      nivel_base,
        "jugador":    jugador,
        "cajas":      cajas,
        "metas":      metas,
        "visitados":  len(visitados),
        "frontera":   0,
        "costo":      0,
        "heuristica": h0,
        "pasos":      pasos,
        "encontrado": False,
        "mensaje":    "Voraz: No se encontro solucion.",
    }

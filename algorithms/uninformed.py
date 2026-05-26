from collections import deque

def _reconstruir_camino(padres, meta):
    """
    Función auxiliar compartida por BFS y DFS.
    """
    camino = []
    nodo_actual = meta

    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = padres[nodo_actual]

    camino.reverse()  
    return camino


def _estado_visual(mapa, visitados, frontera, pos_actual,
                   camino, encontrado, pasos, mensaje):
    """
    Función auxiliar que empaqueta todos los datos visuales
    en un diccionario limpio.
    """
    return {
        "mapa":       mapa,
        "visitados":  set(visitados),    # Copia para que no mute
        "frontera":   set(frontera),
        "camino":     list(camino),
        "pos_actual": pos_actual,
        "encontrado": encontrado,
        "pasos":      pasos,
        "mensaje":    mensaje,
    }


# ───────────────────────────────────────────────────────────────
#  BFS — BREADTH-FIRST SEARCH  (Búsqueda por Anchura)
# ───────────────────────────────────────────────────────────────
def bfs(problema):
    """
    Propiedad principal: GARANTIZA el camino más corto.

    Parámetro:
        problema — instancia de FrozenLake

    Yields:
        Diccionario con estado visual en cada paso.
    """
    inicio = problema.get_start()
    mapa   = problema.get_mapa()

    # Estructuras de BFS 
    cola      = deque([inicio])        
    visitados = set()                  
    padres    = {inicio: None}         
    pasos     = 0

    # Bucle principal 
    while cola:
        # Sacar el nodo más antiguo (izquierda de la cola = FIFO)
        pos_actual = cola.popleft()
        pasos += 1

        # Si ya lo procesamos antes, lo saltamos
        # (puede ocurrir si fue agregado a la cola varias veces)
        if pos_actual in visitados:
            continue

        visitados.add(pos_actual)

        # ── Yield: mostrar estado actual en pantalla
        yield _estado_visual(
            mapa       = mapa,
            visitados  = visitados,
            frontera   = list(cola),   # Nodos esperando en la cola
            pos_actual = pos_actual,
            camino     = [],
            encontrado = False,
            pasos      = pasos,
            mensaje    = f"BFS: Explorando {pos_actual}..."
        )

        # ¿Llego a la meta?
        if problema.is_goal(pos_actual):
            camino = _reconstruir_camino(padres, pos_actual)

            yield _estado_visual(
                mapa       = mapa,
                visitados  = visitados,
                frontera   = [],
                pos_actual = pos_actual,
                camino     = camino,
                encontrado = True,
                pasos      = pasos,
                mensaje    = f"¡Meta encontrada! Camino: {len(camino)} pasos"
            )
            return   # Fin del generador

        #Expandir vecinos
        for vecino in problema.get_neighbors(pos_actual):
            if vecino not in visitados and vecino not in padres:
                padres[vecino] = pos_actual   # Registrar de dónde vino
                cola.append(vecino)           # Agregar al final de la cola

    # Si la cola se vació sin encontrar la meta
    yield _estado_visual(
        mapa       = mapa,
        visitados  = visitados,
        frontera   = [],
        pos_actual = None,
        camino     = [],
        encontrado = False,
        pasos      = pasos,
        mensaje    = "BFS: No se encontró solución."
    )


# ───────────────────────────────────────────────────────────────
#  DFS — DEPTH-FIRST SEARCH  (Búsqueda por Profundidad)
# ───────────────────────────────────────────────────────────────
def dfs(problema):
    """
    Propiedad principal: No garantiza el camino más corto,
    pero usa menos memoria en laberintos grandes.

    Parámetro:
        problema — instancia de FrozenLake

    Yields:
        Diccionario con estado visual en cada paso.
    """
    inicio = problema.get_start()
    mapa   = problema.get_mapa()

    # Estructuras de DFS 
    pila      = [inicio]               
    visitados = set()
    padres    = {inicio: None}
    pasos     = 0

    # Bucle principal
    while pila:
        # Sacar el nodo más reciente (derecha de la pila = LIFO)
        pos_actual = pila.pop()       
        pasos += 1

        if pos_actual in visitados:
            continue

        visitados.add(pos_actual)

        # Yield: mostrar estado actual en pantalla
        yield _estado_visual(
            mapa       = mapa,
            visitados  = visitados,
            frontera   = list(pila),   
            pos_actual = pos_actual,
            camino     = [],
            encontrado = False,
            pasos      = pasos,
            mensaje    = f"DFS: Explorando {pos_actual}..."
        )

        # ¿Llego a la meta?
        if problema.is_goal(pos_actual):
            camino = _reconstruir_camino(padres, pos_actual)

            yield _estado_visual(
                mapa       = mapa,
                visitados  = visitados,
                frontera   = [],
                pos_actual = pos_actual,
                camino     = camino,
                encontrado = True,
                pasos      = pasos,
                mensaje    = f"¡Meta encontrada! Camino: {len(camino)} pasos"
            )
            return

        # Expandir vecinos 
        for vecino in problema.get_neighbors(pos_actual):
            if vecino not in visitados and vecino not in padres:
                padres[vecino] = pos_actual
                pila.append(vecino)    # Agregar al tope de la pila

    # Si la pila se vació sin encontrar la meta
    yield _estado_visual(
        mapa       = mapa,
        visitados  = visitados,
        frontera   = [],
        pos_actual = None,
        camino     = [],
        encontrado = False,
        pasos      = pasos,
        mensaje    = "DFS: No se encontró solución."
    )
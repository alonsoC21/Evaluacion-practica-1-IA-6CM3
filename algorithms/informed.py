import heapq

def a_star(problem):
    """
    A* para Sokoban.
    f(n) = g(n) + h(n)  — costo real + heuristica Manhattan.
    Hace yield de cada estado que saca de la frontera para visualizacion.
    """
    initial = problem.get_initial_state()
    h0 = problem.heuristic(initial)

    # (f, g, estado, camino)
    heap = [(h0, 0, initial, [])]
    visitados = {}      # estado -> g minimo visto
    abiertos = 1
    cerrados = 0

    yield {
        "estado": initial,
        "grid": problem.render_state(initial),
        "g": 0,
        "h": h0,
        "f": h0,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "accion": "Inicio",
        "mensaje": f"A* iniciado  h={h0}",
        "resuelto": False,
    }

    while heap:
        f, g, estado, camino = heapq.heappop(heap)
        abiertos = max(0, abiertos - 1)
        cerrados += 1

        if estado in visitados and visitados[estado] <= g:
            continue
        visitados[estado] = g

        h = problem.heuristic(estado)
        accion = camino[-1] if camino else "Inicio"

        if problem.is_goal(estado):
            yield {
                "estado": estado,
                "grid": problem.render_state(estado),
                "g": g,
                "h": 0,
                "f": g,
                "abiertos": abiertos,
                "cerrados": cerrados,
                "accion": accion,
                "mensaje": f"Solucion encontrada  pasos={g}",
                "resuelto": True,
                "camino": camino,
            }
            return

        yield {
            "estado": estado,
            "grid": problem.render_state(estado),
            "g": g,
            "h": h,
            "f": f,
            "abiertos": abiertos,
            "cerrados": cerrados,
            "accion": accion,
            "mensaje": f"Explorando  g={g}  h={h}  f={f}",
            "resuelto": False,
        }

        for sucesor, costo, mov in problem.get_successors(estado):
            ng = g + costo
            if sucesor not in visitados or visitados[sucesor] > ng:
                nh = problem.heuristic(sucesor)
                heapq.heappush(heap, (ng + nh, ng, sucesor, camino + [mov]))
                abiertos += 1

    yield {
        "estado": initial,
        "grid": problem.render_state(initial),
        "g": 0, "h": 0, "f": 0,
        "abiertos": 0,
        "cerrados": cerrados,
        "accion": "-",
        "mensaje": "No se encontro solucion",
        "resuelto": False,
    }


def greedy(problem):
    """
    Busqueda voraz (Greedy Best-First).
    f(n) = h(n)  — solo la heuristica, ignora el costo real.
    """
    initial = problem.get_initial_state()
    h0 = problem.heuristic(initial)

    heap = [(h0, initial, [])]
    visitados = set()
    abiertos = 1
    cerrados = 0

    yield {
        "estado": initial,
        "grid": problem.render_state(initial),
        "g": 0,
        "h": h0,
        "f": h0,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "accion": "Inicio",
        "mensaje": f"Greedy iniciado  h={h0}",
        "resuelto": False,
    }

    while heap:
        h, estado, camino = heapq.heappop(heap)
        abiertos = max(0, abiertos - 1)

        if estado in visitados:
            continue
        visitados.add(estado)
        cerrados += 1

        accion = camino[-1] if camino else "Inicio"

        if problem.is_goal(estado):
            yield {
                "estado": estado,
                "grid": problem.render_state(estado),
                "g": len(camino),
                "h": 0,
                "f": 0,
                "abiertos": abiertos,
                "cerrados": cerrados,
                "accion": accion,
                "mensaje": f"Solucion encontrada  pasos={len(camino)}",
                "resuelto": True,
                "camino": camino,
            }
            return

        yield {
            "estado": estado,
            "grid": problem.render_state(estado),
            "g": len(camino),
            "h": h,
            "f": h,
            "abiertos": abiertos,
            "cerrados": cerrados,
            "accion": accion,
            "mensaje": f"Explorando  h={h}",
            "resuelto": False,
        }

        for sucesor, _, mov in problem.get_successors(estado):
            if sucesor not in visitados:
                nh = problem.heuristic(sucesor)
                heapq.heappush(heap, (nh, sucesor, camino + [mov]))
                abiertos += 1

    yield {
        "estado": initial,
        "grid": problem.render_state(initial),
        "g": 0, "h": 0, "f": 0,
        "abiertos": 0,
        "cerrados": cerrados,
        "accion": "-",
        "mensaje": "No se encontro solucion",
        "resuelto": False,
    }

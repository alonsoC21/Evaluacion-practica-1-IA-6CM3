def hill_climbing(problem):
    """
    Algoritmo (Steepest-Ascent Hill Climbing).
    Recibe una instancia del problema y usa 'yield'
    para permitir la animación paso a paso en Pygame.
    """
    # 1. Obtener el estado inicial aleatorio y evaluar su costo (ataques)
    current_state = problem.get_initial_state()
    current_cost = problem.get_attacks(current_state)

    # Entregamos el estado inicial a la vista para que lo dibuje
    yield {
        "tablero": current_state, 
        "ataques": current_cost, 
        "mensaje": "Estado Inicial"
    }

    while True:
        # Si ya es la meta (0 ataques), terminamos con éxito
        if problem.is_goal(current_state):
            yield {
                "tablero": current_state, 
                "ataques": current_cost, 
                "mensaje": "¡Solución Encontrada (Óptimo Global)!"
            }
            break

        # 2. Generar todos los estados vecinos
        neighbors = problem.get_successors(current_state)
        
        # Encontrar el mejor vecino (el que tenga menos ataques)
        best_neighbor = None
        best_cost = float('inf')

        for neighbor in neighbors:
            cost = problem.get_attacks(neighbor)
            if cost < best_cost:
                best_cost = cost
                best_neighbor = neighbor

        # 3. Criterio de parada: 
        # Si el mejor vecino NO es estrictamente mejor que mi estado actual,
        # significa que nos hemos atascado.
        if best_cost >= current_cost:
            yield {
                "tablero": current_state, 
                "ataques": current_cost, 
                "mensaje": "Atascado en un Óptimo Local"
            }
            break

        # 4. Nos movemos al mejor vecino
        current_state = best_neighbor
        current_cost = best_cost

        # Entregamos el nuevo estado para que la interfaz lo anime
        yield {
            "tablero": current_state, 
            "ataques": current_cost, 
            "mensaje": f"Buscando... (Ataques: {current_cost})"
        }
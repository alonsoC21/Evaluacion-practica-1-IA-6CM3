import math
import random
def hill_climbing(problem):
    """
    Algoritmo (Steepest-Ascent Hill Climbing).
    Recibe una instancia del problema y usa 'yield'
    para permitir la animación paso a paso en Pygame.
    """
    # 1. Obtener el estado inicial aleatorio y evaluar su costo (ataques)
    current_state = problem.get_initial_state()
    current_cost = problem.get_attacks(current_state)

    # Se entrega el estado inicial a la vista para que lo dibuje
    yield {
        "tablero": current_state, 
        "ataques": current_cost, 
        "mensaje": "Estado Inicial"
    }

    while True:
        # Si ya es la meta (0 ataques), acaba con exito
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

def simulated_annealing(problem, initial_temp=100.0, cooling_rate=0.95):
    """
    Algoritmo de Recocido Simulado.
    Utiliza una temperatura que desciende gradualmente para permitir
    movimientos subóptimos y escapar de mínimos locales.
    """
    current_state = problem.get_initial_state()
    current_cost = problem.get_attacks(current_state)
    temp = initial_temp

    yield {
        "tablero": current_state, 
        "ataques": current_cost, 
        "mensaje": f"Inicio SA - Temp: {temp:.1f}"
    }

    # El ciclo continúa mientras la temperatura sea relevante
    while temp > 0.1:
        if problem.is_goal(current_state):
            yield {
                "tablero": current_state, 
                "ataques": current_cost, 
                "mensaje": "¡Solución Encontrada (Óptimo Global)!"
            }
            return # Terminamos exitosamente

        # 1. En Recocido Simulado evaluamos un vecino al azar, NO todos
        neighbors = problem.get_successors(current_state)
        next_state = random.choice(neighbors)
        next_cost = problem.get_attacks(next_state)

        # 2. Calcular la diferencia de costo (Delta E)
        # Como queremos MINIMIZAR, un delta_e > 0 significa que el vecino es MEJOR
        delta_e = current_cost - next_cost

        # 3. Decidir si nos movemos al vecino
        if delta_e > 0:
            # Siempre aceptamos una mejora
            current_state = next_state
            current_cost = next_cost
            msg = f"Mejora - Temp: {temp:.1f}"
        else:
            # Si es peor, lo aceptamos con una probabilidad basada en la fórmula
            probabilidad_aceptacion = math.exp(delta_e / temp)
            if random.random() < probabilidad_aceptacion:
                current_state = next_state
                current_cost = next_cost
                msg = f"Empeora (Aceptado) - Temp: {temp:.1f}"
            else:
                msg = f"Empeora (Rechazado) - Temp: {temp:.1f}"

        # 4. Enfriar el sistema
        temp *= cooling_rate

        yield {
            "tablero": current_state, 
            "ataques": current_cost, 
            "mensaje": msg
        }

    # Si el ciclo termina por baja temperatura y no halló solución
    if not problem.is_goal(current_state):
        yield {
            "tablero": current_state, 
            "ataques": current_cost, 
            "mensaje": "Fin (Enfriado). Atascado."
        }
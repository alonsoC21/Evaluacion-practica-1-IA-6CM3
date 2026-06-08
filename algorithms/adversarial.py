import math

def alpha_beta_pruning(problem, initial_state=None):
    """
    Algoritmo Minimax con Poda Alfa-Beta adaptado con generadores.
    La IA es el jugador Max ('X') y el oponente es Min ('O').
    """
    if initial_state is None:
        state = problem.get_initial_state()
    else:
        state = initial_state

    # --- FUNCIÓN MAXIMIZADORA ---
    def max_value(state, alpha, beta, depth):
        if problem.is_terminal(state):
            val = problem.evaluate(state)
            yield {"tablero": state, "mensaje": f"Terminal (Max). Eval: {val}", "alfa": alpha, "beta": beta}
            return val
        
        v = -math.inf
        for move, successor in problem.get_successors(state, 'X'):
            # Mostramos el nodo que estamos explorando
            yield {"tablero": successor, "mensaje": f"Max explorando. Prof: {depth}", "alfa": alpha, "beta": beta}
            
            # Llamada recursiva a Min (usando yield from)
            val_sucesor = yield from min_value(successor, alpha, beta, depth + 1)
            v = max(v, val_sucesor)
            
            # Condición de Poda Beta
            if v >= beta:
                yield {"tablero": successor, "mensaje": f"¡Poda Beta! v({v}) >= beta({beta})", "alfa": alpha, "beta": beta}
                return v
            
            alpha = max(alpha, v)
            
        return v

    # --- FUNCIÓN MINIMIZADORA ---
    def min_value(state, alpha, beta, depth):
        if problem.is_terminal(state):
            val = problem.evaluate(state)
            yield {"tablero": state, "mensaje": f"Terminal (Min). Eval: {val}", "alfa": alpha, "beta": beta}
            return val
        
        v = math.inf
        for move, successor in problem.get_successors(state, 'O'):
            yield {"tablero": successor, "mensaje": f"Min explorando. Prof: {depth}", "alfa": alpha, "beta": beta}
            
            
            val_sucesor = yield from max_value(successor, alpha, beta, depth + 1)
            v = min(v, val_sucesor)           
            # Condición de Poda Alfa
            if v <= alpha:
                yield {"tablero": successor, "mensaje": f"¡Poda Alfa! v({v}) <= alfa({alpha})", "alfa": alpha, "beta": beta}
                return v
            
            beta = min(beta, v)
            
        return v

    # --- INICIO DE LA BÚSQUEDA ---
    yield {"tablero": state, "mensaje": "Iniciando Árbol Alfa-Beta...", "alfa": -math.inf, "beta": math.inf}
    
    mejor_valor = yield from max_value(state, -math.inf, math.inf, 0)
    
    yield {"tablero": state, "mensaje": f"Búsqueda finalizada. X espera utilidad de: {mejor_valor}", "alfa": "-", "beta": "-"}
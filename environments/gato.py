class TicTacToe:
    def __init__(self):
        self.size = 9

    def get_initial_state(self):
        """
        Retorna un tablero parcialmente lleno para evitar que la animación 
        tarde horas en evaluar los cientos de miles de nodos iniciales.
        """
        return ['X', 'O', ' ', 
                'X', 'O', ' ', 
                ' ', ' ', 'X']

    def get_successors(self, state, player):
        """
        Genera los tableros resultantes de todos los movimientos válidos.
        """
        successors = []
        for i in range(self.size):
            if state[i] == ' ':
                new_state = list(state)
                new_state[i] = player
                successors.append((i, new_state))
        return successors

    def check_winner(self, state):
        """
        Verifica todas las líneas de victoria posibles.
        """
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Filas horizontales
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columnas verticales
            [0, 4, 8], [2, 4, 6]             # Diagonales
        ]
        for condition in win_conditions:
            a, b, c = condition
            if state[a] != ' ' and state[a] == state[b] == state[c]:
                return state[a]
        return None

    def is_terminal(self, state):
        """
        El juego termina si hay un ganador o si no hay casillas vacías (empate).
        """
        return self.check_winner(state) is not None or ' ' not in state

    def evaluate(self, state):
        """
        Función de utilidad. Asumimos que la IA siempre juega con 'X' (Maximizador).
        10 si gana X, -10 si gana O, 0 si es empate.
        """
        winner = self.check_winner(state)
        if winner == 'X':
            return 10
        elif winner == 'O':
            return -10
        return 0
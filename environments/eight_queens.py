import random

class EightQueens:
    def __init__(self, size=8):
        self.size = size

    def get_initial_state(self):
        """
        Genera un estado inicial aleatorio.
        Coloca exactamente una reina por columna en una fila al azar.
        """
        return [random.randint(0, self.size - 1) for _ in range(self.size)]

    def get_attacks(self, state):
        """
        Función Heurística h(n): Calcula el número total de pares de reinas que se atacan.
        Un estado meta (ganador) tendrá exactamente 0 ataques.
        """
        attacks = 0
        for i in range(self.size):
            for j in range(i + 1, self.size):
                # Choque en la misma fila
                if state[i] == state[j]:
                    attacks += 1
                # Choque en la misma diagonal
                elif abs(state[i] - state[j]) == abs(i - j):
                    attacks += 1
        return attacks

    def is_goal(self, state):
        """
        Verifica si el estado actual es la solución (0 ataques).
        """
        return self.get_attacks(state) == 0

    def get_successors(self, state):
        """
        Genera todos los estados vecinos posibles.
        Para las 8 reinas, un vecino se genera moviendo una sola reina
        a una fila diferente dentro de su misma columna.
        """
        successors = []
        for col in range(self.size):
            for row in range(self.size):
                # Solo se genera el estado si la reina realmente cambia de fila
                if state[col] != row:
                    # hace una copia del estado actual
                    new_state = list(state)
                    # se mueve la reina en esta columna a la nueva fila
                    new_state[col] = row
                    successors.append(new_state)
        return successors
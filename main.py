import pygame
import sys
import time
import os

from environments.eight_queens import EightQueens
from environments.eight_queens import EightQueens
from algorithms.local import hill_climbing, simulated_annealing

# --- Imports: No informado 
from environments.frozen_lake import FrozenLake
from algorithms.uninformed import bfs, dfs

# --- CONFIGURACIÓN VISUAL ---
WIDTH = 600
HEIGHT = 750     
TABLERO_Y = 100   

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLUE = (50, 150, 255)
GREEN = (50, 200, 50)
RED = (255, 50, 50)

MENU_DATA = {
    "Frozen Lake (No Informada)": ["BFS (Anchura)", "DFS (Profundidad)"],
    "Sokoban (Informada)": ["A-Estrella (A*)", "Voraz (Greedy)"],
    "8 Reinas (Local)": ["Hill Climbing", "Recocido Simulado"],
    "Gato (Adversaria)": ["Minimax", "Poda Alfa-Beta"]
}


# -- Configuracion visual - No informado 
LIGHT_BLUE  = (100, 180, 255)   # Celdas visitadas
YELLOW      = (255, 230, 100)   # Frontera activa
ORANGE      = (255, 140,   0)   # Nodo actual
DARK_RED    = (180,  50,  50)   # Hoyos
GOLD        = (255, 200,   0)   # Meta


# --- FUNCIONES DE INTERFAZ ---
def dibujar_boton(screen, font, text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = DARK_GRAY if rect.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def dibujar_reinas(screen, state_dict, font_info, font_title, imagen_reina):
    if not state_dict or "tablero" not in state_dict:
        return

    tablero = state_dict["tablero"]
    tamano_celda = WIDTH // 8

    # 1. Dibujar Panel Superior (Mensajes y Ataques)
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))
    texto_ataques = font_title.render(f"Ataques (Costo): {state_dict['ataques']}", True, RED)
    texto_msg = font_info.render(state_dict['mensaje'], True, BLACK)
    screen.blit(texto_ataques, (WIDTH//2 - texto_ataques.get_width()//2, 20))
    screen.blit(texto_msg, (WIDTH//2 - texto_msg.get_width()//2, 60))

    # 2. Dibujar el tablero de 64 casillas
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            rect = pygame.Rect(col * tamano_celda, TABLERO_Y + (row * tamano_celda), tamano_celda, tamano_celda)
            pygame.draw.rect(screen, color, rect)
            
            # 3. DIBUJAR LA REINA
            if tablero[col] == row:
                if imagen_reina:
                    img_x = rect.x + (tamano_celda - imagen_reina.get_width()) // 2
                    img_y = rect.y + (tamano_celda - imagen_reina.get_height()) // 2
                    screen.blit(imagen_reina, (img_x, img_y))
                else:
                    # Plan de respaldo: Círculo azul si no hay imagen
                    pygame.draw.circle(screen, BLUE, rect.center, tamano_celda // 3)
                    pygame.draw.circle(screen, BLACK, rect.center, tamano_celda // 3, 2)

    # Separador visual
    pygame.draw.line(screen, BLACK, (0, TABLERO_Y + 600), (WIDTH, TABLERO_Y + 600), 2)

# -- Funciones de visualización para algoritmos no informados (BFS, DFS) ---
def dibujar_frozen_lake(screen, estado_dict, font_info, font_title):
    """
    Dibuja el laberinto Frozen Lake con su estado visual actual.
    Recibe el diccionario que yieldeó el algoritmo.
    """
    if not estado_dict or "mapa" not in estado_dict:
        return

    mapa       = estado_dict["mapa"]
    visitados  = estado_dict["visitados"]
    frontera   = estado_dict["frontera"]
    camino     = set(estado_dict["camino"])
    pos_actual = estado_dict["pos_actual"]
    encontrado = estado_dict["encontrado"]
    pasos      = estado_dict["pasos"]
    mensaje    = estado_dict["mensaje"]

    filas    = len(mapa)
    columnas = len(mapa[0])

    # Tamaño de cada celda para que el grid quepa en WIDTH=600
    tamano_celda = WIDTH // columnas   # 600 // 8 = 75px

    # ── 1. Panel superior (información) ────────────────────────
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))

    # Título con algoritmo activo
    color_titulo = GREEN if encontrado else BLUE
    titulo = font_title.render(mensaje, True, color_titulo)
    screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 15))

    # Contador de pasos y visitados
    info = font_info.render(
        f"Pasos: {pasos}  |  Visitados: {len(visitados)}", True, BLACK
    )
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 60))

    # ── 2. Dibujar el grid celda por celda ─────────────────────
    for fila in range(filas):
        for col in range(columnas):
            celda    = mapa[fila][col]
            pos      = (fila, col)
            rect     = pygame.Rect(
                col  * tamano_celda,
                TABLERO_Y + fila * tamano_celda,
                tamano_celda,
                tamano_celda
            )

            # ── Determinar color de fondo ───────────────────────
            # Prioridad: camino > actual > frontera > visitado > tipo celda
            if pos in camino:
                color_fondo = GREEN
            elif pos == pos_actual:
                color_fondo = ORANGE
            elif pos in frontera:
                color_fondo = YELLOW
            elif pos in visitados:
                color_fondo = LIGHT_BLUE
            elif celda == 'H':
                color_fondo = DARK_RED
            elif celda == 'S':
                color_fondo = GREEN
            elif celda == 'G':
                color_fondo = GOLD
            else:
                color_fondo = WHITE

            # Dibujar fondo de celda
            pygame.draw.rect(screen, color_fondo, rect)
            # Borde de celda
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)

            # ── Dibujar letra de la celda ───────────────────────
            if celda in ('S', 'G', 'H'):
                color_letra = WHITE if celda == 'H' else BLACK
                letra = font_info.render(celda, True, color_letra)
                screen.blit(
                    letra,
                    (rect.centerx - letra.get_width()  // 2,
                     rect.centery - letra.get_height() // 2)
                )

    # ── 3. Separador visual ─────────────────────────────────────
    pygame.draw.line(
        screen, BLACK,
        (0, TABLERO_Y + filas * tamano_celda),
        (WIDTH, TABLERO_Y + filas * tamano_celda),
        2
    )


# --- BUCLE PRINCIPAL ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizador de Algoritmos IA")
    
    font_title = pygame.font.SysFont(None, 40)
    font_button = pygame.font.SysFont(None, 28)
    font_info = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()
    
    try:
        ruta_imagen = os.path.join("assets", "reina.png")
        img_original = pygame.image.load(ruta_imagen).convert_alpha()
        nuevo_tamano = int((WIDTH // 8) * 1)
        imagen_reina = pygame.transform.scale(img_original, (nuevo_tamano, nuevo_tamano))
    except (pygame.error, FileNotFoundError):
        print("Aviso: No se encontró 'assets/reina.png'. Usando círculos por defecto.")

    estado = "MENU_PROBLEMA"
    problema_seleccionado = None
    algoritmo_seleccionado = None

    generador_algoritmo = None
    estado_actual = None
    ultimo_paso_tiempo = 0
    tiempo_entre_pasos = 0.8  # Un poco más rápido para dar dinamismo

    running = True
    while running:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        tiempo_actual = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    estado = "MENU_PROBLEMA"

        if estado == "MENU_PROBLEMA":
            titulo = font_title.render("Selecciona un Problema", True, BLACK)
            screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))
            
            y_offset = 150
            for problema in MENU_DATA.keys():
                btn = dibujar_boton(screen, font_button, problema, WIDTH//2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    problema_seleccionado = problema
                    estado = "MENU_ALGORITMO"
                y_offset += 80

        elif estado == "MENU_ALGORITMO":
            titulo = font_title.render("Selecciona el Algoritmo", True, BLACK)
            subtitulo = font_button.render(f"Problema: {problema_seleccionado}", True, BLUE)
            screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))
            screen.blit(subtitulo, (WIDTH//2 - subtitulo.get_width()//2, 100))
            
            y_offset = 180
            for algoritmo in MENU_DATA[problema_seleccionado]:
                btn = dibujar_boton(screen, font_button, algoritmo, WIDTH//2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    algoritmo_seleccionado = algoritmo
                    
                    if problema_seleccionado == "8 Reinas (Local)":
                        problema = EightQueens()
                        if algoritmo_seleccionado == "Hill Climbing":
                            generador_algoritmo = hill_climbing(problema)
                        elif algoritmo_seleccionado == "Recocido Simulado":
                            generador_algoritmo = simulated_annealing(problema)
                            
                        try:
                            estado_actual = next(generador_algoritmo)
                        except StopIteration:
                            pass
                    
                    # Conexion no informado con algoritmos BFS y DFS
                    if problema_seleccionado == "Frozen Lake (No Informada)":
                        problema = FrozenLake()
                        if algoritmo_seleccionado == "BFS (Anchura)":
                            generador_algoritmo = bfs(problema)
                        elif algoritmo_seleccionado == "DFS (Profundidad)":
                            generador_algoritmo = dfs(problema)

                        try:
                            estado_actual = next(generador_algoritmo)
                        except StopIteration:
                            pass
                    estado = "VISUALIZACION"
                y_offset += 80
                
            btn_back = dibujar_boton(screen, font_button, "Volver", 20, 20, 100, 40, mouse_pos)
            if btn_back.collidepoint(mouse_pos) and click:
                estado = "MENU_PROBLEMA"

        elif estado == "VISUALIZACION":
            if problema_seleccionado == "8 Reinas (Local)":
                dibujar_reinas(screen, estado_actual, font_info, font_title, imagen_reina)
                
                # Avanzar algoritmo automáticamente
                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                    except StopIteration:
                        generador_algoritmo = None

                # --- 3. DIBUJAR PANEL INFERIOR Y BOTONES ---
                # Fondo del panel inferior
                pygame.draw.rect(screen, WHITE, (0, TABLERO_Y + 600, WIDTH, HEIGHT - (TABLERO_Y + 600)))
                
                # Botón de Reintentar (Izquierda)
                btn_retry = dibujar_boton(screen, font_button, "Reintentar", 60, HEIGHT - 45, 200, 35, mouse_pos)
                if btn_retry.collidepoint(mouse_pos) and click:
                    if problema_seleccionado == "8 Reinas (Local)":
                        problema = EightQueens()
                        if algoritmo_seleccionado == "Hill Climbing":
                            generador_algoritmo = hill_climbing(problema)
                        elif algoritmo_seleccionado == "Recocido Simulado":
                            generador_algoritmo = simulated_annealing(problema)
                            
                        try:
                            estado_actual = next(generador_algoritmo)
                        except StopIteration:
                            pass
                # Botón de Volver (Derecha)
                btn_back = dibujar_boton(screen, font_button, "Volver al Menú", 340, HEIGHT - 45, 200, 35, mouse_pos)
                if btn_back.collidepoint(mouse_pos) and click:
                    estado = "MENU_PROBLEMA"
 
            # ── Frozen Lake ────────────────────────
            elif problema_seleccionado == "Frozen Lake (No Informada)":
                dibujar_frozen_lake(screen, estado_actual, font_info, font_title)
 
                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                    except StopIteration:
                        generador_algoritmo = None
 
                pygame.draw.rect(screen, WHITE, (0, HEIGHT - 60, WIDTH, 60))
 
                btn_retry = dibujar_boton(screen, font_button, "Reintentar", 60, HEIGHT - 45, 200, 35, mouse_pos)
                if btn_retry.collidepoint(mouse_pos) and click:
                    problema = FrozenLake()
                    if algoritmo_seleccionado == "BFS (Anchura)":
                        generador_algoritmo = bfs(problema)
                    elif algoritmo_seleccionado == "DFS (Profundidad)":
                        generador_algoritmo = dfs(problema)
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                    except StopIteration:
                        pass
 
                btn_back = dibujar_boton(screen, font_button, "Volver al Menú", 340, HEIGHT - 45, 200, 35, mouse_pos)
                if btn_back.collidepoint(mouse_pos) and click:
                    estado = "MENU_PROBLEMA"
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

import pygame
import sys
import time
import os

# --- Imports: Local
from environments.eight_queens import EightQueens
from algorithms.local import hill_climbing, simulated_annealing

# --- Imports: No informado
from environments.frozen_lake import FrozenLake
from algorithms.uninformed import bfs, dfs

# --- Imports: Informado ---
from environments.sokoban import Sokoban
from algorithms.informed import a_star, greedy

# --- Imports: Adversaria ---
from environments.gato import TicTacToe
from algorithms.adversarial import alpha_beta_pruning

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

# -- Configuracion visual - No informado 
LIGHT_BLUE  = (100, 180, 255)   # Celdas visitadas
YELLOW      = (255, 230, 100)   # Frontera activa
ORANGE      = (255, 140,   0)   # Nodo actual
DARK_RED    = (180,  50,  50)   # Hoyos
GOLD        = (255, 200,   0)   # Meta


MENU_DATA = {
    "Frozen Lake (No Informada)": ["BFS (Anchura)", "DFS (Profundidad)"],
    "Sokoban (Informada)": ["A-Estrella (A*)", "Voraz (Greedy)"],
    "8 Reinas (Local)": ["Hill Climbing", "Recocido Simulado"],
    "Gato (Adversaria)": ["Poda Alfa-Beta"] # Cambiamos temporalmente para forzar alfa-beta
}


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

# ---Dibujar Tablero de Gato ---
def dibujar_gato(screen, state_dict, font_info, font_title):
    if not state_dict or "tablero" not in state_dict:
        return

    tablero = state_dict["tablero"]
    
    # 1. Panel Superior (Alfa, Beta y Mensaje)
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))
    texto_msg = font_title.render(state_dict['mensaje'], True, BLACK)
    screen.blit(texto_msg, (WIDTH//2 - texto_msg.get_width()//2, 15))
    
    texto_alfa = font_info.render(f"Alfa (\u03B1): {state_dict.get('alfa', '-')}", True, BLUE)
    texto_beta = font_info.render(f"Beta (\u03B2): {state_dict.get('beta', '-')}", True, RED)
    screen.blit(texto_alfa, (40, 60))
    screen.blit(texto_beta, (WIDTH - 40 - texto_beta.get_width(), 60))

    # 2. Dibujar Tablero 3x3 Centrado
    tamano_celda = 150
    margen_x = (WIDTH - (3 * tamano_celda)) // 2
    margen_y = TABLERO_Y + 60

    for row in range(3):
        for col in range(3):
            idx = row * 3 + col
            rect = pygame.Rect(margen_x + col * tamano_celda, margen_y + row * tamano_celda, tamano_celda, tamano_celda)
            
            # Fondo blanco y bordes gruesos para que parezca gato
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 4)
            
            # Dibujar X (Azul) y O (Roja)
            if tablero[idx] == 'X':
                offset = 30
                pygame.draw.line(screen, BLUE, (rect.left + offset, rect.top + offset), (rect.right - offset, rect.bottom - offset), 12)
                pygame.draw.line(screen, BLUE, (rect.right - offset, rect.top + offset), (rect.left + offset, rect.bottom - offset), 12)
            elif tablero[idx] == 'O':
                pygame.draw.circle(screen, RED, rect.center, tamano_celda // 2 - 25, 10)

    # Separador visual inferior
    pygame.draw.line(screen, BLACK, (0, TABLERO_Y + 600), (WIDTH, TABLERO_Y + 600), 2)

def cargar_sprites_frozen_lake(tamano_celda):
    ruta_base = os.path.join("assets", "uninformed")
    sprites   = {}
 
    archivos = {
        "ice":        "ice.png",
        "hole":       "hole.png",
        "goal":       "stool.png",
        "elf_down":   "elf_down.png",
        "elf_up":     "elf_up.png",
        "elf_left":   "elf_left.png",
        "elf_right":  "elf_right.png",
    }
 
    for clave, archivo in archivos.items():
        try:
            ruta    = os.path.join(ruta_base, archivo)
            imagen  = pygame.image.load(ruta).convert_alpha()
            sprites[clave] = pygame.transform.scale(imagen, (tamano_celda, tamano_celda))
        except (pygame.error, FileNotFoundError):
            print(f"Aviso: No se pudo cargar '{archivo}'. Usando color de respaldo.")
            sprites[clave] = None
 
    return sprites
 
def dibujar_celda_con_overlay(screen, rect, color_overlay, alpha=120):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((*color_overlay, alpha))
    screen.blit(overlay, rect.topleft)
 
def dibujar_frozen_lake(screen, estado_dict, font_info, font_title, sprites):
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
 
    filas        = len(mapa)
    columnas     = len(mapa[0])
    tamano_celda = WIDTH // columnas 
 
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))
    color_titulo = GREEN if encontrado else BLUE
    titulo = font_title.render(mensaje, True, color_titulo)
    screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 15))
    info = font_info.render(
        f"Pasos: {pasos}  |  Visitados: {len(visitados)}", True, BLACK
    )
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 60))
 
    for fila in range(filas):
        for col in range(columnas):
            celda = mapa[fila][col]
            pos   = (fila, col)
            rect  = pygame.Rect(
                col  * tamano_celda,
                TABLERO_Y + fila * tamano_celda,
                tamano_celda,
                tamano_celda
            )
 
            if sprites.get("ice"):
                screen.blit(sprites["ice"], rect.topleft)
            else:
                pygame.draw.rect(screen, WHITE, rect)
 
            if celda == 'H':
                if sprites.get("hole"):
                    screen.blit(sprites["hole"], rect.topleft)
                else:
                    pygame.draw.rect(screen, DARK_RED, rect)
 
            elif celda == 'G':
                if sprites.get("goal"):
                    screen.blit(sprites["goal"], rect.topleft)
                else:
                    pygame.draw.rect(screen, GOLD, rect)
 
            if celda != 'H':
                if pos in camino:
                    dibujar_celda_con_overlay(screen, rect, GREEN,      alpha=140)
                elif pos == pos_actual:
                    dibujar_celda_con_overlay(screen, rect, ORANGE,     alpha=160)
                elif pos in frontera:
                    dibujar_celda_con_overlay(screen, rect, YELLOW,     alpha=130)
                elif pos in visitados:
                    dibujar_celda_con_overlay(screen, rect, LIGHT_BLUE, alpha=110)
 
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)
 
            if pos == pos_actual:
                sprite_elfo = sprites.get("elf_down")
                if sprite_elfo:
                    screen.blit(sprite_elfo, rect.topleft)
                else:
                    pygame.draw.circle(screen, ORANGE, rect.center, tamano_celda // 3)
 
    linea_y = TABLERO_Y + filas * tamano_celda
    pygame.draw.line(screen, BLACK, (0, linea_y), (WIDTH, linea_y), 2)
 
    font_leyenda = pygame.font.SysFont(None, 20)
    leyenda = [
        (GREEN,      "Camino"),
        (ORANGE,     "Actual"),
        (YELLOW,     "Frontera"),
        (LIGHT_BLUE, "Visitado"),
    ]
    x_ley = 8
    y_ley = linea_y + 8
    for color_ley, texto_ley in leyenda:
        pygame.draw.rect(screen, color_ley,  (x_ley,      y_ley, 14, 14))
        pygame.draw.rect(screen, DARK_GRAY,  (x_ley,      y_ley, 14, 14), 1)
        etiqueta = font_leyenda.render(texto_ley, True, BLACK)
        screen.blit(etiqueta, (x_ley + 17, y_ley))
        x_ley += 85

# --- Dibujar Tablero de Sokoban ---
def dibujar_sokoban(screen, estado_dict, font_info, font_title):
    if not estado_dict or "nivel" not in estado_dict:
        return

    nivel      = estado_dict["nivel"]
    jugador    = estado_dict["jugador"]
    cajas      = estado_dict["cajas"]
    metas      = estado_dict["metas"]
    visitados  = estado_dict["visitados"]
    frontera   = estado_dict["frontera"]
    costo      = estado_dict["costo"]
    heuristica = estado_dict["heuristica"]
    encontrado = estado_dict["encontrado"]
    mensaje    = estado_dict["mensaje"]

    FILAS    = len(nivel)
    COLUMNAS = len(nivel[0])

    # Colores propios de Sokoban
    COL_WALL   = (60,  60,  60)
    COL_FLOOR  = (220, 215, 200)
    COL_GOAL   = (255, 200,  80)
    COL_BOX    = (160,  90,  20)
    COL_BOX_OK = (50,  180,  50)
    COL_PLAYER = (50,  100, 220)

    # Tamaño de celda: cabe en el ancho y en la zona de tablero disponible
    tam      = min(WIDTH // COLUMNAS, (HEIGHT - TABLERO_Y - 70) // FILAS)
    margen_x = (WIDTH - COLUMNAS * tam) // 2
    margen_y = TABLERO_Y

    # 1. Panel superior
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))
    color_msg = GREEN if encontrado else BLUE
    txt_msg   = font_title.render(mensaje, True, color_msg)
    screen.blit(txt_msg, (WIDTH // 2 - txt_msg.get_width() // 2, 12))

    txt_g = font_info.render(f"g(n): {costo}", True, BLACK)
    txt_h = font_info.render(f"h(n): {heuristica}", True, BLACK)
    txt_v = font_info.render(f"Visitados: {visitados}", True, BLACK)
    txt_f = font_info.render(f"Frontera: {frontera}", True, BLACK)
    screen.blit(txt_g, (20, 52))
    screen.blit(txt_h, (WIDTH - txt_h.get_width() - 20, 52))
    screen.blit(txt_v, (20, 76))
    screen.blit(txt_f, (WIDTH - txt_f.get_width() - 20, 76))

    # 2. Dibujar cada celda del grid
    for r in range(FILAS):
        for c in range(COLUMNAS):
            celda = nivel[r][c]
            pos   = (r, c)
            rect  = pygame.Rect(
                margen_x + c * tam,
                margen_y + r * tam,
                tam, tam
            )

            # Fondo de celda
            if celda == '#':
                pygame.draw.rect(screen, COL_WALL, rect)
            elif celda == '.':
                pygame.draw.rect(screen, COL_GOAL, rect)
            else:
                pygame.draw.rect(screen, COL_FLOOR, rect)

            # Caja (normal o sobre meta)
            if pos in cajas:
                color_caja  = COL_BOX_OK if pos in metas else COL_BOX
                mg          = tam // 8
                rect_caja   = pygame.Rect(rect.x + mg, rect.y + mg,
                                          tam - 2 * mg, tam - 2 * mg)
                pygame.draw.rect(screen, color_caja, rect_caja, border_radius=4)
                pygame.draw.rect(screen, BLACK, rect_caja, 2, border_radius=4)

            # Jugador
            if pos == jugador:
                pygame.draw.circle(screen, COL_PLAYER, rect.center, tam // 3)
                pygame.draw.circle(screen, BLACK,      rect.center, tam // 3, 2)

            # Borde de celda no-pared
            if celda != '#':
                pygame.draw.rect(screen, DARK_GRAY, rect, 1)

    # Separador visual inferior
    linea_y = margen_y + FILAS * tam
    pygame.draw.line(screen, BLACK, (0, linea_y), (WIDTH, linea_y), 2)


# --- BUCLE PRINCIPAL ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizador de Algoritmos IA")
    
    font_title = pygame.font.SysFont(None, 36)
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

    tamano_celda_fl = WIDTH // 8
    sprites_fl      = cargar_sprites_frozen_lake(tamano_celda_fl)

    #Variables de estado 
    estado = "MENU_PROBLEMA"
    problema_seleccionado = None
    algoritmo_seleccionado = None

    generador_algoritmo = None
    estado_actual = None
    ultimo_paso_tiempo = 0
    tiempo_entre_pasos = 0.8  
    iteracion_actual = 0
    limite_impresiones = 0

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
                    
                    # 1. Preparación para 8 Reinas
                    if problema_seleccionado == "8 Reinas (Local)":
                        problema = EightQueens()
                        if algoritmo_seleccionado == "Hill Climbing":
                            generador_algoritmo = hill_climbing(problema)
                        elif algoritmo_seleccionado == "Recocido Simulado":
                            generador_algoritmo = simulated_annealing(problema)
                    
                    # 2. Preparación para Frozen Lake
                    elif problema_seleccionado == "Frozen Lake (No Informada)":
                        problema = FrozenLake()
                        if algoritmo_seleccionado == "BFS (Anchura)":
                            generador_algoritmo = bfs(problema)
                        elif algoritmo_seleccionado == "DFS (Profundidad)":
                            generador_algoritmo = dfs(problema)
                            
                    # 3. Preparación para Sokoban (Informada)
                    elif problema_seleccionado == "Sokoban (Informada)":
                        problema = Sokoban()
                        if algoritmo_seleccionado == "A-Estrella (A*)":
                            generador_algoritmo = a_star(problema)
                        elif algoritmo_seleccionado == "Voraz (Greedy)":
                            generador_algoritmo = greedy(problema)

                    # 4. Preparación para Gato (Adversaria)
                    elif problema_seleccionado == "Gato (Adversaria)":
                        problema = TicTacToe()
                        if algoritmo_seleccionado == "Poda Alfa-Beta":
                            generador_algoritmo = alpha_beta_pruning(problema)

                    # --- Lógica común de terminal para todos ---
                    print(f"\nHas seleccionado {algoritmo_seleccionado}.")   
                    try:
                        entrada = input("¿Cuántas iteraciones iniciales deseas ver en la terminal? (Ej. 5): ")
                        limite_impresiones = int(entrada)
                        if limite_impresiones <= 0: limite_impresiones = 1
                    except ValueError:
                        print("Entrada no válida. Se mostrarán 5 iteraciones por defecto.")
                        limite_impresiones = 5
                    
                    iteracion_actual = 0
                    print("\n--- Iniciando Búsqueda ---")

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
            
            # === DIBUJO DEPENDIENDO DEL PROBLEMA ===
            if problema_seleccionado == "8 Reinas (Local)":
                dibujar_reinas(screen, estado_actual, font_info, font_title, imagen_reina)
                
                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                        iteracion_actual += 1

                        if iteracion_actual <= limite_impresiones:
                            print(f"Iteración: {iteracion_actual} | Costo (Ataques): {estado_actual['ataques']} | Estado: {estado_actual['mensaje']}")
                        elif iteracion_actual == limite_impresiones + 1:
                            print(f"... (Se han mostrado las {limite_impresiones} iteraciones. Observa la interfaz gráfica) ...")
                    except StopIteration:
                        generador_algoritmo = None
                        print(f"--- Búsqueda finalizada en la iteración {iteracion_actual} ---")
                        iteracion_actual = 0
 
            elif problema_seleccionado == "Frozen Lake (No Informada)":
                dibujar_frozen_lake(screen, estado_actual, font_info, font_title, sprites_fl)
 
                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                        iteracion_actual += 1

                        if iteracion_actual <= limite_impresiones:
                            frontera = estado_actual['frontera']
                            print(f"Iteración: {iteracion_actual} | Expandiendo: {estado_actual['pos_actual']} | Nodos en Frontera: {len(frontera)}")
                        elif iteracion_actual == limite_impresiones + 1:
                            print(f"... (Se han mostrado las {limite_impresiones} iteraciones. Observa la interfaz gráfica) ...")

                    except StopIteration:
                        generador_algoritmo = None
                        print(f"--- Búsqueda finalizada ---")
                        iteracion_actual = 0
                        
            elif problema_seleccionado == "Sokoban (Informada)":
                dibujar_sokoban(screen, estado_actual, font_info, font_title)

                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                        iteracion_actual += 1

                        if iteracion_actual <= limite_impresiones:
                            g  = estado_actual['costo']
                            h  = estado_actual['heuristica']
                            print(f"Iteración: {iteracion_actual} | g={g} | h={h} | f={g + h} | Visitados: {estado_actual['visitados']}")
                            print(f"  Estado: {estado_actual['mensaje']}")
                        elif iteracion_actual == limite_impresiones + 1:
                            print(f"... (Se han mostrado las {limite_impresiones} iteraciones. Observa la interfaz gráfica) ...")

                    except StopIteration:
                        generador_algoritmo = None
                        print(f"--- Búsqueda finalizada en la iteración {iteracion_actual} ---")
                        iteracion_actual = 0

            elif problema_seleccionado == "Gato (Adversaria)":
                dibujar_gato(screen, estado_actual, font_info, font_title)
                
                if generador_algoritmo and (tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos):
                    try:
                        estado_actual = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                        iteracion_actual += 1

                        if iteracion_actual <= limite_impresiones:
                            tablero = estado_actual['tablero']
                            msg = estado_actual['mensaje']
                            alfa = estado_actual.get('alfa', '-')
                            beta = estado_actual.get('beta', '-')
                            
                            print(f"\nIteración: {iteracion_actual} | Alfa: {alfa} | Beta: {beta}")
                            print(f"Estado: {msg}")
                            print(f" {tablero[0]} | {tablero[1]} | {tablero[2]} ")
                            print("---+---+---")
                            print(f" {tablero[3]} | {tablero[4]} | {tablero[5]} ")
                            print("---+---+---")
                            print(f" {tablero[6]} | {tablero[7]} | {tablero[8]} ")
                        elif iteracion_actual == limite_impresiones + 1:
                            print(f"\n... (Se han mostrado las {limite_impresiones} iteraciones. El árbol sigue explorando en la interfaz gráfica) ...")

                    except StopIteration:
                        generador_algoritmo = None
                        print(f"--- Búsqueda de Poda Alfa-Beta finalizada ---")
                        iteracion_actual = 0

            # === DIBUJAR BOTONES COMUNES ===
            pygame.draw.rect(screen, WHITE, (0, HEIGHT - 60, WIDTH, 60))
            
            btn_retry = dibujar_boton(screen, font_button, "Reintentar", 60, HEIGHT - 45, 200, 35, mouse_pos)
            if btn_retry.collidepoint(mouse_pos) and click:
                # Reiniciar el mismo problema/algoritmo seleccionado
                if problema_seleccionado == "8 Reinas (Local)":
                    problema = EightQueens()
                    if algoritmo_seleccionado == "Hill Climbing":
                        generador_algoritmo = hill_climbing(problema)
                    elif algoritmo_seleccionado == "Recocido Simulado":
                        generador_algoritmo = simulated_annealing(problema)
                elif problema_seleccionado == "Frozen Lake (No Informada)":
                    problema = FrozenLake()
                    if algoritmo_seleccionado == "BFS (Anchura)":
                        generador_algoritmo = bfs(problema)
                    elif algoritmo_seleccionado == "DFS (Profundidad)":
                        generador_algoritmo = dfs(problema)
                elif problema_seleccionado == "Sokoban (Informada)":
                    problema = Sokoban()
                    if algoritmo_seleccionado == "A-Estrella (A*)":
                        generador_algoritmo = a_star(problema)
                    elif algoritmo_seleccionado == "Voraz (Greedy)":
                        generador_algoritmo = greedy(problema)
                elif problema_seleccionado == "Gato (Adversaria)":
                    problema = TicTacToe()
                    if algoritmo_seleccionado == "Poda Alfa-Beta":
                        generador_algoritmo = alpha_beta_pruning(problema)

                print(f"\n--- Reiniciando Búsqueda ({algoritmo_seleccionado}) ---")
                iteracion_actual = 0
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
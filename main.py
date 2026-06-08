import pygame
import sys
import time
import os

# ── IMPORTACIONES: 8 Reinas (Busqueda Local) ─────────────────────────────────
from environments.eight_queens import EightQueens
from algorithms.local import hill_climbing, simulated_annealing

# ── IMPORTACIONES: Sokoban (Busqueda Informada) ───────────────────────────────
from environments.sokoban import Sokoban
from algorithms.informed import a_star, greedy

# ── CONFIGURACION VISUAL ──────────────────────────────────────────────────────
WIDTH  = 600
HEIGHT = 750
TABLERO_Y = 100   # usado por el tablero de 8 Reinas

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0  )
GRAY       = (200, 200, 200)
DARK_GRAY  = (150, 150, 150)
BLUE       = (50,  150, 255)
GREEN      = (50,  200, 50 )
RED        = (255, 50,  50 )
ORANGE     = (255, 165, 0  )
LIGHT_BLUE = (173, 216, 230)
BG_PANEL   = (245, 245, 245)

MENU_DATA = {
    "Frozen Lake (No Informada)": ["BFS (Anchura)", "DFS (Profundidad)"],
    "Sokoban (Informada)":        ["A-Estrella (A*)", "Voraz (Greedy)"],
    "8 Reinas (Local)":           ["Hill Climbing",   "Recocido Simulado"],
    "Gato (Adversaria)":          ["Minimax",          "Poda Alfa-Beta"],
}

# ── FUNCIONES DE INTERFAZ COMPARTIDAS ────────────────────────────────────────

def dibujar_boton(screen, font, text, x, y, w, h, mouse_pos, color_base=GRAY):
    rect  = pygame.Rect(x, y, w, h)
    color = DARK_GRAY if rect.collidepoint(mouse_pos) else color_base
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    surf  = font.render(text, True, BLACK)
    screen.blit(surf, surf.get_rect(center=rect.center))
    return rect


def dibujar_texto_centrado(screen, font, text, y, color=BLACK):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def pantalla_iteraciones(screen, font_title, font_info, font_button, clock):
    """Pantalla in-game para que el usuario elija cuantas iteraciones ver."""
    input_text  = ""
    mensaje_err = ""

    while True:
        screen.fill(WHITE)
        dibujar_texto_centrado(screen, font_title,
                               "Configuracion de Visualizacion", 80)
        dibujar_texto_centrado(screen, font_info,
                               "Ingresa el numero de iteraciones a mostrar:", 160)
        dibujar_texto_centrado(screen, font_info,
                               "(Cada iteracion = un nodo expandido por el algoritmo)",
                               195, DARK_GRAY)

        box = pygame.Rect(WIDTH // 2 - 80, 240, 160, 45)
        pygame.draw.rect(screen, LIGHT_BLUE, box, border_radius=6)
        pygame.draw.rect(screen, BLACK,      box, 2, border_radius=6)
        surf_in = font_title.render(input_text + "|", True, BLACK)
        screen.blit(surf_in, surf_in.get_rect(center=box.center))

        if mensaje_err:
            dibujar_texto_centrado(screen, font_info, mensaje_err, 300, RED)

        mouse_pos = pygame.mouse.get_pos()
        btn_ok = dibujar_boton(screen, font_button, "Aceptar",
                               WIDTH // 2 - 70, 330, 140, 44, mouse_pos)

        dibujar_texto_centrado(screen, font_info,
                               "Sugerencia: entre 20 y 100 para ver el avance",
                               395, DARK_GRAY)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    try:
                        n = int(input_text)
                        if n <= 0: raise ValueError
                        return n
                    except ValueError:
                        mensaje_err = "Ingresa un numero entero positivo."
                elif event.unicode.isdigit() and len(input_text) < 6:
                    input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_ok.collidepoint(mouse_pos):
                    try:
                        n = int(input_text)
                        if n <= 0: raise ValueError
                        return n
                    except ValueError:
                        mensaje_err = "Ingresa un numero entero positivo."


# ── RENDER: 8 REINAS (Busqueda Local) ────────────────────────────────────────
# Codigo original sin modificaciones.

def dibujar_reinas(screen, state_dict, font_info, font_title, imagen_reina):
    if not state_dict or "tablero" not in state_dict:
        return

    tablero       = state_dict["tablero"]
    tamano_celda  = WIDTH // 8

    # Panel superior con metricas
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, TABLERO_Y))
    texto_ataques = font_title.render(
        f"Ataques (Costo): {state_dict['ataques']}", True, RED)
    texto_msg = font_info.render(state_dict['mensaje'], True, BLACK)
    screen.blit(texto_ataques,
                (WIDTH // 2 - texto_ataques.get_width() // 2, 20))
    screen.blit(texto_msg,
                (WIDTH // 2 - texto_msg.get_width() // 2, 60))

    # Tablero 8x8
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            rect  = pygame.Rect(col * tamano_celda,
                                TABLERO_Y + (row * tamano_celda),
                                tamano_celda, tamano_celda)
            pygame.draw.rect(screen, color, rect)

            if tablero[col] == row:
                if imagen_reina:
                    img_x = rect.x + (tamano_celda - imagen_reina.get_width())  // 2
                    img_y = rect.y + (tamano_celda - imagen_reina.get_height()) // 2
                    screen.blit(imagen_reina, (img_x, img_y))
                else:
                    pygame.draw.circle(screen, BLUE,  rect.center, tamano_celda // 3)
                    pygame.draw.circle(screen, BLACK, rect.center, tamano_celda // 3, 2)

    pygame.draw.line(screen, BLACK,
                     (0, TABLERO_Y + 600), (WIDTH, TABLERO_Y + 600), 2)


# ── RENDER: SOKOBAN (Busqueda Informada) ─────────────────────────────────────
# Visualiza el estado que devuelve el generador de a_star / greedy.
# El dict 'step' tiene las claves:
#   "grid"     -> lista de listas de chars para dibujar el mapa
#   "mensaje"  -> texto de estado del algoritmo
#   "g"        -> costo acumulado desde el inicio
#   "h"        -> valor heuristico (distancia Manhattan a metas)
#   "f"        -> g + h  (solo A*; en Greedy f == h)
#   "abiertos" -> nodos en la frontera
#   "cerrados" -> nodos ya expandidos
#   "accion"   -> ultima direccion aplicada (U/D/L/R)
#   "resuelto" -> True cuando todas las cajas estan en su meta

SOK_CELL   = 56                              # px por celda del tablero
SOK_BORD_X = (WIDTH - 8 * SOK_CELL) // 2    # margen horizontal
SOK_BORD_Y = 110                             # margen superior

# Colores del mapa de Sokoban
SOK_WALL   = (80,  80,  80 )
SOK_FLOOR  = (230, 220, 200)
SOK_GOAL   = (180, 230, 180)
SOK_PLAYER = (50,  150, 255)
SOK_BOX    = (180, 120, 40 )
SOK_BOX_OK = (50,  200, 50 )

SOK_CHAR_BG = {
    '#': SOK_WALL,  ' ': SOK_FLOOR, '.': SOK_GOAL,
    '@': SOK_FLOOR, '+': SOK_GOAL,  '$': SOK_FLOOR, '*': SOK_GOAL,
}


def dibujar_sokoban(screen, step, font_info, font_title, font_small):
    if not step:
        return

    grid     = step.get("grid", [])
    resuelto = step.get("resuelto", False)

    # Panel superior: mensaje y metricas del algoritmo
    pygame.draw.rect(screen, BG_PANEL, (0, 0, WIDTH, SOK_BORD_Y))

    color_msg = GREEN if resuelto else BLACK
    surf_msg = font_title.render(step.get("mensaje", ""), True, color_msg)
    screen.blit(surf_msg, (WIDTH // 2 - surf_msg.get_width() // 2, 10))

    metrics = (f"g={step.get('g',0)}  h={step.get('h',0)}  "
               f"f={step.get('f',0)}  "
               f"Abiertos={step.get('abiertos',0)}  "
               f"Cerrados={step.get('cerrados',0)}")
    surf_m = font_info.render(metrics, True, BLUE)
    screen.blit(surf_m, (WIDTH // 2 - surf_m.get_width() // 2, 48))

    surf_ac = font_info.render(
        f"Accion: {step.get('accion', '-')}", True, DARK_GRAY)
    screen.blit(surf_ac, (WIDTH // 2 - surf_ac.get_width() // 2, 82))

    # Tablero de Sokoban
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            rect = pygame.Rect(SOK_BORD_X + c * SOK_CELL,
                               SOK_BORD_Y + r * SOK_CELL,
                               SOK_CELL, SOK_CELL)
            pygame.draw.rect(screen, SOK_CHAR_BG.get(ch, SOK_FLOOR), rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

            if ch in ('@', '+'):
                pygame.draw.circle(screen, SOK_PLAYER, rect.center, SOK_CELL // 3)
                pygame.draw.circle(screen, BLACK,      rect.center, SOK_CELL // 3, 2)
            elif ch == '$':
                inner = rect.inflate(-10, -10)
                pygame.draw.rect(screen, SOK_BOX,  inner, border_radius=4)
                pygame.draw.rect(screen, BLACK,    inner, 2, border_radius=4)
            elif ch == '*':
                inner = rect.inflate(-10, -10)
                pygame.draw.rect(screen, SOK_BOX_OK, inner, border_radius=4)
                pygame.draw.rect(screen, BLACK,      inner, 2, border_radius=4)
            elif ch == '.':
                mx, my = rect.center
                d = SOK_CELL // 5
                pygame.draw.line(screen, (0, 170, 0),
                                 (mx - d, my - d), (mx + d, my + d), 3)
                pygame.draw.line(screen, (0, 170, 0),
                                 (mx + d, my - d), (mx - d, my + d), 3)
            elif ch == '#':
                pygame.draw.rect(screen, (60, 60, 60),
                                 rect.inflate(-4, -4), border_radius=2)

    pygame.draw.rect(screen, BLACK,
                     pygame.Rect(SOK_BORD_X, SOK_BORD_Y,
                                 8 * SOK_CELL, 8 * SOK_CELL), 2)

    # Leyenda de colores
    ley_y  = SOK_BORD_Y + 8 * SOK_CELL + 10
    leyenda = [(SOK_PLAYER, "Jugador"), (SOK_BOX, "Caja"),
               (SOK_BOX_OK, "Caja OK"), (SOK_GOAL, "Meta"), (SOK_WALL, "Pared")]
    lx = 10
    for col_l, txt in leyenda:
        pygame.draw.rect(screen, col_l, (lx, ley_y, 14, 14))
        pygame.draw.rect(screen, BLACK,  (lx, ley_y, 14, 14), 1)
        s = font_small.render(txt, True, BLACK)
        screen.blit(s, (lx + 18, ley_y))
        lx += s.get_width() + 32


# ── BUCLE PRINCIPAL ───────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizador de Algoritmos IA")

    font_title  = pygame.font.SysFont(None, 40)
    font_button = pygame.font.SysFont(None, 28)
    font_info   = pygame.font.SysFont(None, 32)
    font_small  = pygame.font.SysFont(None, 20)
    clock       = pygame.time.Clock()

    # Imagen de reina para el tablero de 8 Reinas
    imagen_reina = None
    try:
        ruta_imagen  = os.path.join("assets", "reina.png")
        img_original = pygame.image.load(ruta_imagen).convert_alpha()
        nuevo_tamano = int((WIDTH // 8) * 1)
        imagen_reina = pygame.transform.scale(img_original,
                                              (nuevo_tamano, nuevo_tamano))
    except (pygame.error, FileNotFoundError):
        print("Aviso: No se encontro 'assets/reina.png'. Usando circulos.")

    estado               = "MENU_PROBLEMA"
    problema_seleccionado  = None
    algoritmo_seleccionado = None
    generador_algoritmo  = None
    estado_actual        = None
    ultimo_paso_tiempo   = 0
    tiempo_entre_pasos   = 0.4
    iteracion_actual     = 0
    limite_iteraciones   = 50

    running = True
    while running:
        screen.fill(WHITE)
        mouse_pos   = pygame.mouse.get_pos()
        click       = False
        tiempo_actual = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado = "MENU_PROBLEMA"

        # ── ESTADO: MENU PROBLEMA ─────────────────────────────────────────────
        if estado == "MENU_PROBLEMA":
            titulo = font_title.render("Selecciona un Problema", True, BLACK)
            screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 50))

            y_offset = 150
            for problema in MENU_DATA.keys():
                btn = dibujar_boton(screen, font_button, problema,
                                    WIDTH // 2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    problema_seleccionado = problema
                    estado = "MENU_ALGORITMO"
                y_offset += 80

        # ── ESTADO: MENU ALGORITMO ────────────────────────────────────────────
        elif estado == "MENU_ALGORITMO":
            titulo   = font_title.render("Selecciona el Algoritmo", True, BLACK)
            subtitulo = font_button.render(
                f"Problema: {problema_seleccionado}", True, BLUE)
            screen.blit(titulo,
                        (WIDTH // 2 - titulo.get_width() // 2, 50))
            screen.blit(subtitulo,
                        (WIDTH // 2 - subtitulo.get_width() // 2, 100))

            y_offset = 180
            for algoritmo in MENU_DATA[problema_seleccionado]:
                btn = dibujar_boton(screen, font_button, algoritmo,
                                    WIDTH // 2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    algoritmo_seleccionado = algoritmo
                    iteracion_actual       = 0

                    # ── Instanciar el problema y su generador ─────────────────

                    # 8 Reinas (codigo original)
                    if problema_seleccionado == "8 Reinas (Local)":
                        problema = EightQueens()
                        if algoritmo_seleccionado == "Hill Climbing":
                            generador_algoritmo = hill_climbing(problema)
                        elif algoritmo_seleccionado == "Recocido Simulado":
                            generador_algoritmo = simulated_annealing(problema)

                    # Sokoban (Busqueda Informada) ─────────────────────────────
                    elif problema_seleccionado == "Sokoban (Informada)":
                        problema = Sokoban()
                        if algoritmo_seleccionado == "A-Estrella (A*)":
                            generador_algoritmo = a_star(problema)
                        elif algoritmo_seleccionado == "Voraz (Greedy)":
                            generador_algoritmo = greedy(problema)
                    # ──────────────────────────────────────────────────────────

                    # Pedir al usuario cuantas iteraciones ver
                    limite_iteraciones = pantalla_iteraciones(
                        screen, font_title, font_info, font_button, clock)

                    try:
                        estado_actual = next(generador_algoritmo)
                    except StopIteration:
                        estado_actual = None

                    estado = "VISUALIZACION"
                y_offset += 80

            btn_back = dibujar_boton(screen, font_button, "Volver",
                                     20, 20, 100, 40, mouse_pos)
            if btn_back.collidepoint(mouse_pos) and click:
                estado = "MENU_PROBLEMA"

        # ── ESTADO: VISUALIZACION ─────────────────────────────────────────────
        elif estado == "VISUALIZACION":

            # Dibujar segun el problema activo
            if problema_seleccionado == "8 Reinas (Local)":
                dibujar_reinas(screen, estado_actual,
                               font_info, font_title, imagen_reina)

            # ── Sokoban ───────────────────────────────────────────────────────
            elif problema_seleccionado == "Sokoban (Informada)":
                dibujar_sokoban(screen, estado_actual,
                                font_info, font_title, font_small)
            # ─────────────────────────────────────────────────────────────────

            # Avanzar el generador automaticamente
            es_final = (estado_actual is not None
                        and estado_actual.get("resuelto", False))
            limite_alcanzado = (iteracion_actual >= limite_iteraciones)

            if generador_algoritmo and not es_final and not limite_alcanzado:
                if tiempo_actual - ultimo_paso_tiempo > tiempo_entre_pasos:
                    try:
                        estado_actual      = next(generador_algoritmo)
                        ultimo_paso_tiempo = tiempo_actual
                        iteracion_actual  += 1
                    except StopIteration:
                        generador_algoritmo = None

            # Panel inferior con botones
            panel_y = HEIGHT - 60
            pygame.draw.rect(screen, BG_PANEL, (0, panel_y - 8, WIDTH, 68))

            if limite_alcanzado and not es_final:
                msg = (f"Pausado tras {limite_iteraciones} iteraciones  "
                       f"— pulsa '+{limite_iteraciones} iter' para continuar")
                surf_p = font_small.render(msg, True, ORANGE)
                screen.blit(surf_p,
                            (WIDTH // 2 - surf_p.get_width() // 2, panel_y - 20))

            btn_retry = dibujar_boton(screen, font_button, "Reintentar",
                                      30, panel_y, 160, 35, mouse_pos)
            btn_cont  = dibujar_boton(screen, font_button,
                                      f"+{limite_iteraciones} iter",
                                      WIDTH // 2 - 60, panel_y, 120, 35,
                                      mouse_pos, LIGHT_BLUE)
            btn_back  = dibujar_boton(screen, font_button, "Volver al Menu",
                                      WIDTH - 190, panel_y, 160, 35, mouse_pos)

            # Reintentar: reinicia el mismo algoritmo
            if btn_retry.collidepoint(mouse_pos) and click:
                iteracion_actual = 0
                if problema_seleccionado == "8 Reinas (Local)":
                    problema = EightQueens()
                    if algoritmo_seleccionado == "Hill Climbing":
                        generador_algoritmo = hill_climbing(problema)
                    elif algoritmo_seleccionado == "Recocido Simulado":
                        generador_algoritmo = simulated_annealing(problema)

                # ── Sokoban ───────────────────────────────────────────────────
                elif problema_seleccionado == "Sokoban (Informada)":
                    problema = Sokoban()
                    if algoritmo_seleccionado == "A-Estrella (A*)":
                        generador_algoritmo = a_star(problema)
                    elif algoritmo_seleccionado == "Voraz (Greedy)":
                        generador_algoritmo = greedy(problema)
                # ─────────────────────────────────────────────────────────────

                try:
                    estado_actual = next(generador_algoritmo)
                except StopIteration:
                    estado_actual = None

            # +N iter: continua sin reiniciar el generador
            if btn_cont.collidepoint(mouse_pos) and click:
                iteracion_actual = 0

            # Volver al menu principal
            if btn_back.collidepoint(mouse_pos) and click:
                generador_algoritmo = None
                estado_actual       = None
                iteracion_actual    = 0
                estado              = "MENU_PROBLEMA"

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

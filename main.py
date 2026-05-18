import pygame
import sys

# --- 1. CONFIGURACIÓN VISUAL ---
WIDTH, HEIGHT = 600, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLUE = (50, 150, 255)
GREEN = (50, 200, 50)

# Opciones de la aplicación
MENU_DATA = {
    "Frozen Lake (No Informada)": ["BFS (Anchura)", "DFS (Profundidad)", "Costo Uniforme"],
    "Sokoban (Informada)": ["A-Estrella (A*)", "Voraz (Greedy)"],
    "8 Reinas (Local)": ["Hill Climbing", "Recocido Simulado"],
    "Gato (Adversaria)": ["Minimax", "Poda Alfa-Beta"]
}

# --- 2. FUNCIONES DE INTERFAZ (BOTONES) ---
def dibujar_boton(screen, font, text, x, y, w, h, mouse_pos):
    """Dibuja un botón y devuelve su rectángulo para detectar clics."""
    rect = pygame.Rect(x, y, w, h)
    
    # Cambiar color si el ratón pasa por encima (Efecto Hover)
    color = DARK_GRAY if rect.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10) # Borde
    
    # Renderizar texto
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    return rect

# --- 3. BUCLE PRINCIPAL Y MÁQUINA DE ESTADOS ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizador de Algoritmos IA")
    font_title = pygame.font.SysFont(None, 48)
    font_button = pygame.font.SysFont(None, 28)
    
    # Variables de la Máquina de Estados
    estado = "MENU_PROBLEMA"  # Estados: MENU_PROBLEMA, MENU_ALGORITMO, VISUALIZACION
    problema_seleccionado = None
    algoritmo_seleccionado = None

    running = True
    while running:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        
        # 1. Captura de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Clic izquierdo
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Volver al inicio presionando ESC
                    estado = "MENU_PROBLEMA"

        # 2. Lógica por Pantalla (Estados)
        
        if estado == "MENU_PROBLEMA":
            # Título
            titulo = font_title.render("Selecciona un Problema", True, BLACK)
            screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))
            
            # Dibujar botones de problemas
            y_offset = 150
            for problema in MENU_DATA.keys():
                btn = dibujar_boton(screen, font_button, problema, WIDTH//2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    problema_seleccionado = problema
                    estado = "MENU_ALGORITMO" # Avanzar al siguiente menú
                y_offset += 80

        elif estado == "MENU_ALGORITMO":
            # Título
            titulo = font_title.render("Selecciona el Algoritmo", True, BLACK)
            subtitulo = font_button.render(f"Problema: {problema_seleccionado}", True, BLUE)
            screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))
            screen.blit(subtitulo, (WIDTH//2 - subtitulo.get_width()//2, 100))
            
            # Dibujar botones de algoritmos dinámicamente
            y_offset = 180
            for algoritmo in MENU_DATA[problema_seleccionado]:
                btn = dibujar_boton(screen, font_button, algoritmo, WIDTH//2 - 150, y_offset, 300, 50, mouse_pos)
                if btn.collidepoint(mouse_pos) and click:
                    algoritmo_seleccionado = algoritmo
                    estado = "VISUALIZACION" # Ir a la pantalla final
                y_offset += 80
                
            # Botón de retroceso
            btn_back = dibujar_boton(screen, font_button, "Volver", 20, 20, 100, 40, mouse_pos)
            if btn_back.collidepoint(mouse_pos) and click:
                estado = "MENU_PROBLEMA"

        elif estado == "VISUALIZACION":
            # Aquí irá la lógica de dibujo de tu cuadrícula y la animación
            # Por ahora, mostramos un mensaje temporal
            texto_info = font_title.render("Ejecutando Animación...", True, BLACK)
            texto_prob = font_button.render(f"Problema: {problema_seleccionado}", True, BLUE)
            texto_algo = font_button.render(f"Algoritmo: {algoritmo_seleccionado}", True, GREEN)
            
            screen.blit(texto_info, (WIDTH//2 - texto_info.get_width()//2, HEIGHT//2 - 60))
            screen.blit(texto_prob, (WIDTH//2 - texto_prob.get_width()//2, HEIGHT//2))
            screen.blit(texto_algo, (WIDTH//2 - texto_algo.get_width()//2, HEIGHT//2 + 40))
            
            # Botón para reiniciar
            btn_back = dibujar_boton(screen, font_button, "Terminar / Volver (ESC)", WIDTH//2 - 125, HEIGHT - 100, 250, 50, mouse_pos)
            if btn_back.collidepoint(mouse_pos) and click:
                estado = "MENU_PROBLEMA"

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
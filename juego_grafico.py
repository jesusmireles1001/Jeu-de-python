import pygame
import sys
import random
import os

# --- 1. CONFIGURACIÓN INICIAL Y CONSTANTES ---

pygame.init()

# Dimensiones de la ventana
ANCHO = 800
ALTO = 600

# --- PALETA DE COLORES ---
COLOR_CIELO = (135, 206, 235)      
COLOR_AZUL_AGUA = (0, 105, 148)    
COLOR_ARENA = (238, 214, 175)      
COLOR_BARCO = (139, 69, 19)        
COLOR_PIEL = (255, 224, 189)       
COLOR_ROPA = (255, 0, 0)           
COLOR_HILO = (200, 200, 200)       
COLOR_GANCHO = (50, 50, 50)        

# Colores de interfaz y respaldo (si fallan las imágenes)
COLOR_BLANCO = (255, 255, 255)
COLOR_ROJO = (255, 0, 0)
COLOR_VERDE = (0, 200, 0)
COLOR_DORADO = (255, 215, 0)
COLOR_NEGRO = (0, 0, 0)
COLOR_AMARILLO = (255, 255, 0)
COLOR_LEGENDARIO = (255, 140, 0)
COLOR_BARRA_FONDO = (100, 100, 100)
COLOR_BARRA_RELLENO = (0, 255, 0)
COLOR_BOTON = (0, 150, 0)
COLOR_BOTON_HOVER = (0, 200, 0)

# Configuración de pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Pesca - BATALLA CONTRA EL PEZ GIGANTE")

reloj = pygame.time.Clock()
FPS = 60
TIEMPO_TOTAL_SEGUNDOS = 60 

# --- VARIABLES GLOBALES DEL JUEGO ---
ESTADO_JUEGO = "MENU" # ESTADOS POSIBLES: "MENU", "JUGANDO", "FIN"
tiempo_inicio = 0 
SCORE = 0
tiempo_desbloqueo = 0 

# --- VARIABLES DEL JEFE (BOSS) ---
BOSS_CLICKS_NECESARIOS = 50
BOSS_TIEMPO_LIMITE_MS = 8000 

modo_batalla_boss = False    
boss_clicks_actuales = 0      
boss_tiempo_inicio = 0       
pez_boss_capturado = None     

# Configuración del Hameçon (Gancho)
HAMEZON_ANCHO = 25 
HAMEZON_ALTO = 35
HAMEZON_VELOCIDAD_HORIZONTAL = 7 
HAMEZON_Y_MAX = ALTO - HAMEZON_ALTO 
HAMEZON_Y_INICIAL = 100 
VELOCIDAD_LANZAMIENTO = 8 

# Estados de la Caña
CAÑA_ARRIBA = 0
CAÑA_CAYENDO = 1
CAÑA_SUBIENDO = 2
estado_caña = CAÑA_ARRIBA 

ALTURA_SUPERFICIE = 130 

# Definición del Botón Jugar
BOTON_JUGAR_RECT = pygame.Rect(ANCHO//2 - 100, ALTO//2, 200, 60)
fuente = pygame.font.SysFont("arial", 30)
fuente_grande = pygame.font.SysFont("arial", 50, bold=True)


# --- 2. GESTIÓN DE IMÁGENES (CORREGIDO) ---

def cargar_sprite(nombre_archivo, ancho, alto, color_respaldo):
    """Intenta cargar una imagen desde la carpeta 'imagenes', si falla, usa un color."""
    # Construir la ruta correcta: carpeta 'imagenes' + nombre del archivo
    ruta_completa = os.path.join("imagenes", nombre_archivo)
    
    if os.path.exists(ruta_completa):
        try:
            imagen = pygame.image.load(ruta_completa).convert_alpha()
            imagen = pygame.transform.scale(imagen, (ancho, alto))
            return imagen
        except Exception as e:
            print(f"Error al cargar {nombre_archivo}: {e}")
    else:
        print(f"No se encontró la imagen: {ruta_completa}")
        
    # Si falla la carga, crear un rectángulo de color
    imagen = pygame.Surface([ancho, alto])
    imagen.fill(color_respaldo)
    return imagen

# Cargar assets
print("--- Iniciando carga de recursos ---")

# NOTA: En tu captura el pez verde tiene doble extensión (.png.png), por eso lo escribo así:
img_pez_verde = cargar_sprite("pez_verde.png.png", 60, 50, COLOR_VERDE)

img_pez_rojo = cargar_sprite("pez_rojo.png", 80, 60, COLOR_ROJO)
img_pez_dorado = cargar_sprite("pez_dorado.png", 65, 45, COLOR_DORADO)
img_boss = cargar_sprite("boss.png", 120, 70, COLOR_LEGENDARIO)
img_mina = cargar_sprite("mina.png", 30, 30, COLOR_NEGRO)
img_gancho = cargar_sprite("gancho.png", HAMEZON_ANCHO, HAMEZON_ALTO, COLOR_GANCHO)


# --- 3. CLASES (SPRITES) ---

class Hamezon(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto, imagen, velocidad_horizontal, ancho_pantalla):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        self.velocidad_horizontal = velocidad_horizontal
        self.ancho_pantalla = ancho_pantalla

    def update(self):
        global estado_caña
        if modo_batalla_boss: return
        if pygame.time.get_ticks() < tiempo_desbloqueo: return

        if estado_caña == CAÑA_ARRIBA:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_a]: self.rect.x -= self.velocidad_horizontal
            if teclas[pygame.K_d]: self.rect.x += self.velocidad_horizontal
            
            if self.rect.x < 0: self.rect.x = 0
            if self.rect.x > self.ancho_pantalla - self.rect.width:
                self.rect.x = self.ancho_pantalla - self.rect.width

class Pez(pygame.sprite.Sprite):
    def __init__(self, imagen_base, valor, velocidad_base): 
        super().__init__()
        self.valor = valor 
        self.imagen_original = imagen_base 
        self.image = self.imagen_original
        self.rect = self.image.get_rect()
        self.velocidad_base = velocidad_base
        self.direccion = 1 
        self.reset_posicion()

    def reset_posicion(self):
        self.velocidad = self.velocidad_base + random.uniform(0.5, 2)
        self.rect.y = random.randrange(ALTURA_SUPERFICIE + 40, ALTO - 50)
        self.direccion = random.choice([-1, 1])
        
        if self.direccion == -1: 
            # Va a la IZQUIERDA -> Imagen original
            self.image = self.imagen_original
            self.rect.x = random.randrange(ANCHO + 50, ANCHO + 300)
        else: 
            # Va a la DERECHA -> Voltear imagen
            self.image = pygame.transform.flip(self.imagen_original, True, False)
            self.rect.x = random.randrange(-300, -50)
        
    def update(self):
        if modo_batalla_boss: return 
        self.rect.x += self.velocidad * self.direccion
        if self.direccion == -1 and self.rect.right < 0: self.reset_posicion()
        elif self.direccion == 1 and self.rect.left > ANCHO: self.reset_posicion()

class PezLegendario(pygame.sprite.Sprite):
    def __init__(self): 
        super().__init__()
        self.imagen_original = img_boss
        self.image = self.imagen_original
        self.rect = self.image.get_rect()
        self.valor = 500 
        self.velocidad = 9 
        self.direccion = 1
        self.rect.y = random.randrange(ALTURA_SUPERFICIE + 50, ALTO - 100)
        self.rect.x = -500 

    def update(self):
        if modo_batalla_boss: return 
        
        if self.direccion == -1: 
            self.image = self.imagen_original
        else: 
            self.image = pygame.transform.flip(self.imagen_original, True, False)
            
        self.rect.x += self.velocidad * self.direccion
        
        if (self.direccion == 1 and self.rect.left > ANCHO) or \
           (self.direccion == -1 and self.rect.right < 0):
            self.kill() 

class Mina(pygame.sprite.Sprite):
    def __init__(self): 
        super().__init__()
        self.image = img_mina 
        self.rect = self.image.get_rect()
        self.velocidad = 3 
        self.direccion = 1
        self.reset_posicion()
    
    def reset_posicion(self):
        self.rect.y = random.randrange(ALTURA_SUPERFICIE + 50, ALTO - 50) 
        self.direccion = random.choice([-1, 1])
        if self.direccion == -1: self.rect.x = random.randrange(ANCHO + 50, ANCHO + 300)
        else: self.rect.x = random.randrange(-300, -50)
        
    def update(self):
        if modo_batalla_boss: return 
        self.rect.x += self.velocidad * self.direccion
        if self.direccion == -1 and self.rect.right < 0: self.reset_posicion()
        elif self.direccion == 1 and self.rect.left > ANCHO: self.reset_posicion()


# --- 4. CREACIÓN DE GRUPOS ---

hamezon = Hamezon(ANCHO // 2 - HAMEZON_ANCHO // 2, HAMEZON_Y_INICIAL, HAMEZON_ANCHO, HAMEZON_ALTO, 
                  img_gancho, HAMEZON_VELOCIDAD_HORIZONTAL, ANCHO)

grupo_peces = pygame.sprite.Group()
grupo_minas = pygame.sprite.Group()
grupo_boss = pygame.sprite.Group() 

# Crear peces iniciales
for _ in range(8): grupo_peces.add(Pez(img_pez_verde, 1, 2))
for _ in range(4): grupo_peces.add(Pez(img_pez_rojo, 5, 4))
for _ in range(1): grupo_peces.add(Pez(img_pez_dorado, 10, 7))
for _ in range(1): grupo_minas.add(Mina())


# --- 5. FUNCIONES DE DIBUJO Y LÓGICA ---

def mostrar_texto(pantalla, texto, color, x, y, fuente_usar=fuente):
    surf = fuente_usar.render(texto, True, color)
    pantalla.blit(surf, (x, y))

def dibujar_escenario():
    # Cielo
    pygame.draw.rect(pantalla, COLOR_CIELO, (0, 0, ANCHO, ALTURA_SUPERFICIE))
    # Agua
    pygame.draw.rect(pantalla, COLOR_AZUL_AGUA, (0, ALTURA_SUPERFICIE, ANCHO, ALTO - ALTURA_SUPERFICIE))
    # Arena
    pygame.draw.rect(pantalla, COLOR_ARENA, (0, ALTO - 40, ANCHO, 40))
    for i in range(0, ANCHO, 50):
        pygame.draw.circle(pantalla, (210, 180, 140), (i + 20, ALTO - 20), 5)

    # Barco
    bx = hamezon.rect.centerx
    by = ALTURA_SUPERFICIE - 20 
    pygame.draw.polygon(pantalla, COLOR_BARCO, [(bx-40, by), (bx+40, by), (bx+30, by+25), (bx-30, by+25)])
    
    # Pescador
    pygame.draw.circle(pantalla, COLOR_PIEL, (bx, by-25), 8)
    pygame.draw.rect(pantalla, COLOR_ROPA, (bx-8, by-17, 16, 17))
    
    # Caña
    pygame.draw.line(pantalla, (100, 50, 0), (bx+5, by-10), (bx+20, by-30), 3)
    
    # Hilo
    pygame.draw.line(pantalla, COLOR_HILO, (bx+20, by-30), (hamezon.rect.centerx, hamezon.rect.top), 2)

def dibujar_menu_inicio():
    dibujar_escenario()
    
    # Títulos con sombra
    mostrar_texto(pantalla, "SUPER PESCA EXTREMA", COLOR_NEGRO, ANCHO//2 - 253, 103, fuente_grande)
    mostrar_texto(pantalla, "SUPER PESCA EXTREMA", COLOR_AMARILLO, ANCHO//2 - 250, 100, fuente_grande)
    
    mostrar_texto(pantalla, "Usa 'A' y 'D' para moverte", COLOR_BLANCO, ANCHO//2 - 150, 250)
    mostrar_texto(pantalla, "Click Izquierdo para pescar", COLOR_BLANCO, ANCHO//2 - 160, 290)
    
    # Botón Jugar
    mouse_pos = pygame.mouse.get_pos()
    color_btn = COLOR_BOTON
    if BOTON_JUGAR_RECT.collidepoint(mouse_pos):
        color_btn = COLOR_BOTON_HOVER
        
    pygame.draw.rect(pantalla, color_btn, BOTON_JUGAR_RECT, border_radius=10)
    pygame.draw.rect(pantalla, COLOR_BLANCO, BOTON_JUGAR_RECT, 3, border_radius=10)
    mostrar_texto(pantalla, "JUGAR", COLOR_BLANCO, BOTON_JUGAR_RECT.x + 55, BOTON_JUGAR_RECT.y + 10, fuente)

def dibujar_interfaz_batalla():
    # Ventana de Boss
    rect_win = pygame.Rect(ANCHO//2 - 200, ALTO//2 - 100, 400, 200)
    pygame.draw.rect(pantalla, COLOR_NEGRO, rect_win)
    pygame.draw.rect(pantalla, COLOR_LEGENDARIO, rect_win, 5)
    
    mostrar_texto(pantalla, "¡PEZ GIGANTE!", COLOR_LEGENDARIO, ANCHO//2 - 100, ALTO//2 - 80, fuente_grande)
    mostrar_texto(pantalla, "¡CLICKS RAPIDOS!", COLOR_BLANCO, ANCHO//2 - 140, ALTO//2 - 20, fuente)
    
    # Barra
    progreso = min(1, boss_clicks_actuales / BOSS_CLICKS_NECESARIOS)
    pygame.draw.rect(pantalla, COLOR_BARRA_FONDO, (ANCHO//2 - 150, ALTO//2 + 30, 300, 30))
    pygame.draw.rect(pantalla, COLOR_BARRA_RELLENO, (ANCHO//2 - 150, ALTO//2 + 30, 300 * progreso, 30))
    
    # Tiempo restante boss
    tiempo_pasado = pygame.time.get_ticks() - boss_tiempo_inicio
    tiempo_restante = max(0, BOSS_TIEMPO_LIMITE_MS - tiempo_pasado) / 1000
    mostrar_texto(pantalla, f"{tiempo_restante:.1f}s", COLOR_ROJO, ANCHO//2 - 20, ALTO//2 + 70)

def reiniciar_juego():
    global SCORE, ESTADO_JUEGO, tiempo_inicio, estado_caña, tiempo_desbloqueo, modo_batalla_boss
    SCORE = 0
    ESTADO_JUEGO = "JUGANDO"
    tiempo_inicio = pygame.time.get_ticks()
    
    tiempo_desbloqueo = 0 
    modo_batalla_boss = False
    estado_caña = CAÑA_ARRIBA
    hamezon.rect.y = HAMEZON_Y_INICIAL
    
    for pez in grupo_peces: pez.reset_posicion()
    for mina in grupo_minas: mina.reset_posicion()
    grupo_boss.empty() 

def pantalla_final(pantalla, score):
    pantalla.fill(COLOR_AZUL_AGUA)
    mostrar_texto(pantalla, "¡FIN DEL JUEGO!", COLOR_AMARILLO, ANCHO // 2 - 150, ALTO // 2 - 50, fuente_grande)
    mostrar_texto(pantalla, f"SCORE FINAL: {score}", COLOR_BLANCO, ANCHO // 2 - 100, ALTO // 2 + 20)
    mostrar_texto(pantalla, "Presiona R para Reiniciar", COLOR_BLANCO, ANCHO // 2 - 150, ALTO // 2 + 80)
    pygame.display.flip()

def intentar_spawn_boss():
    if len(grupo_boss) == 0:
        if random.randint(0, 500) == 0:
            boss = PezLegendario()
            boss.direccion = random.choice([-1, 1])
            if boss.direccion == 1: boss.rect.x = -150
            else: boss.rect.x = ANCHO + 150
            grupo_boss.add(boss)


# --- 6. BUCLE PRINCIPAL (MAIN LOOP) ---

ejecutando = True

while ejecutando:
    tiempo_actual = pygame.time.get_ticks()
    
    # --- PROCESAR EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if ESTADO_JUEGO == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Click en botón JUGAR
                if BOTON_JUGAR_RECT.collidepoint(evento.pos):
                    ESTADO_JUEGO = "JUGANDO"
                    tiempo_inicio = pygame.time.get_ticks()
                        
        elif ESTADO_JUEGO == "JUGANDO":
            if modo_batalla_boss:
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    boss_clicks_actuales += 1
            else:
                # Si no está bloqueado por mina
                if tiempo_actual >= tiempo_desbloqueo:
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        if estado_caña == CAÑA_ARRIBA:
                            estado_caña = CAÑA_CAYENDO

        elif ESTADO_JUEGO == "FIN":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reiniciar_juego()

    # --- LÓGICA Y DIBUJO ---

    if ESTADO_JUEGO == "MENU":
        dibujar_menu_inicio()
        pygame.display.flip()

    elif ESTADO_JUEGO == "JUGANDO":
        intentar_spawn_boss()
        
        # Updates
        hamezon.update() 
        grupo_peces.update()
        grupo_minas.update()
        grupo_boss.update() 

        # --- Lógica de Batalla Boss ---
        if modo_batalla_boss:
            tiempo_pasado = tiempo_actual - boss_tiempo_inicio
            
            # Ganaste al Boss
            if boss_clicks_actuales >= BOSS_CLICKS_NECESARIOS:
                SCORE += 500
                pez_boss_capturado.kill() 
                modo_batalla_boss = False
                estado_caña = CAÑA_ARRIBA
                hamezon.rect.y = HAMEZON_Y_INICIAL
            
            # Perdiste contra el Boss
            elif tiempo_pasado >= BOSS_TIEMPO_LIMITE_MS:
                pez_boss_capturado.kill() 
                modo_batalla_boss = False
                estado_caña = CAÑA_ARRIBA
                hamezon.rect.y = HAMEZON_Y_INICIAL
        
        # --- Lógica Normal ---
        else:
            # Movimiento Vertical Caña
            if estado_caña == CAÑA_CAYENDO:
                hamezon.rect.y += VELOCIDAD_LANZAMIENTO
                if hamezon.rect.y >= HAMEZON_Y_MAX:
                    hamezon.rect.y = HAMEZON_Y_MAX 
                    estado_caña = CAÑA_SUBIENDO
            elif estado_caña == CAÑA_SUBIENDO:
                hamezon.rect.y -= VELOCIDAD_LANZAMIENTO
                if hamezon.rect.y <= HAMEZON_Y_INICIAL:
                    hamezon.rect.y = HAMEZON_Y_INICIAL 
                    estado_caña = CAÑA_ARRIBA
            
            # COLISIONES
            # 1. Boss
            hits_boss = pygame.sprite.spritecollide(hamezon, grupo_boss, False)
            if hits_boss:
                if not modo_batalla_boss:
                    modo_batalla_boss = True
                    boss_clicks_actuales = 0
                    boss_tiempo_inicio = tiempo_actual
                    pez_boss_capturado = hits_boss[0]

            # 2. Peces normales
            hits_peces = pygame.sprite.spritecollide(hamezon, grupo_peces, True) 
            for pez in hits_peces:
                SCORE += pez.valor
                # Regenerar
                if pez.valor == 1: nuevo = Pez(img_pez_verde, 1, 2)
                elif pez.valor == 10: nuevo = Pez(img_pez_dorado, 10, 7)
                else: nuevo = Pez(img_pez_rojo, 5, 4)
                grupo_peces.add(nuevo)

            # 3. Minas
            hits_minas = pygame.sprite.spritecollide(hamezon, grupo_minas, True)
            for mina in hits_minas:
                SCORE -= 30 
                tiempo_desbloqueo = tiempo_actual + 3000
                estado_caña = CAÑA_ARRIBA
                hamezon.rect.y = HAMEZON_Y_INICIAL
                grupo_minas.add(Mina())

        # Control de Tiempo Total
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / 1000 
        if tiempo_transcurrido >= TIEMPO_TOTAL_SEGUNDOS:
            ESTADO_JUEGO = "FIN"
        
        # --- DIBUJAR ---
        dibujar_escenario()
        
        # Sprites
        pantalla.blit(hamezon.image, hamezon.rect) 
        grupo_peces.draw(pantalla)
        grupo_minas.draw(pantalla)
        grupo_boss.draw(pantalla) 
        
        # HUD
        segundos_restantes = max(0, TIEMPO_TOTAL_SEGUNDOS - int(tiempo_transcurrido))
        mostrar_texto(pantalla, f"SCORE: {SCORE}", COLOR_AMARILLO, 10, 10)
        mostrar_texto(pantalla, f"TIEMPO: {segundos_restantes}s", COLOR_AMARILLO, ANCHO - 150, 10)
        
        # Aviso bloqueo
        if tiempo_actual < tiempo_desbloqueo:
            segundos_bloqueo = (tiempo_desbloqueo - tiempo_actual) // 1000 + 1
            texto_aviso = f"¡BOOM! BLOQUEADO: {segundos_bloqueo}s"
            aviso_rect = pygame.Rect(ANCHO//2 - 250, ALTO//2 - 40, 500, 80)
            pygame.draw.rect(pantalla, COLOR_ROJO, aviso_rect)
            pygame.draw.rect(pantalla, COLOR_NEGRO, aviso_rect, 3)
            mostrar_texto(pantalla, texto_aviso, COLOR_BLANCO, ANCHO // 2 - 220, ALTO // 2 - 25, fuente_grande)

        # Interfaz batalla
        if modo_batalla_boss:
            dibujar_interfaz_batalla()

        pygame.display.flip()

    elif ESTADO_JUEGO == "FIN":
        pantalla_final(pantalla, SCORE)

    reloj.tick(FPS)

# Salir
pygame.quit()
sys.exit()
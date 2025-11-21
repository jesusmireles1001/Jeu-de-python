import pygame
import sys
import random

# --- 1. CONFIGURACIÓN INICIAL Y CONSTANTES ---

pygame.init()

# Dimensiones de la Ventana
ANCHO = 800
ALTO = 600

# Colores (RGB)
COLOR_AZUL_AGUA = (0, 100, 150)
COLOR_BLANCO = (255, 100, 0) # Gancho
COLOR_ROJO = (255, 0, 0)     # Pez Rojo
COLOR_VERDE = (0, 200, 0)    # Pez Verde
COLOR_AMARILLO = (255, 255, 0) # Texto

# Configuración de la Ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Pesca ")

# Control de Tiempo y FPS
reloj = pygame.time.Clock()
FPS = 65
TIEMPO_TOTAL_SEGUNDOS = 60 
tiempo_inicio = pygame.time.get_ticks()

# Fuente para el Score y Mensajes
fuente = pygame.font.SysFont("arial", 30)

# Variables del Juego
SCORE = 0
JUGANDO = True 

# Hameçon (Gancho)
HAMEZON_ANCHO = 30
HAMEZON_ALTO = 50
HAMEZON_VELOCIDAD_HORIZONTAL = 7 

# Límites del movimiento vertical del hameçon
HAMEZON_Y_MAX = ALTO - HAMEZON_ALTO 
HAMEZON_Y_INICIAL = 50 
VELOCIDAD_LANZAMIENTO = 8 

# Estados de la Caña
CAÑA_ARRIBA = 0
CAÑA_CAYENDO = 1
CAÑA_SUBIENDO = 2
estado_caña = CAÑA_ARRIBA 

# Altura donde se detiene la caída (el "agua")
ALTURA_SUPERFICIE = 100 

# --- 2. CLASE HAMEZON ---

class Hamezon(pygame.sprite.Sprite):
    """Representa el gancho de pesca controlado por el jugador."""
    def __init__(self, x, y, ancho, alto, color, velocidad_horizontal, ancho_pantalla):
        super().__init__()
        
        # Usar rectángulo de color BLANCO
        self.image = pygame.Surface([ancho, alto])
        self.image.fill(color) 
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        self.velocidad_horizontal = velocidad_horizontal
        self.ancho_pantalla = ancho_pantalla

    def update(self):
        """Maneja el movimiento HORIZONTAL del hamezón SOLO cuando la caña está ARRIBA."""
        global estado_caña 
        
        if estado_caña == CAÑA_ARRIBA:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT]:
                self.rect.x -= self.velocidad_horizontal
            if teclas[pygame.K_RIGHT]:
                self.rect.x += self.velocidad_horizontal
                
            # Limitar movimiento horizontal
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.x > self.ancho_pantalla - self.rect.width:
                self.rect.x = self.ancho_pantalla - self.rect.width

# --- 3. CLASE PEZ ---

class Pez(pygame.sprite.Sprite):
    def __init__(self, color, valor, velocidad_base): 
        super().__init__()
        self.valor = valor 
        
        # Usar rectángulo del color pasado como parámetro
        self.image = pygame.Surface([40, 20])
        self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.velocidad_base = velocidad_base
        self.reset_posicion()

    def reset_posicion(self):
        self.rect.x = random.randrange(ANCHO + 50, ANCHO + 300) 
        self.rect.y = random.randrange(ALTURA_SUPERFICIE + 10, ALTO - 20) 
        self.velocidad = self.velocidad_base + random.uniform(0.5, 2)
        
    def update(self):
        self.rect.x -= self.velocidad
        if self.rect.right < 0:
            self.reset_posicion()

# --- 4. CREACIÓN DE OBJETOS ---

# Posición inicial del hameçon
hamezon_inicial_x = ANCHO // 2 - HAMEZON_ANCHO // 2

# Crear el sprite del Hameçon (usando COLOR_BLANCO)
hamezon = Hamezon(hamezon_inicial_x, HAMEZON_Y_INICIAL, HAMEZON_ANCHO, HAMEZON_ALTO, 
                  COLOR_BLANCO, HAMEZON_VELOCIDAD_HORIZONTAL, ANCHO)

# Grupo de Peces
grupo_peces = pygame.sprite.Group()

# Creación de Peces (usando COLOR_VERDE y COLOR_ROJO)
# 1. Peces Verdes
for _ in range(10):
    pez = Pez(COLOR_VERDE, 10, 2) 
    pez.rect.x = random.randrange(ANCHO, ANCHO * 3)
    grupo_peces.add(pez)

# 2. Peces Rojos
for _ in range(5):
    pez = Pez(COLOR_ROJO, 50, 4) 
    pez.rect.x = random.randrange(ANCHO, ANCHO * 3)
    grupo_peces.add(pez)

    # 3. Peces dorados
for _ in range(5):
    pez = Pez(COLOR_ROJO, 5, 4) 
    pez.rect.x = random.randrange(ANCHO, ANCHO * 3)
    grupo_peces.add(pez)


# --- 5. FUNCIONES AUXILIARES ---

def mostrar_texto(pantalla, texto, color, x, y):
    superficie_texto = fuente.render(texto, True, color)
    pantalla.blit(superficie_texto, (x, y))
    
def pantalla_final(pantalla, score):
    pantalla.fill(COLOR_AZUL_AGUA)
    mostrar_texto(pantalla, "🎣 ¡FIN DEL JUEGO! 🎣", COLOR_AMARILLO, ANCHO // 2 - 150, ALTO // 2 - 50)
    mostrar_texto(pantalla, f"SCORE FINAL: {score}", COLOR_BLANCO, ANCHO // 2 - 100, ALTO // 2 + 10)
    mostrar_texto(pantalla, "Presiona R para Reiniciar", COLOR_BLANCO, ANCHO // 2 - 150, ALTO // 2 + 80)
    pygame.display.flip()
    
def reiniciar_juego():
    global SCORE, JUGANDO, tiempo_inicio, estado_caña
    SCORE = 0
    JUGANDO = True
    tiempo_inicio = pygame.time.get_ticks()
    
    # Restablecer la posición del sprite del hameçon y su estado
    hamezon.rect.x = ANCHO // 2 - HAMEZON_ANCHO // 2
    hamezon.rect.y = HAMEZON_Y_INICIAL
    estado_caña = CAÑA_ARRIBA
    
    for pez in grupo_peces:
        pez.reset_posicion()


# --- 6. BUCLE PRINCIPAL DEL JUEGO (Game Loop) ---

ejecutando = True

while ejecutando:
    
    # --- A. Manejo de Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if JUGANDO:
            if evento.type == pygame.KEYDOWN:
                # Lanza la caña con ESPACIO solo si está ARRIBA
                if evento.key == pygame.K_SPACE and estado_caña == CAÑA_ARRIBA:
                    estado_caña = CAÑA_CAYENDO
        else: # Pantalla final
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar_juego()

    
    if JUGANDO:
        
        # --- B. Lógica del Juego ---
        
        # 1. Movimiento Horizontal del Hameçon
        hamezon.update() 

        # 2. Lógica del Lanzamiento Vertical de la Caña
        if estado_caña == CAÑA_CAYENDO:
            hamezon.rect.y += VELOCIDAD_LANZAMIENTO
            
            # Si llega al fondo, comienza a subir
            if hamezon.rect.y >= HAMEZON_Y_MAX:
                hamezon.rect.y = HAMEZON_Y_MAX 
                estado_caña = CAÑA_SUBIENDO
                
        elif estado_caña == CAÑA_SUBIENDO:
            hamezon.rect.y -= VELOCIDAD_LANZAMIENTO
            
            # Si regresa a la posición inicial, detiene el ciclo de lanzamiento
            if hamezon.rect.y <= HAMEZON_Y_INICIAL:
                hamezon.rect.y = HAMEZON_Y_INICIAL 
                estado_caña = CAÑA_ARRIBA
            
        # 3. Movimiento de Peces
        grupo_peces.update()

        # 4. Detección de Colisiones (Captura)
        peces_capturados = pygame.sprite.spritecollide(hamezon, grupo_peces, True) 
            
        for pez in peces_capturados:
            SCORE += pez.valor
            # Vuelve a crear el pez capturado (usando el color original)
            if pez.valor == 10:
                nuevo_pez = Pez(COLOR_VERDE, 10, 2)
            else:
                nuevo_pez = Pez(COLOR_ROJO, 50, 4)
            grupo_peces.add(nuevo_pez)

        # 5. Control de Tiempo 
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / 1000 
        
        if tiempo_transcurrido >= TIEMPO_TOTAL_SEGUNDOS:
            JUGANDO = False 

        
        # --- C. Dibujo ---
        
        pantalla.fill(COLOR_AZUL_AGUA)
        
        # Dibuja la línea de la superficie del agua (línea blanca)
        pygame.draw.line(pantalla, COLOR_BLANCO, (0, ALTURA_SUPERFICIE), (ANCHO, ALTURA_SUPERFICIE), 5)
        
        # 1. Hameçon
        pantalla.blit(hamezon.image, hamezon.rect) 
        
        # 2. Peces
        grupo_peces.draw(pantalla)
        
        # 3. HUD (Score y Tiempo)
        segundos_restantes = max(0, TIEMPO_TOTAL_SEGUNDOS - int(tiempo_transcurrido))
        mostrar_texto(pantalla, f"SCORE: {SCORE}", COLOR_AMARILLO, 10, 10)
        mostrar_texto(pantalla, f"TIEMPO: {segundos_restantes}s", COLOR_AMARILLO, ANCHO - 150, 10)
        
        # 4. Actualizar Pantalla
        pygame.display.flip()

    else:
        # Estado: FIN DEL JUEGO
        pantalla_final(pantalla, SCORE)

    # Controlar FPS
    reloj.tick(FPS)

# --- 7. Salir del Programa ---
pygame.quit()
sys.exit()
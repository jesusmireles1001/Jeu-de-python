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
COLOR_BLANCO = (255, 255, 255) # Gancho
COLOR_ROJO = (255, 0, 0)       # Pez Rojo
COLOR_VERDE = (0, 200, 0)      # Pez Verde
COLOR_DORADO = (255, 215, 0)   # Pez Dorado (Gold)
COLOR_AMARILLO = (255, 255, 0) # Texto

# Configuración de la Ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Pesca - Peces Multidireccionales")

# Control de Tiempo y FPS
reloj = pygame.time.Clock()
FPS = 60
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
    def __init__(self, x, y, ancho, alto, color, velocidad_horizontal, ancho_pantalla):
        super().__init__()
        self.image = pygame.Surface([ancho, alto])
        self.image.fill(color) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        self.velocidad_horizontal = velocidad_horizontal
        self.ancho_pantalla = ancho_pantalla

    def update(self):
        global estado_caña 
        if estado_caña == CAÑA_ARRIBA:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT]:
                self.rect.x -= self.velocidad_horizontal
            if teclas[pygame.K_RIGHT]:
                self.rect.x += self.velocidad_horizontal
            
            # Limites de pantalla
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.x > self.ancho_pantalla - self.rect.width:
                self.rect.x = self.ancho_pantalla - self.rect.width

# --- 3. CLASE PEZ (MODIFICADA PARA DIRECCIONES) ---

class Pez(pygame.sprite.Sprite):
    def __init__(self, color, valor, velocidad_base, ancho, alto): 
        super().__init__()
        self.valor = valor 
        
        self.image = pygame.Surface([ancho, alto])
        self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.velocidad_base = velocidad_base
        self.ancho_original = ancho 
        self.alto_original = alto
        self.direccion = 1 # Variable temporal
        
        self.reset_posicion()

    def reset_posicion(self):
        self.velocidad = self.velocidad_base + random.uniform(0.5, 2)
        self.rect.y = random.randrange(ALTURA_SUPERFICIE + 20, ALTO - 50) 
        
        # Elegir dirección al azar: -1 (Izquierda) o 1 (Derecha)
        self.direccion = random.choice([-1, 1])

        if self.direccion == -1: 
            # Va hacia la izquierda, nace a la derecha
            self.rect.x = random.randrange(ANCHO + 50, ANCHO + 300)
        else:
            # Va hacia la derecha, nace a la izquierda
            self.rect.x = random.randrange(-300, -50)
        
    def update(self):
        # Mover según dirección
        self.rect.x += self.velocidad * self.direccion
        
        # Revisar si salió de pantalla para reiniciar
        if self.direccion == -1 and self.rect.right < 0:
            self.reset_posicion()
        elif self.direccion == 1 and self.rect.left > ANCHO:
            self.reset_posicion()

# --- 4. CREACIÓN DE OBJETOS ---

hamezon_inicial_x = ANCHO // 2 - HAMEZON_ANCHO // 2
hamezon = Hamezon(hamezon_inicial_x, HAMEZON_Y_INICIAL, HAMEZON_ANCHO, HAMEZON_ALTO, 
                  COLOR_BLANCO, HAMEZON_VELOCIDAD_HORIZONTAL, ANCHO)

grupo_peces = pygame.sprite.Group()

# 1. Peces Verdes
for _ in range(8):
    pez = Pez(COLOR_VERDE, 1, 2, 40, 20) 
    grupo_peces.add(pez)

# 2. Peces Rojos
for _ in range(4):
    pez = Pez(COLOR_ROJO, 5, 4, 50, 30) 
    grupo_peces.add(pez)

# 3. Peces Dorados
for _ in range(1): 
    pez = Pez(COLOR_DORADO, 10, 7, 65, 45) 
    grupo_peces.add(pez)


# --- 5. FUNCIONES AUXILIARES ---

def mostrar_texto(pantalla, texto, color, x, y):
    superficie_texto = fuente.render(texto, True, color)
    pantalla.blit(superficie_texto, (x, y))
    
def pantalla_final(pantalla, score):
    pantalla.fill(COLOR_AZUL_AGUA)
    mostrar_texto(pantalla, "🎣 ¡FIN DEL JUEGO! 🎣", COLOR_AMARILLO, ANCHO // 2 - 150, ALTO // 2 - 50)
    mostrar_texto(pantalla, f"SCORE FINAL: {score}", (255, 255, 255), ANCHO // 2 - 100, ALTO // 2 + 10)
    mostrar_texto(pantalla, "Presiona R para Reiniciar", (255, 255, 255), ANCHO // 2 - 150, ALTO // 2 + 80)
    pygame.display.flip()
    
def reiniciar_juego():
    global SCORE, JUGANDO, tiempo_inicio, estado_caña
    SCORE = 0
    JUGANDO = True
    tiempo_inicio = pygame.time.get_ticks()
    
    hamezon.rect.x = ANCHO // 2 - HAMEZON_ANCHO // 2
    hamezon.rect.y = HAMEZON_Y_INICIAL
    estado_caña = CAÑA_ARRIBA
    
    for pez in grupo_peces:
        pez.reset_posicion()


# --- 6. BUCLE PRINCIPAL DEL JUEGO ---

ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if JUGANDO:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and estado_caña == CAÑA_ARRIBA:
                    estado_caña = CAÑA_CAYENDO
        else:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar_juego()

    if JUGANDO:
        hamezon.update() 

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
            
        grupo_peces.update()

        # Detectar colisiones y regenerar
        peces_capturados = pygame.sprite.spritecollide(hamezon, grupo_peces, True) 
            
        for pez in peces_capturados:
            SCORE += pez.valor
            
            if pez.valor == 1:
                nuevo_pez = Pez(COLOR_VERDE, 1, 2, 40, 20)
            elif pez.valor == 10:
                nuevo_pez = Pez(COLOR_DORADO, 10, 7, 65, 45)
            else: 
                nuevo_pez = Pez(COLOR_ROJO, 5, 4, 50, 30)
                
            grupo_peces.add(nuevo_pez)

        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / 1000 
        
        if tiempo_transcurrido >= TIEMPO_TOTAL_SEGUNDOS:
            JUGANDO = False 
        
        pantalla.fill(COLOR_AZUL_AGUA)
        pygame.draw.line(pantalla, (255, 255, 255), (0, ALTURA_SUPERFICIE), (ANCHO, ALTURA_SUPERFICIE), 5)
        
        pantalla.blit(hamezon.image, hamezon.rect) 
        grupo_peces.draw(pantalla)
        
        segundos_restantes = max(0, TIEMPO_TOTAL_SEGUNDOS - int(tiempo_transcurrido))
        mostrar_texto(pantalla, f"SCORE: {SCORE}", COLOR_AMARILLO, 10, 10)
        mostrar_texto(pantalla, f"TIEMPO: {segundos_restantes}s", COLOR_AMARILLO, ANCHO - 150, 10)
        
        pygame.display.flip()

    else:
        pantalla_final(pantalla, SCORE)

    reloj.tick(FPS)

pygame.quit()
sys.exit()
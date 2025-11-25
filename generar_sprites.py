import pygame
import sys

# Inicializar Pygame
pygame.init()

# Colores
TRANSPARENTE = (0, 0, 0, 0)
VERDE = (0, 200, 0)
ROJO = (255, 0, 0)
DORADO = (255, 215, 0)
LEGENDARIO = (255, 140, 0) # Naranja
NEGRO = (0, 0, 0)
GRIS = (50, 50, 50)
BLANCO = (255, 255, 255)

def crear_pez(nombre, ancho, alto, color_cuerpo):
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    
    # Cuerpo
    rect_cuerpo = pygame.Rect(0, 0, ancho - int(ancho*0.25), alto)
    pygame.draw.ellipse(surf, color_cuerpo, rect_cuerpo)
    
    # Cola
    cola_puntos = [(ancho - int(ancho*0.3), alto // 2), (ancho, 0), (ancho, alto)]
    pygame.draw.polygon(surf, color_cuerpo, cola_puntos)
    
    # Ojo
    pygame.draw.circle(surf, BLANCO, (int(ancho*0.2), int(alto*0.3)), int(alto*0.15))
    pygame.draw.circle(surf, NEGRO, (int(ancho*0.2), int(alto*0.3)), int(alto*0.05))
    
    pygame.image.save(surf, nombre)
    print(f"Creado: {nombre}")

def crear_boss():
    ancho, alto = 120, 70
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    
    # Cuerpo
    pygame.draw.ellipse(surf, LEGENDARIO, (0, 0, 90, 70))
    # Cola
    pygame.draw.polygon(surf, LEGENDARIO, [(80, 35), (120, 0), (120, 70)])
    # Aleta dorsal
    pygame.draw.polygon(surf, ROJO, [(40, 0), (60, -10), (80, 0)])
    # Ojo furioso
    pygame.draw.circle(surf, BLANCO, (25, 25), 12)
    pygame.draw.circle(surf, NEGRO, (25, 25), 4)
    # Ceja enojada
    pygame.draw.line(surf, NEGRO, (10, 15), (40, 20), 3)
    # Dientes
    for i in range(15, 60, 10):
        pygame.draw.polygon(surf, BLANCO, [(i, 50), (i+5, 60), (i+10, 50)])

    pygame.image.save(surf, "boss.png")
    print("Creado: boss.png")

def crear_mina():
    ancho, alto = 30, 30
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.circle(surf, NEGRO, (15, 15), 15)
    # Pinchos
    pygame.draw.line(surf, NEGRO, (0, 15), (30, 15), 3)
    pygame.draw.line(surf, NEGRO, (15, 0), (15, 30), 3)
    # Luz roja
    pygame.draw.circle(surf, ROJO, (15, 15), 5)
    pygame.image.save(surf, "mina.png")
    print("Creado: mina.png")

def crear_gancho():
    ancho, alto = 25, 35
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    # Forma de J
    pygame.draw.line(surf, GRIS, (12, 0), (12, 25), 4) # Vertical
    pygame.draw.arc(surf, GRIS, (2, 15, 20, 20), 3.14, 6.28, 4) # Curva
    # Punta
    pygame.draw.polygon(surf, GRIS, [(22, 15), (18, 20), (26, 20)])
    pygame.image.save(surf, "gancho.png")
    print("Creado: gancho.png")

# --- EJECUTAR ---
if __name__ == "__main__":
    crear_pez("pez_verde.png", 40, 20, VERDE)
    crear_pez("pez_rojo.png", 50, 30, ROJO)
    crear_pez("pez_dorado.png", 65, 45, DORADO)
    crear_boss()
    crear_mina()
    crear_gancho()
    print("¡IMÁGENES GENERADAS CON ÉXITO!")
    pygame.quit()
    sys.exit()
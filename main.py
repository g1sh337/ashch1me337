# test_simple.py - Minimal async test for Pygbag
import asyncio

async def main():
    print("=" * 50)
    print("SIMPLE TEST: main() STARTED!")
    print("=" * 50)
    
    import pygame
    print("SIMPLE TEST: pygame imported!")
    
    pygame.init()
    print("SIMPLE TEST: pygame initialized!")
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Simple Test")
    print("SIMPLE TEST: display created!")
    
    clock = pygame.time.Clock()
    running = True
    frame = 0
    
    while running:
        frame += 1
        if frame % 60 == 0:
            print(f"SIMPLE TEST: Frame {frame}")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 128, 255))  # Blue screen
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    pygame.quit()
    print("SIMPLE TEST: Finished!")

# Pygbag will find and run this automatically

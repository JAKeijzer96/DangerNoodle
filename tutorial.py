import pygame


pygame.init() # initialize pygame modules. Returns a tuple of (succesful, unsuccesful) initializations

gameDisplay = pygame.display.set_mode((800,600)) # tuple of height x width pixels
pygame.display.set_caption('Slither')

pygame.display.update()

gameExit = False

while not gameExit:
    for event in pygame.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
        if event.type == pygame.QUIT:
            gameExit = True
        #print(event)


pygame.quit() # uninitializes everything
quit() # quit the python program
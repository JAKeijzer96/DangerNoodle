import pygame


pygame.init() # initialize pygame modules. Returns a tuple of (succesful, unsuccesful) initializations

white = (255,255,255) # RGB value of the color
black = (0,0,0)
red = (255,0,0)


gameDisplay = pygame.display.set_mode((800,600)) # returns a surface object with (h,w) hxw pixels
pygame.display.set_caption('Slither')

gameExit = False

while not gameExit:
    for event in pygame.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
        if event.type == pygame.QUIT:
            gameExit = True
        #print(event)
    gameDisplay.fill(white)
    pygame.display.update() # update the display

pygame.quit() # uninitializes everything
quit() # quit the python program
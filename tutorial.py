import pygame


pygame.init() # initialize pygame modules. Returns a tuple of (succesful, unsuccesful) initializations

white = (255,255,255) # RGB value of the color
black = (0,0,0)
red = (255,0,0)

gameDisplay = pygame.display.set_mode((800,600)) # returns a surface object with (w,h) wxh pixels
pygame.display.set_caption('Slither')

gameExit = False

lead_x = 300
lead_y = 300
lead_x_change = 0
lead_y_change = 0

clock = pygame.time.Clock() # pygame clock object used to set fps


while not gameExit:
    for event in pygame.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                lead_x_change = -10
                lead_y_change = 0
            if event.key == pygame.K_RIGHT:
                lead_x_change = 10
                lead_y_change = 0
            if event.key == pygame.K_UP:
                lead_y_change = -10
                lead_x_change = 0
            if event.key == pygame.K_DOWN:
                lead_y_change = 10
                lead_x_change = 0

    if lead_x >= 800 or lead_x < 0 or lead_y >= 600 or lead_y < 0: # add boundaries
        gameExit = True
    
    lead_x += lead_x_change
    lead_y += lead_y_change

    gameDisplay.fill(white)
    pygame.draw.rect(gameDisplay, black, [lead_x,lead_y,10,10]) # parameters: surface, color, [x,y,width,height]
    pygame.display.update() # update the display

    clock.tick(10) # tick(x) for a game of x frames per second

pygame.quit() # uninitializes everything
quit() # quit the python program


























# gameDisplay.fill(red, rect=[200,200,50,50]) # alternative way to draw, can be graphics accellerated

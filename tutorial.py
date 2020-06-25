import pygame
import time


pygame.init() # initialize pygame modules. Returns a tuple of (succesful, unsuccesful) initializations

white = (255,255,255) # RGB value of the color
black = (0,0,0)
red = (255,0,0)
display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height)) # returns a surface object with (w,h) wxh pixels
pygame.display.set_caption('Slither')

gameExit = False

lead_x = display_width//2
lead_y = display_height//2
lead_x_change = 0
lead_y_change = 0

clock = pygame.time.Clock() # pygame clock object used to set fps
fps = 15

block_size = 10

font = pygame.font.SysFont(None, 25) # size 25

def message_to_screen(msg, color):
    screen_text = font.render(msg, True, color) # render message, True (for anti-aliasing), color
    gameDisplay.blit(screen_text, [display_width//2, display_height//2]) # show screen_text on [coords]

while not gameExit:
    for event in pygame.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                lead_x_change = -block_size
                lead_y_change = 0
            if event.key == pygame.K_RIGHT:
                lead_x_change = block_size
                lead_y_change = 0
            if event.key == pygame.K_UP:
                lead_y_change = -block_size
                lead_x_change = 0
            if event.key == pygame.K_DOWN:
                lead_y_change = block_size
                lead_x_change = 0

    if lead_x >= display_width or lead_x < 0 or lead_y >= display_height or lead_y < 0: # add boundaries
        gameExit = True
    
    lead_x += lead_x_change
    lead_y += lead_y_change

    gameDisplay.fill(white)
    pygame.draw.rect(gameDisplay, black, [lead_x,lead_y,block_size,block_size]) # parameters: surface, color, [x,y,width,height]
    pygame.display.update() # update the display

    clock.tick(fps) # tick(x) for a game of x frames per second

message_to_screen("You lose", red)
pygame.display.update()
time.sleep(2)
pygame.quit() # uninitializes everything
quit() # quit the python program

import pygame as pg
from random import randint

pg.init() # initialize pg modules. Returns a tuple of (succesful, unsuccesful) initializations

white = (255, 255, 255) # RGB value of the color
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 140, 0)

display_width = 800
display_height = 600

program_surface = pg.display.set_mode((display_width,display_height)) # returns a surface object with (w,h) wxh pixels
pg.display.set_caption('Slither')

img = pg.image.load("snakehead.png") # snakehead.png is a 20x20 file
apple_img = pg.image.load("apple.png") # apple.png is a 20x20 file


clock = pg.time.Clock() # pg clock object used to set fps
fps = 15

block_size = 20
apple_thickness = 20
direction = "down"

smallfont = pg.font.SysFont("comicsansms", 25) # size 25
medfont = pg.font.SysFont("comicsansms", 50) # size 25
largefont = pg.font.SysFont("comicsansms", 80) # size 25

def game_intro():
    intro = True

    while intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_c:
                    intro = False
                if event.key == pg.K_q:
                    pg.quit()
                    quit()
        
        program_surface.fill(white)
        message_to_screen("Welcome to Slither", green, -100, "large")
        message_to_screen("The objective of the game is to eat red apples", black, -30)
        message_to_screen("The more apples you eat, the longer you get", black)
        message_to_screen("If you run into yourself or the edges, you die", black, 30)
        message_to_screen("Press C to play or Q to quit", black, 180)
        pg.display.update()
        clock.tick(15) # no need for high fps, just dont make the delay on keydown too long



def snake(block_size, snake_list):
    # make new function rotate(img, direction)?
    # could also remove direction variable and immediately rotate imgs when key is pressed
    if direction == "up":
        head = img
    elif direction == "left":
        head = pg.transform.rotate(img, 90) # rotate counterclockwise
    elif direction == "down":
        head = pg.transform.rotate(img, 180)
    elif direction == "right":
        head = pg.transform.rotate(img, 270)

    program_surface.blit(head, (snake_list[-1][0], snake_list[-1][1])) # blit the snake head image
    for x_and_y in snake_list[:-1]: # the last element is the head, so dont put a square there
        pg.draw.rect(program_surface, green, [x_and_y[0],x_and_y[1],block_size,block_size]) # parameters: surface, color, [x,y,width,height]

def text_objects(text, color, size):
    if size == "small":
        text_surface = smallfont.render(text, True, color) # render message, True (for anti-aliasing), color
    elif size == "med":
        text_surface = medfont.render(text, True, color) # render message, True (for anti-aliasing), color
    elif size == "large":
        text_surface = largefont.render(text, True, color) # render message, True (for anti-aliasing), color
    return text_surface, text_surface.get_rect()

def message_to_screen(msg, color, y_displace=0, size="small"):
    text_surface, text_rect = text_objects(msg, color, size)
    text_rect.center = (display_width//2, display_height//2 + y_displace)
    program_surface.blit(text_surface, text_rect) # show screen_text on [coords]

def game_loop():
    global direction
    direction = "down"
    program_exit = False
    game_over = False

    lead_x = display_width//2
    lead_y = display_height//2
    lead_x_change = 0
    lead_y_change = block_size
    snake_list = [] # list of all squares occupied by the snake
    snake_length = 1 # max allowed length of danger noodle

    # randint(0,display_width) could return display_width, meaning we would get an apple with coordinates
    # [display_width, display_height, block_size, block_size], which would appear offscreen
    rand_apple_x = round(randint(0, display_width - apple_thickness)) # / 10) * 10 # round to nearest 10
    rand_apple_y = round(randint(0, display_height - apple_thickness)) # / 10) * 10 # round to nearest 10

    while not program_exit:
        while game_over:
            program_surface.fill(white)
            message_to_screen("Game over", red, y_displace=-50, size="large")
            message_to_screen("Press C to play again or Q to quit", black, 50, size="med")
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    program_exit = True
                    game_over = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        program_exit = True
                        game_over = False
                    if event.key == pg.K_c:
                        game_loop()

        for event in pg.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
            if event.type == pg.QUIT:
                program_exit = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    lead_x_change = -block_size
                    lead_y_change = 0
                    direction = "left"
                if event.key == pg.K_RIGHT:
                    lead_x_change = block_size
                    lead_y_change = 0
                    direction = "right"
                if event.key == pg.K_UP:
                    lead_y_change = -block_size
                    lead_x_change = 0
                    direction = "up"
                if event.key == pg.K_DOWN:
                    lead_y_change = block_size
                    lead_x_change = 0
                    direction = "down"

        if lead_x >= display_width or lead_x < 0 or lead_y >= display_height or lead_y < 0: # add boundaries
            game_over = True
        
        lead_x += lead_x_change
        lead_y += lead_y_change

        program_surface.fill(white)
        #pg.draw.rect(program_surface, red, [rand_apple_x, rand_apple_y, apple_thickness, apple_thickness]) # draw apple
        program_surface.blit(apple_img, (rand_apple_x, rand_apple_y))
        
        snake_head = []
        snake_head.append(lead_x)
        snake_head.append(lead_y)
        snake_list.append(snake_head)
        
        if len(snake_list) >  snake_length:
            del snake_list[0] # remove the first (oldest) element of the list
        
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over = True


        snake(block_size, snake_list)
        pg.display.update() # update the display

        # Collision for small snake, big apple
        # if lead_x >= rand_apple_x and lead_x <= rand_apple_x + apple_thickness:
        #     if lead_y >= rand_apple_y and lead_y <= rand_apple_y + apple_thickness:
        #         rand_apple_x = round(randint(0, display_width - block_size)) # / 10) * 10 # round to nearest 10
        #         rand_apple_y = round(randint(0, display_height - block_size)) # / 10) * 10 # round to nearest 10
        #         snake_length += 1

        # Updated collision for any size snake/apple
        if (lead_x + block_size > rand_apple_x and lead_y + block_size > rand_apple_y
            and lead_x < rand_apple_x + apple_thickness and lead_y < rand_apple_y + apple_thickness):
                rand_apple_x = round(randint(0, display_width - apple_thickness)) # / 10) * 10 # round to nearest 10
                rand_apple_y = round(randint(0, display_height - apple_thickness)) # / 10) * 10 # round to nearest 10
                snake_length += 1

        clock.tick(fps) # tick(x) for a game of x frames per second, put this after display.update()

    pg.quit() # uninitialize pygame
    quit() # quit the program

game_intro()
game_loop()
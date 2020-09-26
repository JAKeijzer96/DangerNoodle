try:
    import pygame as pg
except ModuleNotFoundError as e:
    print(f"{e}: The pygame module could not be found")
from sys import exit
from random import randint
import ctypes

pg.init() # initialize pg modules. Returns a tuple of (succesful, unsuccesful) initializations

# set unique windows app id so Windows uses the proper icon in the taskbar when executing snake.py
myappid = "arbitrary string to uniquely identify snake game"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Initialize color constants as their corresponding RGB values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SNAKE_GREEN = (0, 155, 0) # Not bright green
REGULAR_FONT = "./Gasalt-Regular.ttf"

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

FPS = 15 # TODO: Find optimal fps with possibly lower x,y increments per clock tick.
         # increments depend on but are not equal to block_size. if they were this could mess up the grid system
BLOCK_SIZE = 20

class Snake():
    def __init__(self):
        # Load images
        self.icon = pg.image.load("icon.png") # icon should be a 32x32 file
        self.head_img = pg.image.load("snakehead.png") # block_size x block_size pixels
        self.apple_img = pg.image.load("apple.png") # block_size x block_size pixels
        self.tail_img = pg.image.load("snaketail.png") # block_size x block_size pixels
        # Initialize main program surface
        self.program_surface = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT)) # returns a surface object with (w,h) wxh pixels
        pg.display.set_caption("DangerNoodle - A very original game by Jasper")
        pg.display.set_icon(self.icon) # TODO: add proper icon
        # Initialize clock object to tick every FPS times per second
        self.clock = pg.time.Clock() # pg clock object used to set fps
        # Initialize fonts
        self.smallfont = pg.font.Font(REGULAR_FONT, 25) # TODO: find prettier font and matching sizes
        self.medfont = pg.font.Font(REGULAR_FONT, 40) # size 50
        self.largefont = pg.font.Font(REGULAR_FONT, 80) # size 80
        # Call function to reset game variables, in this case initializing them
        self.reset_game_variables()

        
    # Function to initialize game variables at the start, or reset them on game_over
    def reset_game_variables(self):
        self.game_over = False # True if snake is dead but program still running
        self.program_exit = False # True if program is quit
        self.lead_x = DISPLAY_WIDTH//2 # x-location of head, initially center of screen
        self.lead_y = DISPLAY_HEIGHT//2 # y-ocation of head, initially center of screen
        self.lead_x_change = 0 # Change in lead_x location every clock tick
        self.lead_y_change = BLOCK_SIZE # change in lead_y location every clock tick, initially snake moves down
        self.snake_list = [] # list of all squares currently occupied by the snake
        self.snake_length = 2 # max allowed length of the snake
        self.head = self.rotate(self.head_img, 180) # starting direction is down
        #self.tail = self.tail_img
        self.score = 0 # score, could use snake_length - base length but base length still not certain # TODO ?
        self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen() # TODO: refactor? also comment functionality

    def game_intro(self):
        # Print introductory messages (start menu)
        self.program_surface.fill(WHITE)
        self.message_to_screen("Welcome to Slither", SNAKE_GREEN, -100, "large")
        self.message_to_screen("The objective of the game is to eat red apples", BLACK, -30, "med")
        self.message_to_screen("The more apples you eat, the longer you get", BLACK, 0, "med")
        self.message_to_screen("If you run into yourself or the edges, you die", BLACK, 30, "med")
        self.message_to_screen("Press C to play, P to pause or Q to quit", BLACK, 180, "med")
        pg.display.update()

        intro = True
        while intro:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        intro = False
                    elif event.key == pg.K_q:
                        pg.quit()
                        exit()
            
            # TODO: find optimal clock tick here
            self.clock.tick(15) # no need for high fps, just dont make the delay on keydown too long

    def rand_apple_gen(self):
        # TODO: Make apple unable to spawn on/under snake

        # randint(0,display_width) could return display_width, meaning we would get an apple with coordinates
        # [display_width, display_height, block_size, block_size], which would appear offscreen
        rand_apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        rand_apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        return rand_apple_x, rand_apple_y

    def print_score(self, score):
        text = self.smallfont.render(f"Score: {score}", True, BLACK)
        self.program_surface.blit(text, [0,0])

    def pause(self):
        # Update once when paused, then only check for event handling
        self.message_to_screen("Paused", BLACK, -100, size="large")
        self.message_to_screen("Press C to continue or Q to quit", BLACK)
        pg.display.update()
        
        paused = True
        while paused:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        paused = False
                    elif event.key == pg.K_q:
                        pg.quit()
                        exit()
            # TODO: find optimal fps here
            self.clock.tick(15) # dont need high fps

    def rotate(self, img, degrees):
        return pg.transform.rotate(img, degrees)

    def snake(self, block_size, snake_list):
        draw_tail = 0 # used in list slicing to determine whether or not to draw the tail without raising index errors

        self.program_surface.blit(self.head, (self.snake_list[-1][0], self.snake_list[-1][1])) # blit the snake head image
        
        if len(self.snake_list) > 1:
            draw_tail = 1
            if self.snake_list[1][0] < self.snake_list[0][0]: # x less, so go left
                tail = self.rotate(self.tail_img, 90)
            elif self.snake_list[1][1] > self.snake_list[0][1]: # y greater, go down
                tail = self.rotate(self.tail_img, 180)
            elif self.snake_list[1][0] > self.snake_list[0][0]: # x greater, go right
                tail = self.rotate(self.tail_img, 270)
            else: # going up
                tail = self.tail_img

            self.program_surface.blit(tail, (self.snake_list[0][0], self.snake_list[0][1]))
        
        # TODO: Add extra segment images for the body and when we turn a corner
        # TODO: For corner image, check coords before and after current segment to see which way to rotate the image

        for x_and_y in self.snake_list[draw_tail:-1]: # the last element is the head, so dont put a square there
            pg.draw.rect(self.program_surface, SNAKE_GREEN, [x_and_y[0],x_and_y[1],BLOCK_SIZE,BLOCK_SIZE]) # parameters: surface, color, [x,y,width,height]

    def text_objects(self, text, color, size):
        if size == "small":
            text_surface = self.smallfont.render(text, True, color) # render message, True (for anti-aliasing), color
        elif size == "med":
            text_surface = self.medfont.render(text, True, color) # render message, True (for anti-aliasing), color
        elif size == "large":
            text_surface = self.largefont.render(text, True, color) # render message, True (for anti-aliasing), color
        return text_surface, text_surface.get_rect()

    def message_to_screen(self, msg, color, y_displace=0, size="small"):
        # TODO: clean up text_objects and message_to_screen functions? possibly combine
        text_surface, text_rect = self.text_objects(msg, color, size)
        text_rect.center = (DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + y_displace)
        self.program_surface.blit(text_surface, text_rect) # show screen_text on [coords]

    def game_loop(self):
        while not self.program_exit:
            if self.game_over: # only paste text once # TODO: is it possible to clean this up? merge if game_over and while game_over
                #program_surface.fill(white)
                self.message_to_screen("Game over", RED, y_displace=-50, size="large")
                self.message_to_screen("Press C to play again or Q to quit", BLACK, 50, size="med")
                pg.display.update()
                
            while self.game_over:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.program_exit = True
                        self.game_over = False
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_q:
                            self.program_exit = True
                            self.game_over = False
                        elif event.key == pg.K_c:
                            self.reset_game_variables()
                            self.game_loop() # TODO: restart game loop without re-initializing class


            for event in pg.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
                if event.type == pg.QUIT:
                    self.program_exit = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        if self.lead_x_change == BLOCK_SIZE: # disallow running into self
                            break # TODO: momre comments on functionality
                        self.lead_x_change = -BLOCK_SIZE
                        self.lead_y_change = 0
                        self.head = self.rotate(self.head_img, 90)
                    elif event.key == pg.K_RIGHT:
                        if self.lead_x_change == -BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_x_change = BLOCK_SIZE
                        self.lead_y_change = 0
                        self.head = self.rotate(self.head_img, 270)
                    elif event.key == pg.K_UP:
                        if self.lead_y_change == BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_y_change = -BLOCK_SIZE
                        self.lead_x_change = 0
                        self.head = self.head_img
                    elif event.key == pg.K_DOWN:
                        if self.lead_y_change == -BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_y_change = BLOCK_SIZE
                        self.lead_x_change = 0
                        self.head = self.rotate(self.head_img, 180)
                    elif event.key == pg.K_p:
                        self.pause()

            if self.lead_x >= DISPLAY_WIDTH or self.lead_x < 0 or self.lead_y >= DISPLAY_HEIGHT or self.lead_y < 0: # add boundaries
                self.game_over = True # TODO: comment on if statement
            
            self.lead_x += self.lead_x_change
            self.lead_y += self.lead_y_change

            self.program_surface.fill(WHITE)
            self.program_surface.blit(self.apple_img, (self.rand_apple_x, self.rand_apple_y))
            
            # TODO: check if this is needed or double functionality
            snake_head = []
            snake_head.append(self.lead_x)
            snake_head.append(self.lead_y)
            self.snake_list.append(snake_head)
            
            if len(self.snake_list) >  self.snake_length:
                del self.snake_list[0] # remove the first (oldest) element of the list
            
            for segment in self.snake_list[:-1]:
                if segment == snake_head:
                    self.game_over = True


            self.snake(BLOCK_SIZE, self.snake_list)
            self.print_score(self.score)
            pg.display.update() # update the display

            # Collision for small snake, big apple
            # if lead_x >= rand_apple_x and lead_x <= rand_apple_x + apple_thickness:
            #     if lead_y >= rand_apple_y and lead_y <= rand_apple_y + apple_thickness:
            #         rand_apple_x = round(randint(0, display_width - block_size)) # / 10) * 10 # round to nearest 10
            #         rand_apple_y = round(randint(0, display_height - block_size)) # / 10) * 10 # round to nearest 10
            #         snake_length += 1

            # Updated collision for any size snake/apple
            # TODO: move back to grid-based collision
            if (self.lead_x + BLOCK_SIZE > self.rand_apple_x and self.lead_y + BLOCK_SIZE > self.rand_apple_y
                and self.lead_x < self.rand_apple_x + BLOCK_SIZE and self.lead_y < self.rand_apple_y + BLOCK_SIZE):
                    self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen()
                    self.snake_length += 1
                    self.score += 1

            self.clock.tick(FPS) # tick(x) for a game of x frames per second, put this after display.update()

        pg.quit() # uninitialize pygame
        exit() # quit the program

if __name__ == "__main__":
    snek = Snake()
    snek.game_intro()
    snek.game_loop()
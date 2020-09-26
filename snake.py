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
GREY = (140, 140, 140)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SNAKE_GREEN = (0, 155, 0) # Not bright green
REGULAR_FONT = "./Gasalt-Regular.ttf"

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

FPS = 15 # TODO: Find optimal fps with possibly lower x,y increments per clock tick.
         # increments depend on but are not equal to block_size. if they were this could mess up the grid system
         # check for first upcoming multiple of block_size, then turn?
BLOCK_SIZE = 20

# TODO: Make proper start menu, with options and local highscore submenus, arrow key movement, possible mouse support
# TODO: Add toggle for boundaries
# TODO: Add local highscore file with related function
# TODO: Add different maps with obstacles?
# TODO: Add different map sizes? small, medium, large
# TODO: Resizeable game window? Need to think about desired behaviour of program_surface

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
        pg.display.set_icon(self.icon)
        # Initialize clock object to tick every FPS times per second
        self.clock = pg.time.Clock() # pg clock object used to set fps
        # Initialize fonts
        self.smallfont = pg.font.Font(REGULAR_FONT, 25) # TODO: find prettier font and matching sizes
        self.medfont = pg.font.Font(REGULAR_FONT, 40) # size 50
        self.largefont = pg.font.Font(REGULAR_FONT, 80) # size 80
        # Initialize options, changeable in options menu
        self.background_color = WHITE
        self.text_color_normal = BLACK
        self.text_color_emphasis = RED
        self.snake_color = SNAKE_GREEN
        self.boundaries = True
        # Call function to reset game variables, in this case initializing them
        self.reset_game_variables()

        """remove this later"""
        # TODO: save dark mode (and other settings) in settings file
        self.toggle_dark_mode()

        
    # Function to initialize game variables at the start, or reset them on game_over
    def reset_game_variables(self):
        self.game_over = False # True if snake is dead but program still running
        self.program_exit = False # True if program is quit
        self.in_game = False # True if the user is actively playing snake
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
    
    def shutdown(self):
        pg.quit()
        exit()

    def draw_main_menu(self):
        # Print introductory messages (start menu)
        self.program_surface.fill(self.background_color)
        self.message_to_screen("Welcome to Slither", self.snake_color, -100, "large")
        self.message_to_screen("The objective of the game is to eat red apples", self.text_color_normal, -30, "med")
        self.message_to_screen("The more apples you eat, the longer you get", self.text_color_normal, 0, "med")
        self.message_to_screen("If you run into yourself or the edges, you die", self.text_color_normal, 30, "med")
        self.message_to_screen("Press C to play, O for options, P to pause or Q to quit", self.text_color_normal, 180, "med")
        pg.display.update()

    def main_menu(self):
        # TODO: Add main_menu functionality
        self.draw_main_menu()

        while not self.program_exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.shutdown()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        self.game_loop()
                        self.draw_main_menu()
                    elif event.key == pg.K_q:
                        self.shutdown()
                    elif event.key == pg.K_o:
                        self.options_menu()
                        self.draw_main_menu()
            
            # TODO: find optimal clock tick here
            # no need for high fps, just dont make the delay on keydown too long
            # Could remove clock.tick() entirely in menus, but that would cause the while
            # loop to run as fast as it can, demanding a lot of unnecessary resources
            self.clock.tick(15)
            

    def draw_options_menu(self):
        self.program_surface.fill(self.background_color)
        self.message_to_screen("Temporary Options menu", self.text_color_normal, -100, "large")
        self.message_to_screen("Press D to toggle dark mode", self.text_color_normal)
        self.message_to_screen(f"Press B to toggle edge boundaries. Currently: {self.boundaries}", self.text_color_normal, 50)
        self.message_to_screen("Press BACKSPACE to return to main menu", self.text_color_normal, 250)
        pg.display.update()

    def options_menu(self):
        self.draw_options_menu()

        in_submenu = True
        while in_submenu:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        in_submenu = False
                    elif event.key == pg.K_d:
                        self.toggle_dark_mode()
                        self.draw_options_menu()
                    elif event.key == pg.K_b:
                        self.boundaries = not self.boundaries
                        self.draw_options_menu()
                elif event.type == pg.QUIT:
                    self.shutdown()
            
            # TODO: find optimal clock tick here
            self.clock.tick(15)
    
    def toggle_dark_mode(self):
        if self.background_color == WHITE:
            self.background_color = BLACK
            self.text_color_normal = WHITE
            # TODO: Find alternative emphasis color?
            #self.text_color_emphasis = RED
            # TODO: Add alternative snake color?
            #self.snake_color = SNAKE_GREEN
        else:
            self.background_color = WHITE
            self.text_color_normal = BLACK
            #self.text_color_emphasis = RED
            #self.snake_color = SNAKE_GREEN

    def rand_apple_gen(self):
        # TODO: Make apple unable to spawn on/under snake

        # randint(0,display_width) could return display_width, meaning we would get an apple with coordinates
        # [display_width, display_height, block_size, block_size], which would appear offscreen
        rand_apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        rand_apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        return rand_apple_x, rand_apple_y

    def print_score(self, score):
        text = self.smallfont.render(f"Score: {score}", True, self.text_color_normal)
        self.program_surface.blit(text, [0,0])

    def pause(self):
        # Update once when paused, then only check for event handling
        self.message_to_screen("Paused", self.text_color_normal, -100, size="large")
        self.message_to_screen("Press C to continue, Q to quit or BACKSPACE to return to the main menu", self.text_color_normal)
        pg.display.update()
        
        paused = True
        while paused:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        paused = False
                    elif event.key == pg.K_BACKSPACE:
                        self.reset_game_variables()
                        paused = False
                    elif event.key == pg.K_q:
                        self.shutdown()
                elif event.type == pg.QUIT:
                    self.shutdown()
            # TODO: find optimal fps here
            self.clock.tick(15) # dont need high fps

    def rotate(self, img, degrees):
        return pg.transform.rotate(img, degrees)

    def draw_snake(self):
        draw_tail = 0 # used in list slicing to determine whether or not to draw the tail without raising index errors
        
        # TODO: If tail calculations cannot be simplified, move them to seperate function
        if len(self.snake_list) > 1: # TODO: code snake to appear fully on game start instead of being generated from the spawning point
                                     # This would remove the need for checking if len(snake_list) > 1
                                     # Currently snake_list is always > 1, except for the very first frame of the game
            draw_tail = 1
            tail_x, tail_y = self.snake_list[0][0], self.snake_list[0][1]
            pretail_x, pretail_y = self.snake_list[1][0], self.snake_list[1][1]
            if pretail_x < tail_x:
                # pretail_x is less than tail_x, so the snake is moving left
                # Exception: When self.boundaries == False AND we're moving right AND pretail has just appeared
                # on the far left of the screen. In that case we still want the tail to be pictured as heading right
                # Similar logic applies for the other directions
                if not self.boundaries and pretail_x >= DISPLAY_WIDTH and pretail_x % DISPLAY_WIDTH == 0:
                    tail = self.rotate(self.tail_img, 270)
                else:
                    tail = self.rotate(self.tail_img, 90)
            elif pretail_y > tail_y: # y greater, going down
                if not self.boundaries and pretail_y < 0 and pretail_y % DISPLAY_HEIGHT == DISPLAY_HEIGHT:# - BLOCK_SIZE:
                    tail = self.tail_img
                else:
                    tail = self.rotate(self.tail_img, 180)
            elif pretail_x > tail_x: # x greater, going right
                if not self.boundaries and pretail_x < 0 and pretail_x % 480 == DISPLAY_WIDTH:# - BLOCK_SIZE:
                    tail = self.rotate(self.tail_img, 90)
                else:
                    tail = self.rotate(self.tail_img, 270)
            elif pretail_y < tail_y: # y less, going up
                if not self.boundaries and pretail_y >= DISPLAY_HEIGHT and pretail_y % DISPLAY_HEIGHT == 0:
                    tail = self.rotate(self.tail_img, 180)
                else:
                    tail = self.tail_img

            self.program_surface.blit(tail, (tail_x % DISPLAY_WIDTH, tail_y % DISPLAY_HEIGHT))
        
        # TODO: Add extra segment images for the body and when we turn a corner
        # TODO: For corner image, check coords before and after current segment to see which way to rotate the image

        # Modulo divisor (%) in coords for when self.boundaries == False
        for x_and_y in self.snake_list[draw_tail:-1]: # the last element is the head, so dont put a square there
            pg.draw.rect(self.program_surface, self.snake_color,
                    [x_and_y[0] % DISPLAY_WIDTH, x_and_y[1] % DISPLAY_HEIGHT, BLOCK_SIZE,BLOCK_SIZE]) # parameters: surface, color, [x,y,width,height]
        
        # blit the snake head image last, so it still shows after self-collision
        # check for game_over to not print the head on the other side of the screen after wall collision
        if not self.game_over:
            self.program_surface.blit(self.head, (self.snake_list[-1][0] % DISPLAY_WIDTH, self.snake_list[-1][1] % DISPLAY_HEIGHT))

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

    def game_over_function(self):
        # Only paste text once
        self.message_to_screen("Game over", self.text_color_emphasis, y_displace=-50, size="large")
        self.message_to_screen("Press C to play again, Q to quit", self.text_color_normal, 50, size="med")
        self.message_to_screen("or BACKSPACE to return to main menu", self.text_color_normal, 100, size="med")
        pg.display.update()
        
        while self.game_over:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.shutdown()
                    elif event.key == pg.K_c:
                        # Reset variables, then reset in_game to True to return to game_loop()
                        self.reset_game_variables()
                        self.in_game = True
                    elif event.key == pg.K_BACKSPACE:
                        # Reset variables, inclucing in_game to False to exit out of game_loop()
                        # and return to main_menu()
                        self.reset_game_variables()
                elif event.type == pg.QUIT:
                    self.shutdown()

    def game_loop(self):
        self.in_game = True
        while self.in_game:
            for event in pg.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
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
                elif event.type == pg.QUIT:
                    self.shutdown()

            self.lead_x += self.lead_x_change
            self.lead_y += self.lead_y_change

            # Add boundaries to the game. If x or y is outside the game window, game over
            if self.boundaries and (self.lead_x >= DISPLAY_WIDTH or self.lead_x < 0 or self.lead_y >= DISPLAY_HEIGHT or self.lead_y < 0):
                self.game_over = True
                # elif not self.boundaries:
                #     if self.lead_x >= DISPLAY_WIDTH:
                #         self.lead_x = 0
                #     elif self.lead_x < 0:
                #         self.lead_x = DISPLAY_WIDTH - BLOCK_SIZE
                #     elif self.lead_y >= DISPLAY_HEIGHT:
                #         self.lead_y = 0
                #     elif self.lead_y < 0:
                #         self.lead_y = DISPLAY_HEIGHT-BLOCK_SIZE

            self.program_surface.fill(self.background_color)
            self.program_surface.blit(self.apple_img, (self.rand_apple_x, self.rand_apple_y))
            
            self.snake_list.append([self.lead_x, self.lead_y])
            
            # TODO: check if this is needed fixing other issue where tail is only drawn on second clocktick.
            # Suspect that the if-statement can then be removed, leaving just del statement
            if len(self.snake_list) >  self.snake_length:
                del self.snake_list[0] # remove the first (oldest) element of the list
            
            # If the head overlaps with any other segment of the snake, game over
            for segment in self.snake_list[:-1]:
                if segment == [self.lead_x, self.lead_y]:
                    self.game_over = True

            self.draw_snake()
            self.print_score(self.score)

            # Collision checking for grid-based and same-size apple/snake
            # Modulo divisor (%) for when boundaries are disabled
            if [self.lead_x % DISPLAY_WIDTH, self.lead_y % DISPLAY_HEIGHT] == [self.rand_apple_x, self.rand_apple_y]:
                self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen()
                self.snake_length += 1
                self.score += 1

            # Non grid-based collision checking for any size snake/apple
            # if (self.lead_x + BLOCK_SIZE > self.rand_apple_x and self.lead_y + BLOCK_SIZE > self.rand_apple_y
            #     and self.lead_x < self.rand_apple_x + BLOCK_SIZE and self.lead_y < self.rand_apple_y + BLOCK_SIZE):
            #     self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen()
            #     self.snake_length += 1
            #     self.score += 1

            pg.display.update() # update the display
            self.clock.tick(FPS) # tick(x) for a game of x frames per second, put this after display.update()

            if self.game_over:
                self.game_over_function()


if __name__ == "__main__":
    snek = Snake()
    snek.main_menu()
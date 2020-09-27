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
GREEN = (0, 255, 0)
SNAKE_GREEN = (0, 155, 0) # Not bright green
FONT = "./Gasalt-Black.ttf"

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600


GAME_FPS = 15 # TODO: Find optimal fps with possibly lower x,y increments per clock tick.
         # increments depend on but are not equal to block_size. if they were this could mess up the grid system
         # check for first upcoming multiple of block_size, then turn?
MENU_FPS = 15
BLOCK_SIZE = 20

# TODO: Make proper start menu, with options and local highscore submenus, arrow key movement, possible mouse support
# TODO: Add local highscore file with related function
# TODO: Add different maps with obstacles?
# TODO: Add different map sizes? small, medium, large
# TODO: Resizeable game window? Need to think about desired behaviour of program_surface
# TODO: bugfix not printing head on self collision
# TODO: bugfix passing through self when boundaries are removed

class Snake():
    def __init__(self):
        # Load images
        try:
            self.icon = pg.image.load("icon.png") # icon should be a 32x32 file
            self.head_img = pg.image.load("snakehead.png") # block_size x block_size pixels
            self.apple_img = pg.image.load("apple.png") # block_size x block_size pixels
            self.tail_img = pg.image.load("snaketail.png") # block_size x block_size pixels
        except pg.error as e:
            print(f"Error: One or more sprites could not be located\n{e}")
            print("Shutting down")
            self.shutdown()
        # Initialize main program surface
        self.program_surface = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT)) # returns a surface object with (w,h) wxh pixels
        pg.display.set_caption("DangerNoodle - A very original game by Jasper")
        pg.display.set_icon(self.icon)
        # Initialize clock object to tick every FPS times per second
        self.clock = pg.time.Clock() # pg clock object used to set fps
        # Initialize fonts
        try:
            self.smallfont = pg.font.Font(FONT, 30) # TODO: find prettier font and matching sizes
            self.medfont = pg.font.Font(FONT, 40) # size 50
            self.largefont = pg.font.Font(FONT, 80) # size 80
        except FileNotFoundError as e:
            print(f"Error: Font could not be located\nProceeding with default system font\n{e}")
            self.smallfont = pg.font.SysFont(None, 30, bold=1)
            self.medfont = pg.font.SysFont(None, 40, bold=1)
            self.largefont = pg.font.SysFont(None, 80, bold=1)
        # Initialize options, changeable in options menu
        self.background_color = WHITE
        self.text_color_normal = BLACK
        self.text_color_emphasis_bad = RED
        self.text_color_emphasis_good = GREEN
        self.snake_color = SNAKE_GREEN
        self.boundaries = True
        self.dark_mode = False
        # Call function to reset game variables, in this case initializing them
        self.reset_game_variables()

        """remove this later"""
        # TODO: save dark mode (and other settings) in settings file
        self.toggle_dark_mode(True)

        
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
        self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen() # TODO: refactor? also comment functionality
    
    def shutdown(self):
        pg.quit()
        exit()

    def draw_main_menu(self, ind_pos):
        # TODO: integrate indicator_pos to add ">" before current selected pos
        self.program_surface.fill(self.background_color)
        self.center_msg_to_screen("Welcome to Slither", self.snake_color, -100, "large")
        self.center_msg_to_screen("Play", self.text_color_normal, 0, "med", show_indicator=ind_pos==0)
        self.center_msg_to_screen("Help", self.text_color_normal, 40, "med", show_indicator=ind_pos==1)
        self.center_msg_to_screen("Options", self.text_color_normal, 80, "med", show_indicator=ind_pos==2)
        self.center_msg_to_screen("Quit", self.text_color_normal, 120, "med", show_indicator=ind_pos==3)
        pg.display.update()

    def main_menu(self):
        # TODO: add mouse support?
        indicator_pos = 0
        number_of_entries = 3 # number of entries in menu - 1
        self.draw_main_menu(indicator_pos)

        while not self.program_exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.shutdown()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        # When enter is pressed, execute code depending on indicator position
                        if indicator_pos == 0:
                            self.game_loop()
                            self.draw_main_menu(indicator_pos)
                        elif indicator_pos == 1:
                            self.help_menu()
                            self.draw_main_menu(indicator_pos)
                        elif indicator_pos == 2:
                            self.options_menu()
                            self.draw_main_menu(indicator_pos)
                        elif indicator_pos == 3:
                            self.shutdown()
                    # Move indicator position up/down with arrow keys, wrap when exceeding entry number
                    elif event.key == pg.K_DOWN:
                        indicator_pos += 1
                        if indicator_pos > number_of_entries:
                            indicator_pos = 0
                        self.draw_main_menu(indicator_pos)
                    elif event.key == pg.K_UP:
                        indicator_pos -= 1
                        if indicator_pos < 0:
                            indicator_pos = number_of_entries
                        self.draw_main_menu(indicator_pos)

            # no need for high fps, just dont make the delay on keydown too long
            # Could remove clock.tick() entirely in menus, but that would cause the while
            # loop to run as fast as it can, demanding a lot of unnecessary resources
            self.clock.tick(MENU_FPS)
            

    def draw_options_menu(self, ind_pos):
        # Set the correct colors for whether or not dark mode/edges are enabled/disabled
        bound_enabled_txt_color = self.text_color_emphasis_good
        bound_disabled_txt_color = self.text_color_emphasis_bad
        if not self.boundaries:
            bound_enabled_txt_color = self.text_color_emphasis_bad
            bound_disabled_txt_color = self.text_color_emphasis_good
        dark_enabled_txt_color = self.text_color_emphasis_bad
        dark_disabled_txt_color = self.text_color_emphasis_good
        if self.dark_mode:
            dark_enabled_txt_color = self.text_color_emphasis_good
            dark_disabled_txt_color = self.text_color_emphasis_bad

        self.program_surface.fill(self.background_color)
        self.center_msg_to_screen("Options", self.text_color_normal, -100, "large")
        self.center_msg_to_screen("Dark mode:", self.text_color_normal)
        self.msg_to_screen("Enabled", dark_enabled_txt_color, DISPLAY_WIDTH//2 - 200, DISPLAY_HEIGHT // 2 + 20, show_indicator=ind_pos==[0,0])
        self.msg_to_screen("Disabled", dark_disabled_txt_color, DISPLAY_WIDTH//2 + 100, DISPLAY_HEIGHT // 2 + 20, show_indicator=ind_pos==[1,0])
        
        self.center_msg_to_screen(f"Edge boundaries", self.text_color_normal, 100)
        self.msg_to_screen("Enabled", bound_enabled_txt_color, DISPLAY_WIDTH//2 - 200, DISPLAY_HEIGHT // 2 + 120, show_indicator=ind_pos==[0,1])
        self.msg_to_screen("Disabled", bound_disabled_txt_color, DISPLAY_WIDTH//2 + 100, DISPLAY_HEIGHT // 2 + 120, show_indicator=ind_pos==[1,1])
        self.center_msg_to_screen("Return to main menu", self.text_color_normal, 250, show_indicator=ind_pos[1]==2)
        pg.display.update()

    def options_menu(self):
        indicator_pos = [0,0]
        number_of_vert_entries = 2 # number of vert entries in menu - 1
        number_of_hor_entries = 1 # number of hor entries in menu - 1
        self.draw_options_menu(indicator_pos)

        in_submenu = True
        while in_submenu:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        # When the user hits enter, execute code depending on indicator position
                        if indicator_pos == [0,0]:
                            self.toggle_dark_mode(True)
                            self.draw_options_menu(indicator_pos)
                        elif indicator_pos == [1,0]:
                            self.toggle_dark_mode(False)
                            self.draw_options_menu(indicator_pos)
                        elif indicator_pos == [0,1]:
                            self.boundaries = True
                            self.draw_options_menu(indicator_pos)
                        elif indicator_pos == [1,1]:
                            self.boundaries = False
                            self.draw_options_menu(indicator_pos)
                        elif indicator_pos[1] == 2:
                            in_submenu = False
                    # Move indicator position with arrow keys, wrap when exceeding entry number 
                    if event.key == pg.K_RIGHT:
                        indicator_pos[0] += 1
                        if indicator_pos[0] > number_of_hor_entries:
                            indicator_pos[0] = 0
                        self.draw_options_menu(indicator_pos)
                    elif event.key == pg.K_LEFT:
                        indicator_pos[0] -= 1
                        if indicator_pos[0] < 0:
                            indicator_pos[0] = number_of_hor_entries
                        self.draw_options_menu(indicator_pos)
                    elif event.key == pg.K_DOWN:
                        indicator_pos[1] += 1
                        if indicator_pos[1] > number_of_vert_entries:
                            indicator_pos[1] = 0
                        self.draw_options_menu(indicator_pos)
                    elif event.key == pg.K_UP:
                        indicator_pos[1] -= 1
                        if indicator_pos[1] < 0:
                            indicator_pos[1] = number_of_vert_entries
                        self.draw_options_menu(indicator_pos)
                elif event.type == pg.QUIT:
                    self.shutdown()
            
            self.clock.tick(MENU_FPS)
    
    def draw_help_menu(self):
        # TODO: Move all (sub)menus up a bit? But stay consistent
        self.program_surface.fill(self.background_color)
        self.center_msg_to_screen("Help", self.text_color_normal, -100, "large")
        self.center_msg_to_screen("You are a hungry snake, looking for food. The objective of", self.text_color_normal, 30 )
        self.center_msg_to_screen("the game is to eat as many apples as possible, without running", self.text_color_normal, 60)
        self.center_msg_to_screen("into yourself or the walls. Your size increases with every", self.text_color_normal, 90)
        self.center_msg_to_screen("apple you eat. If you run into yourself or the edges, you die.", self.text_color_normal, 120)
        self.center_msg_to_screen("Control the snake using the arrow keys.", self.text_color_normal, 150)
        self.center_msg_to_screen("Good luck!", self.text_color_normal, 180)
        self.center_msg_to_screen("Back", self.text_color_normal, 250, "med", show_indicator=True)
        pg.display.update()

    def help_menu(self):
        self.draw_help_menu()

        in_submenu = True
        while in_submenu:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        in_submenu = False
                elif event.type == pg.QUIT:
                    self.shutdown()
            
            self.clock.tick(MENU_FPS)
    
    def draw_pause_menu(self, ind_pos):
        # Re-draw the background images to create a transparent pause menu
        self.draw_in_game_screen()
        # Update once when paused, then only check for event handling
        self.center_msg_to_screen("Game paused", self.text_color_normal, -50, size="large")
        self.center_msg_to_screen("Continue", self.text_color_normal, 50, size="med", show_indicator=ind_pos==0)
        self.center_msg_to_screen("Main menu", self.text_color_normal, 100, size="med", show_indicator=ind_pos==1)
        self.center_msg_to_screen("Quit", self.text_color_normal, 150, size="med", show_indicator=ind_pos==2)
        pg.display.update()

    def pause_menu(self):
        paused = True
        indicator_pos = 0
        number_of_entries = 2 # number of menu entries - 1
        self.draw_pause_menu(indicator_pos)

        while paused:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        if indicator_pos == 0:
                            paused = False
                        elif indicator_pos == 1:
                            self.reset_game_variables()
                            paused = False
                        elif indicator_pos == 2:
                            self.shutdown()
                    elif event.key == pg.K_DOWN:
                        indicator_pos += 1
                        if indicator_pos > number_of_entries:
                            indicator_pos = 0
                        self.draw_pause_menu(indicator_pos)
                    elif event.key == pg.K_UP:
                        indicator_pos -= 1
                        if indicator_pos < 0:
                            indicator_pos = number_of_entries
                        self.draw_pause_menu(indicator_pos)
                elif event.type == pg.QUIT:
                    self.shutdown()
            self.clock.tick(MENU_FPS) # dont need high fps

    def draw_game_over_menu(self, ind_pos):
        # Re-draw the background images to create a transparent game over menu
        self.draw_in_game_screen()
        # Only paste text once
        self.center_msg_to_screen("Game over", self.text_color_emphasis_bad, y_displace=-50, size="large")
        self.center_msg_to_screen("Play again", self.text_color_normal, 50, size="med", show_indicator=ind_pos==0)
        self.center_msg_to_screen("Main menu", self.text_color_normal, 100, size="med", show_indicator=ind_pos==1)
        self.center_msg_to_screen("Quit", self.text_color_normal, 150, size="med", show_indicator=ind_pos==2)
        pg.display.update()
    
    def game_over_menu(self):
        indicator_pos = 0
        number_of_entries = 2 # number of menu entries - 1
        self.draw_game_over_menu(indicator_pos)
        while self.game_over:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        if indicator_pos == 0:
                            # Reset variables, then reset in_game to True to return to game_loop()
                            self.reset_game_variables()
                            self.in_game = True
                        elif indicator_pos == 1:
                            # Reset variables, inclucing in_game to False to exit out of game_loop()
                            # and return to main_menu()
                            self.reset_game_variables()
                        elif indicator_pos == 2:
                            self.shutdown()
                    elif event.key == pg.K_DOWN:
                        indicator_pos += 1
                        if indicator_pos > number_of_entries:
                            indicator_pos = 0
                        self.draw_game_over_menu(indicator_pos)
                    elif event.key == pg.K_UP:
                        indicator_pos -= 1
                        if indicator_pos < 0:
                            indicator_pos = number_of_entries
                        self.draw_game_over_menu(indicator_pos)

                elif event.type == pg.QUIT:
                    self.shutdown()

    def draw_score(self):
        # Score is the current snake length - starting length, currently 2
        text = self.smallfont.render(f"Score: {self.snake_length - 2}", True, self.text_color_normal)
        self.program_surface.blit(text, [0,0])

    def toggle_dark_mode(self, enable):
        if enable:
            self.dark_mode = True
            self.background_color = BLACK
            self.text_color_normal = WHITE
        else:
            self.dark_mode = False
            self.background_color = WHITE
            self.text_color_normal = BLACK
            
    def rand_apple_gen(self):
        # randint(0,display_width) could return display_width, meaning we would get an apple with coordinates
        # [display_width, display_height, block_size, block_size], which would appear offscreen
        rand_apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        rand_apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        # Disallow apple to spawn under snake, modulo operator for when snake is past screen boundaries
        mod_list = [[x % DISPLAY_WIDTH, y % DISPLAY_HEIGHT] for [x,y] in self.snake_list]
        while [rand_apple_x, rand_apple_y] in mod_list:
            rand_apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
            rand_apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        return rand_apple_x, rand_apple_y

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
        # TODO: Fix bug where now it also doesn't print head on self collision
        if not self.game_over:
            self.program_surface.blit(self.head, (self.snake_list[-1][0] % DISPLAY_WIDTH, self.snake_list[-1][1] % DISPLAY_HEIGHT))
    
    def draw_in_game_screen(self):
        self.program_surface.fill(self.background_color)
        self.program_surface.blit(self.apple_img, (self.rand_apple_x, self.rand_apple_y))
        self.draw_score()
        self.draw_snake()

    def rotate(self, img, degrees):
        return pg.transform.rotate(img, degrees)
    
    def text_objects(self, text, color, size):
        if size == "small":
            text_surface = self.smallfont.render(text, True, color) # render message, True (for anti-aliasing), color
        elif size == "med":
            text_surface = self.medfont.render(text, True, color) # render message, True (for anti-aliasing), color
        elif size == "large":
            text_surface = self.largefont.render(text, True, color) # render message, True (for anti-aliasing), color
        return text_surface, text_surface.get_rect()

    def center_msg_to_screen(self, msg, color, y_displace=0, size="small", show_indicator=False, indicator_offset=-50):
        # TODO: clean up text_objects and center_msg_to_screen functions? possibly combine
        text_surface, text_rect = self.text_objects(msg, color, size)
        text_rect.center = (DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2 + y_displace)
        if show_indicator:
            self.indicator_to_screen(text_rect, size, indicator_offset)
        self.program_surface.blit(text_surface, text_rect) # show screen_text on [coords]

    def msg_to_screen(self, msg, color, x_coord, y_coord, size="small", show_indicator=False, indicator_offset=-50):
        text_surface, text_rect = self.text_objects(msg, color, size)
        text_rect.x = x_coord
        text_rect.y = y_coord
        if show_indicator:
            self.indicator_to_screen(text_rect, size, indicator_offset)
        self.program_surface.blit(text_surface, text_rect)

    def indicator_to_screen(self, text_rect, size, offset):
         # text_rect = [x, y, width, height]
         indicator = self.text_objects(">", self.text_color_normal, size)[0] # first entry of (surface, rect) tuple
         self.program_surface.blit(indicator, [text_rect.x + offset, text_rect.y]) # TODO: remove hardcoded offset of 50?


    def game_loop(self):
        self.in_game = True
        while self.in_game:
            # Moved event handling down so screen isn't redrawn when returning to main menu from pause menu

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
            
            self.snake_list.append([self.lead_x, self.lead_y])
            
            # TODO: check if this is needed fixing other issue where tail is only drawn on second clocktick.
            # Suspect that the if-statement can then be removed, leaving just del statement
            if len(self.snake_list) >  self.snake_length:
                del self.snake_list[0] # remove the first (oldest) element of the list
            
            # If the head overlaps with any other segment of the snake, game over
            for segment in self.snake_list[:-1]:
                if segment == [self.lead_x, self.lead_y]:
                    self.game_over = True
            
            self.draw_in_game_screen()

            # Collision checking for grid-based and same-size apple/snake
            # Modulo divisor (%) for when boundaries are disabled
            if [self.lead_x % DISPLAY_WIDTH, self.lead_y % DISPLAY_HEIGHT] == [self.rand_apple_x, self.rand_apple_y]:
                self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen()
                self.snake_length += 1

            # Non grid-based collision checking for any size snake/apple
            # if (self.lead_x + BLOCK_SIZE > self.rand_apple_x and self.lead_y + BLOCK_SIZE > self.rand_apple_y
            #     and self.lead_x < self.rand_apple_x + BLOCK_SIZE and self.lead_y < self.rand_apple_y + BLOCK_SIZE):
            #     self.rand_apple_x, self.rand_apple_y = self.rand_apple_gen()
            #     self.snake_length += 1
            #     self.score += 1

            pg.display.update() # update the display
            self.clock.tick(GAME_FPS) # tick(x) for a game of x frames per second, put this after display.update()

            if self.game_over:
                self.game_over_menu()
            
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
                        self.pause_menu()
                elif event.type == pg.QUIT:
                    self.shutdown()

if __name__ == "__main__":
    snek = Snake()
    snek.main_menu()
try:
    import pygame as pg
except ModuleNotFoundError as e:
    print(f"{e}: The pygame module could not be found")
from sys import exit
from random import randint
import ctypes
import pickle

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

# TODO: Add different maps with obstacles?
# TODO: Add different map sizes? small, medium, large
# TODO: Resizeable game window? Need to think about desired behaviour of program_surface
# TODO: bugfix not printing head on self collision

class Snake():
    def __init__(self):
        # Load images
        try:
            self.icon = pg.image.load("icon.png") # icon should be a 32x32 file
            self.head_img = pg.image.load("snakehead.png") # block_size x block_size pixels
            self.apple_img = pg.image.load("apple.png") # block_size x block_size pixels
            self.tail_img = pg.image.load("snaketail.png") # block_size x block_size pixels
            self.body_img = pg.image.load("body.png")
            self.body_turn_img = pg.image.load("bodyturn.png")
        except pg.error as e:
            print(f"Error: One or more sprites could not be located\n{e}")
            print("Shutting down")
            self.shutdown()
        # Initialize fonts
        try:
            self.smallfont = pg.font.Font(FONT, 30)
            self.medfont = pg.font.Font(FONT, 40) # size 50
            self.largefont = pg.font.Font(FONT, 80) # size 80
        except FileNotFoundError as e:
            print(f"Error: Font could not be located\nProceeding with default system font\n{e}")
            self.smallfont = pg.font.SysFont(None, 30, bold=1)
            self.medfont = pg.font.SysFont(None, 40, bold=1)
            self.largefont = pg.font.SysFont(None, 80, bold=1)
        # Initialize colors, changeable in settings menu
        self.background_color = WHITE
        self.text_color_normal = BLACK
        self.text_color_emphasis_bad = RED
        self.text_color_emphasis_good = GREEN
        self.snake_color = SNAKE_GREEN
        # Initialize highscores
        try:
            with open("highscores.pickle", "rb") as file:
                self.highscores = pickle.load(file)
        except:
            self.highscores = []
            for _ in range(5):
                self.highscores.append( ('', 0) ) #Initialize highscores to empty if no file is found
        # Initialize settings
        try:
            with open("settings.pickle", "rb") as file:
                self.boundaries, self.dark_mode = pickle.load(file)
            if self.dark_mode:
                self.toggle_dark_mode(True)
        except:
            self.boundaries = True
            self.dark_mode = False
        # Initialize main program surface
        self.program_surface = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT)) # returns a surface object with (w,h) wxh pixels
        pg.display.set_caption("DangerNoodle - A very original game by Jasper")
        pg.display.set_icon(self.icon)
        # Initialize clock object to tick every FPS times per second
        self.clock = pg.time.Clock() # pg clock object used to set fps


        # Call function to reset in-game variables, in this case initializing them
        self.reset_game_variables()
        
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
        self.current_score = self.snake_length - 2 # score == current length - base length
        self.head_rotation = 180 # starting direction is down
        self.head = self.rotate(self.head_img, self.head_rotation) # starting direction is down
        self.generate_apple() # Generate initial apple location
    
    def shutdown(self):
        # Store highscores on shutdown
        with open("highscores.pickle", "wb") as file:
            pickle.dump(self.highscores, file)
        with open("settings.pickle", "wb") as file:
            pickle.dump( (self.boundaries, self.dark_mode), file)
        pg.quit()
        exit()

    def draw_main_menu(self, ind_pos):
        self.program_surface.fill(self.background_color)
        self.center_msg_to_screen("Welcome to Slither", self.snake_color, -100, "large")
        self.center_msg_to_screen("Play", self.text_color_normal, 0, "med", show_indicator=ind_pos==0)
        self.center_msg_to_screen("Help", self.text_color_normal, 40, "med", show_indicator=ind_pos==1)
        self.center_msg_to_screen("High-scores", self.text_color_normal, 80, "med", show_indicator=ind_pos==2)
        self.center_msg_to_screen("Settings", self.text_color_normal, 120, "med", show_indicator=ind_pos==3)
        self.center_msg_to_screen("Quit", self.text_color_normal, 160, "med", show_indicator=ind_pos==4)
        pg.display.update()

    def main_menu(self):
        indicator_pos = 0
        number_of_entries = 4 # number of entries in menu - 1
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
                            self.highscore_menu()
                            self.draw_main_menu(indicator_pos)
                        elif indicator_pos == 3:
                            self.settings_menu()
                            self.draw_main_menu(indicator_pos)
                        elif indicator_pos == 4:
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
            

    def draw_settings_menu(self, ind_pos):
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
        self.center_msg_to_screen("Settings", self.text_color_normal, -100, "large")
        self.center_msg_to_screen("Dark mode:", self.text_color_normal)
        self.msg_to_screen("Enabled", dark_enabled_txt_color, DISPLAY_WIDTH//2 - 200, DISPLAY_HEIGHT // 2 + 20, show_indicator=ind_pos==[0,0])
        self.msg_to_screen("Disabled", dark_disabled_txt_color, DISPLAY_WIDTH//2 + 100, DISPLAY_HEIGHT // 2 + 20, show_indicator=ind_pos==[1,0])
        
        self.center_msg_to_screen(f"Edge boundaries", self.text_color_normal, 100)
        self.msg_to_screen("Enabled", bound_enabled_txt_color, DISPLAY_WIDTH//2 - 200, DISPLAY_HEIGHT // 2 + 120, show_indicator=ind_pos==[0,1])
        self.msg_to_screen("Disabled", bound_disabled_txt_color, DISPLAY_WIDTH//2 + 100, DISPLAY_HEIGHT // 2 + 120, show_indicator=ind_pos==[1,1])
        self.center_msg_to_screen("Return to main menu", self.text_color_normal, 250, show_indicator=ind_pos[1]==2)
        pg.display.update()

    def settings_menu(self):
        indicator_pos = [0,0]
        number_of_vert_entries = 2 # number of vert entries in menu - 1
        number_of_hor_entries = 1 # number of hor entries in menu - 1
        self.draw_settings_menu(indicator_pos)

        in_submenu = True
        while in_submenu:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        # When the user hits enter, execute code depending on indicator position
                        if indicator_pos == [0,0]:
                            self.toggle_dark_mode(True)
                            self.draw_settings_menu(indicator_pos)
                        elif indicator_pos == [1,0]:
                            self.toggle_dark_mode(False)
                            self.draw_settings_menu(indicator_pos)
                        elif indicator_pos == [0,1]:
                            self.boundaries = True
                            self.draw_settings_menu(indicator_pos)
                        elif indicator_pos == [1,1]:
                            self.boundaries = False
                            self.draw_settings_menu(indicator_pos)
                        elif indicator_pos[1] == 2:
                            in_submenu = False
                    # Move indicator position with arrow keys, wrap when exceeding entry number 
                    if event.key == pg.K_RIGHT:
                        indicator_pos[0] += 1
                        if indicator_pos[0] > number_of_hor_entries:
                            indicator_pos[0] = 0
                        self.draw_settings_menu(indicator_pos)
                    elif event.key == pg.K_LEFT:
                        indicator_pos[0] -= 1
                        if indicator_pos[0] < 0:
                            indicator_pos[0] = number_of_hor_entries
                        self.draw_settings_menu(indicator_pos)
                    elif event.key == pg.K_DOWN:
                        indicator_pos[1] += 1
                        if indicator_pos[1] > number_of_vert_entries:
                            indicator_pos[1] = 0
                        self.draw_settings_menu(indicator_pos)
                    elif event.key == pg.K_UP:
                        indicator_pos[1] -= 1
                        if indicator_pos[1] < 0:
                            indicator_pos[1] = number_of_vert_entries
                        self.draw_settings_menu(indicator_pos)
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
    
    def draw_highscore_menu(self):
        self.program_surface.fill(self.background_color)
        self.center_msg_to_screen("High-scores", self.text_color_normal, -100, "large")
        offset = 30
        for idx, (name, score) in enumerate(self.highscores):
            if name:
                self.center_msg_to_screen(f"{name}: {score}", self.text_color_normal, (idx+1) * offset, "med")
        self.center_msg_to_screen("Back", self.text_color_normal, 250, "med", show_indicator=True)
        pg.display.update()

    def highscore_menu(self):
        self.draw_highscore_menu()
        in_submenu = True
        while in_submenu:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        in_submenu = False
                elif event.type == pg.QUIT:
                    self.shutdown()
            self.clock.tick(MENU_FPS)

    def update_highscores(self):
        # Max amount of highscores is currently 5
        if len(self.highscores) >= 5:
            for idx, (_, old_score) in enumerate(self.highscores):
                if self.current_score > old_score:
                    new_name = self.highscore_name_input()
                    if new_name: # don't save score when name is empty
                        self.highscores.insert(idx, (new_name, self.current_score) )
                        self.highscores.pop()
                    return # End loop after inserting the new highscore
        else:
            self.highscores.append( ("", self.current_score) )
            self.highscores.sort(reverse=True) # Is this possible for the desired data structure?
    
    def draw_highscore_name_input(self, string):
        self.draw_in_game_screen()
        # Make textbox, user input, keep updating when user enters text
        # Possibly need draw function with inputted string as parameter
        self.center_msg_to_screen("New high-score!", self.text_color_emphasis_good, -100, "large")
        self.center_msg_to_screen("Please enter your name:", self.text_color_normal, -30, "med")
        self.center_msg_to_screen(string, self.text_color_normal, 0, "med")
        pg.display.update()

    def highscore_name_input(self):
        # Called after game over menu if new highscore
        user_string = ''
        self.draw_highscore_name_input(user_string)
        inputting = True
        bkspace = False
        while inputting:
            if bkspace:
                user_string = user_string[:-1]
                self.draw_highscore_name_input(user_string)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        inputting = False
                    elif event.key == pg.K_BACKSPACE:
                        bkspace = True
                    elif event.unicode:
                        user_string += event.unicode
                        self.draw_highscore_name_input(user_string)
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_BACKSPACE:
                        bkspace = False
                elif event.type == pg.QUIT:
                    self.shutdown()
            
            self.clock.tick(MENU_FPS)
        return user_string
    
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
                            # Return to main menu
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
        self.update_highscores()
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
        text = self.smallfont.render(f"Score: {self.current_score}", True, self.text_color_normal)
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

    def generate_apple(self):
        # randint(0,display_width) could return display_width, meaning we would get an apple with coordinates
        # [display_width, display_height, block_size, block_size], which would appear offscreen
        self.apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        self.apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
        # Disallow apple to spawn under snake
        # TODO: remove checklist and check immediately in self.snake_list using some kind of dont-care operator?
        # like while [apple_x, apple_y, _] in self.snakelist
		# https://stackoverflow.com/questions/53488787/is-there-a-dont-care-value-for-lists-in-python/53488822
        checklist = [segment[:2] for segment in self.snake_list]
        while [self.apple_x, self.apple_y] in checklist:
            self.apple_x = round(randint(0, DISPLAY_WIDTH - BLOCK_SIZE)  / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size
            self.apple_y = round(randint(0, DISPLAY_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE # round to nearest block_size

    def draw_snake(self):
        # TODO: code snake to appear fully on game start instead of being generated from the spawning point

        draw_tail = 0 # used in list slicing to determine whether or not to draw the tail without raising index errors
        for idx, segment in enumerate(self.snake_list[draw_tail:-1]): # the last element is the head, so dont put a square there
            if idx == 0:
                body = self.rotate(self.tail_img, self.snake_list[idx+1][2])
            else:
                # currently fails when moving up and turning right, and when moving right and turning up
                # needs respectively extra 270 and 90 degree turns
                # movign up, then right: current segment rotation == 0, next == 270
                # moving right then up: current segment rotaion == 270, then 0
                if segment[2] != self.snake_list[idx+1][2]:
                    # First two conditional statements are filthy hardcoding
                    if self.snake_list[idx+1][2] == 0 and segment[2] == 270:
                        body = self.body_turn_img
                    elif self.snake_list[idx+1][2] == 270 and segment[2] == 0:
                        body = self.rotate(self.body_turn_img, 180)
                    # This is actual calculation
                    # TODO: remove the hardcoded checking for right-then-up and up-then-right movement
                    elif self.snake_list[idx+1][2] > segment[2]:
                        body = self.rotate(self.body_turn_img, self.snake_list[idx+1][2])
                    elif self.snake_list[idx+1][2] < segment[2]:
                        body = self.rotate(self.body_turn_img, (self.snake_list[idx+1][2] + 270) % 360)
                else:
                    body = self.rotate(self.body_img, self.snake_list[idx+1][2])
            self.program_surface.blit(body, (segment[0], segment[1]))
        
        # blit the snake head image last, so it still shows after self-collision
        self.program_surface.blit(self.head, (self.snake_list[-1][0], self.snake_list[-1][1]))
    
    def draw_in_game_screen(self):
        self.program_surface.fill(self.background_color)
        self.program_surface.blit(self.apple_img, (self.apple_x, self.apple_y))
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
         # text_rect is an object with [x, y, width, height] values
         indicator = self.text_objects(">", self.text_color_normal, size)[0] # first entry of (surface, rect) tuple
         self.program_surface.blit(indicator, [text_rect.x + offset, text_rect.y])

    def game_loop(self):
        self.in_game = True
        while self.in_game:
            # Moved event handling down so screen isn't redrawn when returning to main menu from pause menu

            self.lead_x += self.lead_x_change
            self.lead_y += self.lead_y_change

            # Add boundaries to the game. If x or y is outside the game window, game over
            if self.lead_x >= DISPLAY_WIDTH or self.lead_x < 0 or self.lead_y >= DISPLAY_HEIGHT or self.lead_y < 0:
                if self.boundaries:
                    self.game_over = True
                elif not self.boundaries:
                    if self.lead_x >= DISPLAY_WIDTH:
                        self.lead_x = 0
                    elif self.lead_x < 0:
                        self.lead_x = DISPLAY_WIDTH - BLOCK_SIZE
                    elif self.lead_y >= DISPLAY_HEIGHT:
                        self.lead_y = 0
                    elif self.lead_y < 0:
                        self.lead_y = DISPLAY_HEIGHT-BLOCK_SIZE
            
            snake_head = [self.lead_x, self.lead_y, self.head_rotation]
            self.snake_list.append(snake_head)
            
            # TODO: check if this is needed after fixing other issue where tail is only drawn on second clocktick.
            # Suspect that the if-statement can then be removed, leaving just del statement
            if len(self.snake_list) >  self.snake_length:
                del self.snake_list[0] # remove the first (oldest) element of the list
            
            # If the head overlaps with any other segment of the snake, game over
            for segment in self.snake_list[:-1]:
                if segment[:2] == snake_head[:2]:
                    self.game_over = True
            
            self.draw_in_game_screen()

            # Collision checking for grid-based and same-size apple/snake
            if snake_head[:2] == [self.apple_x, self.apple_y]:
                self.generate_apple()
                self.snake_length += 1
                self.current_score += 1

            # Non grid-based collision checking for any size snake/apple
            # if (self.lead_x + BLOCK_SIZE > self.apple_x and self.lead_y + BLOCK_SIZE > self.apple_y
            #     and self.lead_x < self.apple_x + BLOCK_SIZE and self.lead_y < self.apple_y + BLOCK_SIZE):
            #     self.generate_apple()
            #     self.snake_length += 1
            #     self.score += 1

            pg.display.update() # update the display
            self.clock.tick(GAME_FPS) # tick(x) for a game of x frames per second, put this after display.update()

            if self.game_over:  
                self.game_over_menu()
            
            for event in pg.event.get(): # gets all events (mouse movenent, key press/release, quit etc)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        # If moving right, don't allow the user to move left, instead 
                        # break out of loop and get next event
                        if self.lead_x_change == BLOCK_SIZE:
                            break
                        self.lead_x_change = -BLOCK_SIZE
                        self.lead_y_change = 0
                        # Rotate head to face the right way
                        self.head_rotation = 90
                        self.head = self.rotate(self.head_img, self.head_rotation)
                    elif event.key == pg.K_RIGHT:
                        if self.lead_x_change == -BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_x_change = BLOCK_SIZE
                        self.lead_y_change = 0
                        self.head_rotation = 270
                        self.head = self.rotate(self.head_img, self.head_rotation)
                    elif event.key == pg.K_UP:
                        if self.lead_y_change == BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_y_change = -BLOCK_SIZE
                        self.lead_x_change = 0
                        self.head_rotation = 0
                        self.head = self.head_img
                    elif event.key == pg.K_DOWN:
                        if self.lead_y_change == -BLOCK_SIZE: # disallow running into self
                            break
                        self.lead_y_change = BLOCK_SIZE
                        self.lead_x_change = 0
                        self.head_rotation = 180
                        self.head = self.rotate(self.head_img, self.head_rotation)
                    elif event.key == pg.K_p:
                        self.pause_menu()
                elif event.type == pg.QUIT:
                    self.shutdown()

if __name__ == "__main__":
    snek = Snake()
    snek.main_menu()
# DangerNoodle
DangerNoodle is a snake clone, based on the first 42 videos of the The New Boston pygame tutorial playlist:

https://www.youtube.com/playlist?list=PL6gx4Cwl9DGAjkwJocj7vlc_mFU-4wXJq

# How it's similar:
- Same kind of event handling with while loops
- Similar way to save the snakes body
- Same basic gameplay (I mean, it's snake...)

# How it's different:
- Refactored all code to work in class structure
- More than tripled the amount of lines of code
- Completely revamped game and menu visuals using custom-made images
- Added images for the body, the body when making a turn, tail and game icon
- Added functionality to properly display body, turning body and tail depending on previous segment
- Created menu and sub-menu structure with indicator and arrow-key functionality
- Added dark mode and the ability to toggle walls on/off
- Added settings menu to configure above settings
- Added highscore menu and tracking with user-inputted name
- Use pickle to save settings and highscore locally and retrieve them on startup
- Add try/catch blocks with helpful error messages, but still allow user to play if not all files are present
- Rewrote code to more closely comply to PEP8 standards
- Added docstrings and comments

You could say the tutorial taught me how to use pygame using snake as an example,
and allowed me to create my own version of the game pretty much from scratch.
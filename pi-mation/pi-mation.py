	#!/usr/bin/env python

# Pi-Mation v0.5
# Stop motion animation for the Raspberry Pi and camera module
# Russell Barnes - 12 Nov 2013 for Linux User magazine issue 134 
# www.linuxuser.co.uk

import pygame, os, sys, time
import pygame.camera

# global variables
pics_taken = 0
current_alpha, next_alpha = 128, 0	
enable_live_preview = False

# set your desired fps (~5 for beginners, 10+ for advanced users)
fps = 10

# Initialise Pygame, start screen and camera
pygame.init()
res = pygame.display.list_modes() # return the best resolution for your monitor
width, height = res[0] # Having trouble getting the right resolution? Manually set with: 'width, height = 1650, 1050' (where the numbers match your monitor)
#width, height = [640, 480]
print "Reported resolution is:", width, "x", height
start_pic = pygame.image.load(os.path.join('data', 'start_screen.jpg'))
start_pic_fix = pygame.transform.scale(start_pic, (width, height))
screen = pygame.display.set_mode([width, height])
pygame.display.toggle_fullscreen()
pygame.mouse.set_visible = False
play_clock = pygame.time.Clock()

surface = pygame.Surface((width, height)).convert()
pygame.camera.init()
camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], (width, height))
camera.start()

def take_pic():
    """Grabs an image and load it for the alpha preview and 
    appends the name to the animation preview list"""
    global pics_taken, prev_pic
    #camera.capture(os.path.join('pics', 'image_' + str(pics_taken) + '.jpg'), use_video_port = True)
    img = camera.get_image()
    pygame.image.save(img, os.path.join('pics', 'image_' + str(pics_taken) + '.jpg'))
    prev_pic = pygame.image.load(os.path.join('pics', 'image_' + str(pics_taken) + '.jpg'))
    pics_taken += 1	
    # now flash the screen:
    screen.fill((255,255,255))
    pygame.display.update()
    time.sleep(0.02)

def delete_pic():
    """Doesn't actually delete the last picture, but the preview will 
    update and it will be successfully overwritten the next time you take a shot"""
    global pics_taken, prev_pic
    if pics_taken > 0:
        pics_taken -= 1
	if pics_taken >= 1:
	    prev_pic = pygame.image.load(os.path.join('pics', 'image_' + str(pics_taken) + '.jpg'))
        
def animate():
    """Do a quick live preview animation of 
    all current pictures taken"""
    for pic in range(1, pics_taken):
        anim = pygame.image.load(os.path.join('pics', 'image_' + str(pic) + '.jpg'))
        anim = pygame.transform.scale(anim, (width, height))        
        screen.blit(anim, (0, 0))
        play_clock.tick(fps)
        pygame.display.flip()
    play_clock.tick(fps)

def update_display():
    """Blit the screen (behind the camera preview) with the last picture taken"""
    screen.fill((0,0,0))
    cam_img = camera.get_image()
    cam_img = pygame.transform.scale(cam_img, (width, height))
    screen.blit(cam_img, (0, 0))
    if pics_taken > 0:
        scaled_pic = pygame.transform.scale(prev_pic, (width, height))        
        surface.blit(scaled_pic, (0, 0))
        surface.set_alpha(current_alpha)        
        screen.blit(surface, (0,0))

    play_clock.tick(30)
    pygame.display.flip()

def make_movie():
    """Quit out of the application 
    and create a movie with your pics"""
    pygame.quit()
    print "\nQuitting Pi-Mation to transcode your video.\nWarning: this will take a long time!"
    print "\nOnce complete, write 'omxplayer video.mp4' in the terminal to play your video.\n"
    os.system("avconv -r " + str(fps) + " -i " + str((os.path.join('pics', 'image_%d.jpg'))) + " -vcodec libx264 video.mp4")
    sys.exit(0)
    
def change_alpha():
    """Toggle's camera preview optimacy between half and full."""
    global current_alpha, next_alpha
    enable_live_preview = False
    current_alpha, next_alpha = next_alpha, current_alpha
    return next_alpha
    
def quit_app():
    """Cleanly closes the camera and the application"""
    pygame.camera.quit()
    pygame.quit()
    print "You've taken", pics_taken, " pictures. Don't forget to back them up (or they'll be overwritten next time)"
    sys.exit(0)

def intro_screen():
    """Application starts on the help screen. User can exit 
    or start Pi-Mation proper from here"""
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_app()
                elif event.key == pygame.K_F1:
                    intro = False
        screen.blit(start_pic_fix, (0, 0))
        pygame.display.update()

def new_project():
    """starts new project by resetting pics_taken to zero"""
    global pics_taken
    pics_taken = 0
    
    


def main():
    """Begins on the help screen before the main application loop starts"""
    #intro_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_app()
                elif event.key == pygame.K_SPACE:
                    take_pic()
                elif event.key == pygame.K_BACKSPACE:
                    delete_pic()
                elif event.key == pygame.K_RETURN:
                    make_movie()
                elif event.key == pygame.K_TAB:
                    change_alpha()
                elif event.key == pygame.K_F1:
                    intro_screen()
                elif event.key == pygame.K_p:
                    if pics_taken > 1:
                        animate()
                elif event.key == pygame.K_n:
                    new_project()
        update_display()

if __name__ == '__main__':
    main()

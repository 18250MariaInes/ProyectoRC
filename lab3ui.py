import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
from math import cos, sin, pi

#colors for the game
BLACK = (0,0,0)
WHITE = (255,255,255)
BACKGROUND = (62,3,4)


#textures for blocks
textures = {
    '1' : pygame.image.load('block1.png'),
    '2' : pygame.image.load('block5.png'),
    '3' : pygame.image.load('block2.png'),
    '4' : pygame.image.load('block4.png'),
    '5' : pygame.image.load('block3.png')
    }

#background and other images
background=pygame.image.load('bg5.jpg')
mario=pygame.image.load('mario.png')
#set size of mario
mario = pygame.transform.scale(mario, (150, 150))

#class raycaster for the game itself
class Raycaster(object):
    def __init__(self,screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallHeight = 50

        self.stepSize = 5

        #self.setColor(WHITE)

        self.player = {
            "x" : 75,
            "y" : 175,
            "angle" : 0,
            "fov" : 60
            }
    
    #carga del mapa del nivel
    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    #se dibujan los muros del nivel
    def drawRect(self, x, y, tex):
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize))
        rect = tex.get_rect()
        rect = rect.move( (x,y) )
        self.screen.blit(tex, rect)

    #se dibuja el jugador que se mueve en el nivel
    def drawPlayerIcon(self,color):
        rect = (self.player['x'] - 2, self.player['y'] - 2, 5, 5)
        self.screen.fill(color, rect)

    #Los rayos de vista del jugador son calculados
    def castRay(self, a):
        rads = a * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if self.map[j][i] != ' ':
                hitX = x - i*self.blocksize
                hitY = y - j*self.blocksize
                #code for collisions
                if 1 < hitX < self.blocksize - 1:
                    maxHit = hitX
                else:
                    maxHit = hitY

                tx = maxHit / self.blocksize

                return dist, self.map[j][i], tx

            self.screen.set_at((x,y), WHITE)

            dist += 2

    #función para renderizar el juego
    def render(self):

        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):
                
                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if self.map[j][i] != ' ':
                    self.drawRect(x, y, textures[self.map[j][i]])

        self.drawPlayerIcon(BLACK)

        for i in range(halfWidth):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / halfWidth
            dist, wallType, tx = self.castRay(angle)

            x = halfWidth + i 

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle) * wallHeight ----- Formula para el alto de las paredes
            h = self.height / (dist * cos( (angle - self.player['angle']) * pi / 180 )) * self.wallHeight

            start = int( halfHeight - h/2)
            end = int( halfHeight + h/2)
            #carga de imagenes para los bloques
            img = textures[wallType]
            tx = int(tx * img.get_width())

            for y in range(start, end):
                ty = (y - start) / (end - start)
                ty = int(ty * img.get_height())
                texColor = img.get_at((tx, ty))
                self.screen.set_at((x, y), texColor)



        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), BLACK)
            self.screen.set_at( (halfWidth+1, i), BLACK)
            self.screen.set_at( (halfWidth-1, i), BLACK)

#function used by my UIElement to set characteristics of my titles and font           
def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Arial", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

#class for my titles and buttons
class UIElement(Sprite):

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        
        
        self.mouse_over = False  # true if the mouse over the text

        # create the default title, normal size
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # creates title 1.2 time bigger when mouse over it
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        self.action = action #the actions called when clicked

        # calls the init method of the parent sprite class
        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    #can tell if mouse is over or clicked
    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        # title into screen 
        surface.blit(self.image, self.rect)

#class that keeps control of the state of the game
class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1

#main that directs to different screens of my game
def main():
    pygame.init()

    screen = pygame.display.set_mode((1000,500))
    game_state = GameState.TITLE

    while True:
        #title screen
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)
        #game screen
        if game_state == GameState.NEWGAME:
            game_state = play_level(screen)
        #quitting
        if game_state == GameState.QUIT:
            pygame.quit()
            return

def title_screen(screen):
    #title
    game_btn = UIElement(
        center_position=(500, 200),
        font_size=50,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text="SUPER MARIO BROS",
    )
    #start button
    start_btn = UIElement(
        center_position=(500, 300),
        font_size=30,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text="Start",
        action=GameState.NEWGAME,
    )
    #quit button
    quit_btn = UIElement(
        center_position=(500, 400),
        font_size=30,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = [start_btn, quit_btn, game_btn]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
        #imagen for main screen
        screen.blit(background, (-600,-550))
        screen.blit(mario, (600,250))

        
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()

#function called when starting a game
def play_level(screen):
    
    return_btn = UIElement(
        center_position=(870, 450),
        font_size=20,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text="Back to main menu",
        action=GameState.TITLE,
    )
    pygame.init()
    #Set de tamaño de la pantalla
    screen = pygame.display.set_mode((1000,500), pygame.DOUBLEBUF | pygame.HWACCEL) #, pygame.FULLSCREEN)
    screen.set_alpha(None)
    pygame.display.set_caption('Laboratorio3')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)

    #get FPS of game, normally between 3-6 in my project
    def updateFPS():
        fps = str(int(clock.get_fps()))
        fps = font.render(fps, 1, pygame.Color("white"))
        return fps

    r = Raycaster(screen)

    #se carga el mapa del nivel del juego en base al .txt
    r.load_map('map.txt')

    isRunning = True
    #return_btn.draw(screen)
    while isRunning:
        mouse_up=False
        return_btn.draw(screen)
        for ev in pygame.event.get():
            
            if ev.type == pygame.QUIT:
                isRunning = False
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                mouse_up = True

            ui_action = return_btn.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            
            pygame.display.flip()
            #to substitute below values
            newX = r.player['x']
            newY = r.player['y']
            #programación de los inputs que acepta el sistema. Usa UP para ir adelante, DOWN para ir ára atrás, LEFT para ir a la izquiera, 
            #RIGHT para ir a la derecha, Q para girar a la izquierda y E para girar a la derecha
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    isRunning = False
                elif ev.key == pygame.K_UP:
                    newX += cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY += sin(r.player['angle'] * pi / 180) * r.stepSize
                elif ev.key == pygame.K_DOWN:
                    newX -= cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY -= sin(r.player['angle'] * pi / 180) * r.stepSize
                elif ev.key == pygame.K_LEFT:
                    newX -= cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY -= sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
                elif ev.key == pygame.K_RIGHT:
                    newX += cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY += sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
                elif ev.key == pygame.K_q:
                    r.player['angle'] -= 5
                elif ev.key == pygame.K_e:
                    r.player['angle'] += 5


                i = int(newX / r.blocksize)
                j = int(newY / r.blocksize)

                if r.map[j][i] == ' ':
                    r.player['x'] = newX
                    r.player['y'] = newY

        screen.fill(pygame.Color("forestgreen")) #Background

        #Sky
        screen.fill(pygame.Color("skyblue"), (int(r.width / 2), 0, int(r.width / 2),int(r.height / 2)))
        
        #Grass
        screen.fill(pygame.Color("forestgreen"), (int(r.width / 2), int(r.height / 2), int(r.width / 2),int(r.height / 2)))

        r.render()
        
        # FPS for the game, displayed in screen
        screen.fill(pygame.Color("black"), (0,0,30,30))
        screen.blit(updateFPS(), (0,0))
        clock.tick(30)  
        
        pygame.display.update()
    
    pygame.quit()

# call main when the script is run
if __name__ == "__main__":
    main()
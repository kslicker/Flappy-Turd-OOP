import pygame as pg
import random


class Player(pg.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.x = 300
        self.y = 250
        self.image = pg.image.load("turd.png")
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.mask = pg.mask.from_surface(self.image)

        # Jump mechanics
        self.gravity = .6
        self.jump_height = 7
        self.velocity = self.jump_height

    def jump(self):
        self.rect.y -= self.velocity
        self.velocity -= self.gravity


class Enemy(pg.sprite.Sprite):

    def __init__(self, x, y):
        super(Enemy, self).__init__()
        self.x = x
        self.y = y
        self.image = pg.image.load("pipe.png")
        self.rect = self.image.get_rect(topleft=(self.x,self.y))
        self.mask = pg.mask.from_surface(self.image)
        

class Enemy180(pg.sprite.Sprite):
    
    def __init__(self, x, y):
        super(Enemy180, self).__init__()
        self.x = x
        self.y = y
        self.image = pg.image.load("pipe180.png")
        self.rect = self.image.get_rect(bottomleft=(self.x,self.y))
        self.mask = pg.mask.from_surface(self.image)

class Game:

    def __init__(self):
        self.screen = pg.display.set_mode((800, 400))
        pg.display.set_caption("Flappy Turd")
        self.bg = pg.image.load("bg.png")
        self.bg2 = pg.image.load("bg.png")
        self.bgx = 0
        self.bg2x = self.bg.get_width()
        self.player = Player()
        self.all_sprites = pg.sprite.Group(self.player)
        self.score = 0
        self.game_on = False
        self.started = False
        self.completed = False
        self.ping_sound = pg.mixer.Sound("score.wav")
        self.fart_sound = pg.mixer.Sound("fart.wav")

        # Fonts
        self.title_font = pg.font.Font("freesansbold.ttf", 100)
        self.title = self.title_font.render("FLAPPY TURD", True, (255,255,255))
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (800 / 2, 50)

        self.start_font = pg.font.Font("freesansbold.ttf", 40)
        self.start = self.start_font.render("Press Space Key To Jump", True, (255,255,255))
        self.startRect = self.start.get_rect()
        self.startRect.center = (800 / 2, 400 / 2)

        self.score_font = pg.font.Font("freesansbold.ttf", 40)
        self.ds = self.score_font.render(f"{self.score}", True, (255,255,255))
        self.ds_rect = self.ds.get_rect()
        self.ds_rect.center = (800 / 2, 50)

        self.final_score_font = pg.font.Font("freesansbold.ttf", 75)
        self.final_score = self.final_score_font.render(f"Score: {self.score}", True, (255,255,255))
        self.final_score_rect = self.final_score.get_rect()
        self.final_score_rect.center = (800 / 2, 320)

        self.congratulations_font = pg.font.Font("freesansbold.ttf", 50)
        self.congratulations = self.congratulations_font.render("Congratulations! You won!", True, (255,255,255))
        self.congratulations_rect = self.congratulations.get_rect()
        self.congratulations_rect.center = (800 / 2, 200)

        # Variable for changing states and clock
        self.done = False
        self.jumping = False
        self.clock = pg.time.Clock()

    def create_pipes(self):
        self.enemies = pg.sprite.Group()
        self.margin = 200
        for x in range(20):
            self.pipe = Enemy(350 + self.margin, random.randint(275,350))
            self.pipe180 = Enemy180(self.pipe.x, self.pipe.y - random.randint(125,225))
            self.enemies.add(self.pipe, self.pipe180)
            self.margin += 400
        self.all_sprites.add(self.enemies)
        self.pipe_width = self.pipe.image.get_width()

    def run(self):
        while not self.done:
            if self.game_on:
                self.event_loop()
                self.update()
                self.draw()
                pg.display.flip()
                self.clock.tick(60)
                if self.completed:
                    self.screen.blit(self.congratulations, self.congratulations_rect)
                    # Clear pipes
                    for sprite in self.all_sprites:
                        if "Enemy" in str(type(sprite)):
                            self.all_sprites.remove(sprite)
                    pg.display.flip()
                    pg.time.wait(3000)
                    self.completed = False
                
            else:
                if self.bgx + self.bg.get_width() <= 0:
                    self.bgx = self.bg.get_width()
                if self.bg2x + self.bg.get_width() <= 0:
                    self.bg2x = self.bg.get_width()

                self.bgx -= 1
                self.bg2x -= 1
                self.player.rect.x = 300
                self.player.rect.y = 250
                self.screen.blit(self.bg, (self.bgx,0))
                self.screen.blit(self.bg2, (self.bg2x,0))
                self.screen.blit(self.title, self.titleRect)
                self.screen.blit(self.start, self.startRect)
                if self.started:
                    self.final_score = self.final_score_font.render(f"Score: {self.score}", True, (255,255,255))
                    self.screen.blit(self.final_score, self.final_score_rect)
                self.all_sprites.draw(self.screen)
                pg.display.flip()
                self.clock.tick(60)

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.done = True

                self.keys = pg.key.get_pressed()

                if self.keys[pg.K_SPACE]:
                    self.game_on = True
                    self.score = 0
                    self.ds = self.score_font.render(f"{self.score}", True, (255,255,255))
                    self.create_pipes()   

    def event_loop(self):
        self.keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True

        if self.keys[pg.K_SPACE]:
            self.game_on = True
            self.started = True
            self.jumping = True
            self.player.velocity = self.player.jump_height

        if self.jumping: 
            self.player.jump()

    def update(self):
        # Check if the player collides with an enemy sprite. The
        # `pygame.sprite.collide_mask` callback uses the `mask`
        # attributes of the sprites for the collision detection.
        if pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_mask):
            self.fart_sound.play()

            # Clear pipes
            for sprite in self.all_sprites:
                if "Enemy" in str(type(sprite)):
                    self.all_sprites.remove(sprite)
            self.game_on = False 
            pg.time.wait(2000)

        # Check if turd leaves the screen
        if self.player.rect.y + self.player.rect.height < 0 or self.player.rect.y > self.screen.get_height():
            self.fart_sound.play()

            # Clear pipes
            for sprite in self.all_sprites:
                if "Enemy" in str(type(sprite)):
                    self.all_sprites.remove(sprite)
            self.game_on = False 
            pg.time.wait(2000)

        # Convert sprite group to list (so we can check every second pipe i.e bottom pipes)
        self.enemy_list = list(self.enemies)

        # If turd passes pipe update score
        for pipe in self.enemy_list[0::2]:
            if 299 <= pipe.rect.x + self.pipe_width <= 300: 
                self.score += 1
                self.ds = self.score_font.render(f"{self.score}", True, (255,255,255))
                self.ping_sound.play()
                if self.score == 20:
                    self.completed = True
                    self.game_on = False
                break

        # Clear pipes that are off screen
        for pipe in self.enemies:
            if pipe.rect.x + self.pipe_width < 0:
                self.enemies.remove(pipe)


    def draw(self):
        # Scroll two background images continuously  
        if self.bgx + self.bg.get_width() <= 0:
            self.bgx = self.bg.get_width()
        if self.bg2x + self.bg.get_width() <= 0:
            self.bg2x = self.bg.get_width()

        # Move the backgrounds to the left
        self.bgx -= 1
        self.bg2x -= 1
        
        # Move the pipes to the left
        for pipe in self.enemies:
            pipe.rect.x -= 2

        # Draw everything onto the screen
        self.screen.blit(self.bg, (self.bgx,0))
        self.screen.blit(self.bg2, (self.bg2x,0))
        if self.game_on:
            self.all_sprites.draw(self.screen)
            self.screen.blit(self.ds, self.ds_rect)

if __name__ == '__main__':
    pg.init()
    game = Game()
    game.run()
    pg.quit()
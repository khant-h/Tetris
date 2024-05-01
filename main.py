import pygame
from random import choices
from sys import exit
from os.path import join

class Game:
  def __init__(self, update_scores):
    #DISPLAY
    self.game_surface = pygame.Surface((300, 600))
    self.game_display_surface = pygame.display.get_surface()
    self.game_rect = self.game_surface.get_rect(topleft = (15, 15))
    self.game_sprites = pygame.sprite.Group()

    #UPDATE SCORE
    self.update_scores = update_scores

    #GRID DISPLAY
    self.game_line_surface = self.game_surface.copy()
    self.game_line_surface.fill((0, 255, 0))
    self.game_line_surface.set_colorkey((0, 255, 0))
    self.game_line_surface.set_alpha(120)

    #FIELD DATA/MATRIX
    self.field_data = [[0 for x in range(12)] for y in range(24)]

    #TETROMINO
    self.tetromino_bag = TetrominoBag()
    self.tetromino = Tetromino(
      self.tetromino_bag.Choose(), 
      self.game_sprites, 
      self.new_tetromino, 
      self.field_data)
    
    #FALL SPEED
    self.speed = 400
    self.speed_faster = self.speed * 0.3
    self.down_pressed = False

    #TIMING
    self.timers = {
       'vertical' : Timer(self.speed, True, self.move_down),
       'horizontal' : Timer(200),
       'rotate' : Timer(200)
    }
    self.timers['vertical'].activate()

    #SCORE BOARD
    self.current_level = 1
    self.current_score = 0
    self.num_lines = 0

  def update_score(self, lines):
    #SCORING SYSTEM
    score_data = {1: 40, 2: 100, 3: 300, 4: 1200}
    self.num_lines += lines
    self.current_score += score_data[lines] * self.current_level

    #LEVEL SYSTEM
    if self.num_lines / 10 > self.current_level:
      self.current_level += 1
      self.speed *= 0.75
      self.speed_faster = self.speed * 0.3
      self.timers['vertical'].duration = self.speed
    self.update_scores(self.current_level, self.current_score)

  def gameover_check(self):
    for block in self.tetromino.blocks:
      if block.pos.y < 0:
        main = Main('GAME OVER!')
        main.run()

  def new_tetromino(self):
    #CHECKING BEFORE THE NEW TETROMINO FALL
    self.gameover_check()
    self.full_row_check()

    #NEW TETROMINO FALL
    self.tetromino = Tetromino(
      self.tetromino_bag.Choose(), 
      self.game_sprites, 
      self.new_tetromino, 
      self.field_data)

  def update_timer(self):
     for timer in self.timers.values():
        timer.update()

  def move_down(self):
     self.tetromino.move_down()

  def draw_grid(self):
    #COLUMN LINES
    for col in range(1, 12):
      pygame.draw.line(self.game_line_surface, '#ffffff', (col * 25, 0), (col * 25, self.game_surface.get_height()), 1)

    #ROW LINES
    for row in range(1, 24):
      pygame.draw.line(self.game_line_surface, '#ffffff', (0, row * 25), (self.game_surface.get_width(), row * 25))

    self.game_surface.blit(self.game_line_surface, (0,0))
  
  def full_row_check(self):
    remove_rows = []

    #ADDING FULL ROW INTO THE TO_BE_REMOVED ROW LIST
    for i, row in enumerate(self.field_data):
      if all(row):
        remove_rows.append(i)
    
    #IF THERE ARE FULL ROWS IN THE LIST, THOSE ROWS WILL BE REMOVED
    if remove_rows:
      for remove_row in remove_rows:
        for block in self.field_data[remove_row]:
          block.kill()

        #DROPING THE NON_REMOVED ROWS WHICH ARE ABOVE THE REMOVED ROWS
        for row in self.field_data:
          for block in row:
            if block and block.pos.y < remove_row:
              block.pos.y += 1
      
      #REBUILDING FIELD DATA
      self.field_data = [[0 for x in range(12)] for y in range(24)]
      for block in self.game_sprites:
        self.field_data[int(block.pos.y)][int(block.pos.x)] = block
    
      self.update_score(len(remove_rows))

  def input(self):
    key = pygame.key.get_pressed()

    #THIS IF STATEMENT PREVENT THE TETROMINO MOVING TOO FAST WITH TIMER CLASS
    if not self.timers['horizontal'].active:
      #MOVE LEFT
      if key[pygame.K_LEFT]:
        self.tetromino.move_horizontal(-1)
        self.timers['horizontal'].activate()
      #MOVE RIGHT
      if key[pygame.K_RIGHT]:
        self.tetromino.move_horizontal(1)
        self.timers['horizontal'].activate()

    #THIS IF STATEMENT PREVENT THE TETROMINO ROTATING TOO FAST WITH TIMER CLASS
    if not self.timers['rotate'].active:
      #ROTATE CLOCKWISE
      if key[pygame.K_UP]:
        self.tetromino.rotate()
        self.timers['rotate'].activate()

    #THOSE TWO IF STATEMENT PREVENT THE FALLING SPEED INCREASE PERMENANTLY BY BOOLEAN EXPRESSION
    if not self.down_pressed and key[pygame.K_DOWN]:
      self.down_pressed = True
      self.timers['vertical'].duration = self.speed_faster

    if self.down_pressed and not key[pygame.K_DOWN]:
      self.down_pressed = False
      self.timers['vertical'].duration = self.speed

  def run(self):
    #UPDATING THE GAME
    self.input()
    self.update_timer()
    self.game_sprites.update()

    #DISPLAY
    self.game_surface.fill('#f0f0f0')
    self.game_sprites.draw(self.game_surface)

    self.draw_grid()
    self.game_display_surface.blit(self.game_surface, (15, 15))

    #GAME DISPLAY BORDER
    pygame.draw.rect(self.game_display_surface, '#ffffff', self.game_rect, 2, 2)


class Start:
  def __init__(self, heading):
    #DISPLAY
    self.heading = heading
    self.active = False
    self.start_surface = pygame.Surface((300, 150))
    self.start_display_surface = pygame.display.get_surface()
    self.start_rect = self.start_surface.get_rect(topleft = (15,15))

    #START BUTTON AND EXIT BUTTON
    self.startbtn = Button(105, 270, 'START')
    self.exitbtn = Button(105, 320, 'EXIT')

    #FONT
    self.font = pygame.font.Font(join('font/Silkscreen-Regular.ttf'), 40)

  def display_text(self, pos, text):
    #TEXT FORMAT FOR HEADING
    text_surface = self.font.render(text, True, '#000000')
    text_rect = text_surface.get_rect(center = pos)
    self.start_surface.blit(text_surface, text_rect)

  def run(self):
    #DISPLAY
    self.start_surface.fill('#ffffff')
    self.display_text((150, 75), self.heading)
    self.start_display_surface.blit(self.start_surface, self.start_rect)

    #CLICKING START
    if self.startbtn.active:
      self.active = True

    #CLICKING EXIT
    if self.exitbtn.active:
      exit()

    self.startbtn.run()
    self.exitbtn.run()


class Button:
  def __init__(self, x, y, text):
    #ACTIVATING BUTTON CHECK
    self.active = False

    #DISPLAY
    self.text = text
    self.button_surface = pygame.Surface((120, 40))
    self.button_display_surface = pygame.display.get_surface()
    self.button_rect = self.button_surface.get_rect(topleft = (x, y))
    self.clicked = False

    #FONT
    self.font = pygame.font.Font(join('font/Silkscreen-Regular.ttf'), 20)
  
  def display_text(self, pos, text):
    #BUTTON TEXT FORMAT
    text_surface = self.font.render(text, True, '#ffffff')
    text_rect = text_surface.get_rect(center = pos)
    self.button_surface.blit(text_surface, text_rect)

  def run(self):
    #MOUSE POSITION ON WINDOWS
    pos = pygame.mouse.get_pos()
    
    #CHECKING THAT MOUSE IS ON THE BUTTON
    if self.button_rect.collidepoint(pos):
      #ACTIVATING BUTTON IF NOT CLICKED
      if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
        self.clicked = True
        self.active = True

    #IF THE MOUSE ISN'T CLICKING THE BUTTON, THE CLICK WILL TURN FALSE. THIS IS TO PREVENT FROM CONTINUOUS ACTIVATING.
    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False

    #DISPLAY
    self.button_surface.fill('#000000')
    self.display_text((60,20), self.text)
    self.button_display_surface.blit(self.button_surface, self.button_rect)


class TetrominoBag:
    def __init__(self):
        self.bag = {}
        self.tetromino_type_list = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

    def MakeDoubleBag(self):
        #ADDING TETROMINOS INTO THE BAG, TWO FOR EACH SHAPE
        for i in self.tetromino_type_list:
            self.bag.update({i: 2})

    def Choose(self):
        #CHECKING THE BAG IS EMPTY. IF EMPTY, CREATE NEW BAG
        if self.bag == {}:
            TetrominoBag.MakeDoubleBag(self)
        
        #CREATING LIST FROM BAG
        lst = [x for x in self.bag.keys()]

        #RANDOMLY CHOOSING FROM THE BAG
        choice = choices(lst, k=1)[0]

        #IF THE CHOSEN TETROMINO IS THE LAST ONE WITHIN THE SAME SHAPE, IT WILL BE POPPED. IF NOT, IT WILL BE SUBTRACTED 1 FROM THE BAG
        if self.bag.get(choice) == 1:
            self.bag.pop(choice)
        else:
            self.bag.update({choice: self.bag.get(choice) - 1})
        return choice


class Tetromino:
  def __init__(self, shape, group, new_tetromino, field_data):
    tetrominos = {
    'T': [(0,0), (-1,0), (1,0), (0,-1)],
    'O': [(0,0), (0,-1), (1,0), (1,-1)],
    'J': [(0,0), (0,-1), (0,1), (-1,1)],
    'L': [(0,0), (0,-1), (0,1), (1,1)],
    'I': [(0,0), (0,-1), (0,-2), (0,1)],
    'S': [(0,0), (-1,0), (0,-1), (1,-1)],
    'Z': [(0,0), (1,0), (0,-1), (-1,-1)]
    }

    self.shape = shape
    self.tetromino_list = tetrominos[shape]
    self.new_tetromino = new_tetromino
    self.field_data = field_data

    #CREATING BLOCK LIST FROM TETROMINO LIST(BLOCK LIST FROM ONE TETROMINO SHAPE)
    self.blocks = [Block(group, pos) for pos in self.tetromino_list]

  def vertical_collision(self, blocks, val):
     #CHECKING THE TETROMINO FROM FALLING PASS THROUGH THE GAME BOARD
     collision_list = [block.vertical_collide(int(block.pos.y + val), self.field_data) for block in self.blocks]
     return True if any(collision_list) else False

  def horizontal_collision(self, blocks, val):
     #CHECKING THE TETROMINO FROM MOVING PASS THROUGH THE GAME BOARD
     collision_list = [block.horizontal_collide(int(block.pos.x + val), self.field_data) for block in self.blocks]
     return True if any(collision_list) else False

  def move_horizontal(self, val):
    #CHECKING IF THERE IS HORIZONTAL MOVEMENT COLLISION OR NOT
    if not self.horizontal_collision(self.blocks, val):
      for block in self.blocks:
        block.pos.x += val

  def move_down(self):
    #CHECKING IF THERE IS VERTICAL MOVEMENT COLLISION OR NOT
    if not self.vertical_collision(self.blocks, 1):
      for block in self.blocks:
        block.pos.y += 1
    #IF THERE IS A COLLISION, IT WILL STOP FALLING AND UPDATE TO THE FIELD DATA AND CREATE A NEW TETROMINO
    else:
      for block in self.blocks:
        self.field_data[int(block.pos.y)][int(block.pos.x)] = block
      self.new_tetromino()

  def rotate(self):
    #SINCE 'O' IS NOT ROTATABLE, CHECK IF THE SHAPE IS 'O' OR NOT
    if self.shape != 'O':
      main_point = self.blocks[0].pos
      #ROTATED POSITION LIST FOR EACH BLOCK EXCEPT MAIN BLOCK
      new_pos = [block.rotate(main_point) for block in self.blocks]

      #ROTATED COLLISION CHECK
      for pos in new_pos:
        if pos.x < 0 or pos.x >= 12 or self.field_data[int(pos.y)][int(pos.x)] or pos.y > 24:
          return

      #ROTATE THE TETROMINO
      for i, block in enumerate(self.blocks):
        block.pos = new_pos[i]


class Block(pygame.sprite.Sprite):
  def __init__(self, group, pos):
    super().__init__(group)
    #DISPLAY
    self.image = pygame.Surface((25, 25))
    self.image.fill('#000000')

    #POSITION
    self.pos = pygame.Vector2(pos) + pygame.Vector2(6, -1)
    self.rect = self.image.get_rect(topleft = self.pos * 25)

  def vertical_collide(self, y, field_data):
    if not y < 24:
      return True
    if y >= 0 and field_data[y][int(self.pos.x)]:
      return True

  def horizontal_collide(self, x, field_data):
    if not 0 <= x < 12:
       return True
    if field_data[int(self.pos.y)][x]:
      return True

  def rotate(self, point):
    #ROTATE 90 DEGREE
    return point + (self.pos - point).rotate(90)

  def update(self):
    self.rect.topleft = self.pos * 25


class Timer:
  def __init__(self, duration, repeat = False, func = None):
    self.repeat = repeat
    self.func = func
    self.duration = duration

    self.start_time = 0
    self.active = False

  def activate(self):
    self.active = True
    self.start_time = pygame.time.get_ticks()

  def deactivate(self):
     self.active = False
     self.start_time = 0
  
  def update(self):
    current_time = pygame.time.get_ticks()
    #DURATION CONTROL THE SPEED OF THE TETROMINO MOVEMENT SO THE TETROMINO WILL BE MOVE IF THE GAP BETWEEN THE START TIME AND THE CURRENT TIME IS EQUAL OR GREATER THAN THE DURATION. THE TIMER ALSO SHOULD BE ACTIVATED. IT WILL ALSO BE LOOPED BY DEACTIVATING AND ACTIVATING IF IT IS REPEATED
    if current_time - self.start_time >= self.duration and self.active:
       if self.func and self.start_time != 0:
          self.func()

       self.deactivate()

       if self.repeat:
          self.activate()


class Score:
  def __init__(self):
    #DISPLAY
    self.score_surface = pygame.Surface((300, 80))
    self.score_rect = self.score_surface.get_rect(bottomright = (315, 710))
    self.score_display_surface = pygame.display.get_surface()

    #FONT
    self.font = pygame.font.Font(join('font/Silkscreen-Regular.ttf'), 20)

    #DIVISION
    self.increment_width = self.score_surface.get_width() / 2

    #CURRENT LEVEL AND SCORE
    self.level = 1
    self.score = 0

  def display_text(self, pos, text):
    #TEXT FORMAT
    text_surface = self.font.render(f'{text[0]}:{text[1]}', True, '#000000')
    text_rect = text_surface.get_rect(center = pos)
    self.score_surface.blit(text_surface, text_rect)

  def run(self):
    #DISPLAY
    self.score_surface.fill('#ffffff')

    #DISPLAY THE LEVEL AND SCORE
    for i, text in enumerate([('Level', self.level), ('Score', self.score)]):
      x = self.increment_width / 2 + i * self.increment_width
      y = self.score_surface.get_height() / 2
      self.display_text((x,y), text)
    self.score_display_surface.blit(self.score_surface, self.score_rect)

    #BORDER
    pygame.draw.rect(self.score_display_surface, '#000000', self.score_rect, 2, 2)


class Main:
  def __init__(self, heading):
    pygame.init()

    #DISPLAY
    self.heading = heading
    self.display_surface = pygame.display.set_mode((330, 725))
    self.clock = pygame.time.Clock()
    pygame.display.set_caption('Tetris By Khant')

    self.start = Start(self.heading)
    self.game = Game(self.update_scores)
    self.score = Score()

  def update_scores(self, level, score):
    self.score.level = level
    self.score.score = score

  def run(self):
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          exit()

      self.display_surface.fill('#FFFFFF')
      self.start.run()

      #AFTER PRESSING START BUTTON, THE GAME WILL RUN
      if self.start.active:
        self.game.run()
        self.score.run()

      #UPDATING DISPLAY
      pygame.display.update()
      self.clock.tick()


if __name__ == '__main__':
  main = Main('TETRIS')
  main.run()
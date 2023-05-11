import random
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SALMON = (250, 128, 114)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKYBLUE = (135, 206, 235)
YELLOW = (255, 212, 0)
PINK = (255, 192, 203)
FOODCOLOR = (None, GREEN, YELLOW, PINK)

class GridObject:
    def __init__(self, x, y, game, color):
        self.game = game
        self.active = True
        self.color = color
        self.x = x  # grid column index
        self.y = y  # grid row index

    def handle_event(self, event):
        pass

    def tick(self):
        pass

    def draw(self):
        block_size = self.game.block_size
        pygame.draw.rect(self.game.display, self.color,
                         [self.x * block_size, self.y * block_size, block_size, block_size])

    def interact(self, other):
        pass

class Player(GridObject):
    dx = 0
    dy = 0

    def __init__(self, x, y, game, head_color, body_color, player_num, move_keys):
        super().__init__(x, y, game, head_color)
        self.bodylist = [self]
        self.time = 0
        self.head_color = head_color
        self.body_color = body_color
        self.player_num = player_num
        self.move_keys = move_keys

    def activate_last_inactive(self):
        '''끝을 늘리는(activate) 함수'''
        for i in range(len(self.bodylist)):
            if not self.bodylist[i].active:
                self.bodylist[i].active = True
                return 0
        return -1

    def deactivate_last_active(self):
        '''끝을 없애는(deactivate) 함수'''
        for i in range(len(self.bodylist) - 1, 0, -1):
            if self.bodylist[i].active:
                self.bodylist[i].active = False
                break

    def show_length(self):
        '''뱀의 길이를 알려주는 함수'''
        length = 0
        for body in self.bodylist:
            if body.active:
                length += 1
        return length

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.move_keys[0]:
                self.dx = -1
                self.dy = 0
            elif event.key == self.move_keys[1]:
                self.dx = 1
                self.dy = 0
            elif event.key == self.move_keys[2]:
                self.dx = 0
                self.dy = -1
            elif event.key == self.move_keys[3]:
                self.dx = 0
                self.dy = 1

    def tick(self):
        '''몸통이 머리를 따라감, 5초 흐를 때마다 길이 1씩 감소, 테두리에 닿으면 끝'''
        self.time += 1
        for i in range(len(self.bodylist) - 1, 0, -1):
            self.bodylist[i].x = self.bodylist[i - 1].x
            self.bodylist[i].y = self.bodylist[i - 1].y
        self.x += self.dx
        self.y += self.dy

        if self.time % 50 == 0 and len(self.bodylist) > 1:
            self.deactivate_last_active()

        if not (5 < self.x < self.game.n_cols + 4 and 5 < self.y < self.game.n_rows + 4):
            self.game.gameover(self.player_num, -1)

        '''길이 24 이상이 되면 승리'''
        if self.show_length() >= 24:
            self.game.gameover(self.player_num, 1)

    def interact(self, other):
        '''음식 먹으면 value만큼 길이 늘어남, Food 랜덤 추가'''
        if isinstance(other, Food):
            if self.x == other.x and self.y == other.y:
                for i in range(other.value):
                    if self.activate_last_inactive() == -1:
                        new_body = PlayerBody(self.bodylist[-1].x, self.bodylist[-1].y,
                                              self.game, self.body_color, self.player_num)
                        self.bodylist.append(new_body)
                        self.game.add_object(new_body)
                other.relocate()

        '''상대 뱀의 몸에 부딪히면 패배'''
        if isinstance(other, PlayerBody):
            if self.x == other.x and self.y == other.y:
                if self.player_num != other.player_num:
                    self.game.gameover(self.player_num, -1)

        def compare_lengths(a,b):
            '''뱀 길이 비교해주는 함수'''
            if a.show_length() < b.show_length():
                a.game.gameover(a.player_num, 1)
                a.game.gameover(b.player_num, -1)
            elif a.show_length() > b.show_length():
                a.game.gameover(a.player_num, -1)
                a.game.gameover(b.player_num, 1)
            else:
                a.game.gameover(a.player_num, 0)
                a.game.gameover(b.player_num, 0)

        '''두 뱀의 머리가 만나면 길이가 짧은 플레이어가 승리, 같으면 무승부'''
        if isinstance(other, Player):
            if self.player_num != other.player_num:
                if (self.x - other.x) == 0 and (self.y - other.y) == 0:
                    if self.x == other.x and self.y == other.y:
                        compare_lengths(self, other)
                if (self.x-self.dx, self.y-self.dy) == (other.x, other.y) and (self.x, self.y) == (other.x-other.dx, other.y-other.dy):
                    compare_lengths(self, other)

class PlayerBody(GridObject):
    def __init__(self, x, y, game, color, player_num):
        super().__init__(x, y, game, color)
        self.active = True
        self.color = color
        self.player_num = player_num

class Food(GridObject):
    def __init__(self, game):
        self.value = random.randint(1, 3)
        self.color = FOODCOLOR[self.value]
        x = random.randint(6, game.n_cols + 3)
        y = random.randint(6, game.n_rows + 3)
        super().__init__(x, y, game, self.color)

    def not_overlap(self, new_x, new_y):
        '''음식 랜덤 생성 위치와 기존 뱀,먹이의 위치와 안 겹치게 하기 위해 필요한 함수'''
        if (new_x, new_y) in self.game.active_coords():
            return True
        return False

    def relocate(self):
        '''음식 랜덤 생성 함수, 기존 뱀,먹이의 위치와 안 겹침'''
        new_x = random.randint(6, self.game.n_cols + 3)
        new_y = random.randint(6, self.game.n_rows + 3)
        self.value = random.randint(1, 3)
        self.color = FOODCOLOR[self.value]

        while self.not_overlap(new_x, new_y):
            new_x = random.randint(6, self.game.n_cols + 3)
            new_y = random.randint(6, self.game.n_rows + 3)

        self.x = new_x
        self.y = new_y

class Game:
    block_size = 10

    def __init__(self, n_rows, n_cols):
        pygame.init()
        pygame.display.set_caption('DCCP Snake Game')
        self.display = pygame.display.set_mode((n_cols * self.block_size + 100, n_rows * self.block_size + 100))
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.objects = []
        self.determine_win = [None, 0, 0]

    def active_objects(self):
        for obj in self.objects:
            if obj.active:
                yield obj

    def active_coords(self):
        '''현재 쓰이고 있는(active한) 좌표들'''
        coord_list = []
        for obj in self.active_objects():
            coord_list.append((obj.x, obj.y))
        return coord_list

    def add_object(self, obj):
        self.objects.append(obj)

    def gameover(self, player_num, win):
        self.determine_win[player_num] += win
        self.game_over = True

    def play(self, n_foods):
        keys_P1 = (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
        keys_P2 = (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
        start_P1 = (self.n_cols//4+5, self.n_rows//2+5)
        start_P2 = (self.n_cols*3//4+5, self.n_rows//2+5)
        head_color_P1 = SKYBLUE
        head_color_P2 = SALMON
        body_color_P1 = BLUE
        body_color_P2 = RED

        self.objects = [
            Player(start_P1[0], start_P1[1], self, head_color_P1, body_color_P1, 1, keys_P1),
            Player(start_P2[0], start_P2[1], self, head_color_P2, body_color_P2, 2, keys_P2),
            *[Food(self) for _ in range(n_foods)]
        ]

        while not self.game_over:
            for event in pygame.event.get():
                # Handle Event
                for obj in self.active_objects():
                    obj.handle_event(event)

            # Tick
            for obj in self.active_objects():
                obj.tick()

            # Interact
            for obj1 in self.active_objects():
                for obj2 in self.active_objects():
                    obj1.interact(obj2)
                    obj2.interact(obj1)

            # Draw
            self.display.fill(BLACK)
            '''흰 테두리 만들기'''
            pygame.draw.line(self.display, WHITE, (50, 50), (self.n_cols*self.block_size+50, 50))
            pygame.draw.line(self.display, WHITE, (50, self.n_rows*self.block_size+50), (self.n_cols*self.block_size+50, self.n_rows*self.block_size+50))
            pygame.draw.line(self.display, WHITE, (50, 50), (50, self.n_rows*self.block_size+50))
            pygame.draw.line(self.display, WHITE, (self.n_cols*self.block_size+50, 50), (self.n_cols*self.block_size+50, self.n_rows*self.block_size+50))
            '''하단에 먹이별 점수 표시'''
            sf = pygame.font.SysFont('Monospace', 15)
            pygame.draw.rect(self.display, FOODCOLOR[1], [self.n_cols*self.block_size//4+50, self.n_rows*self.block_size+70, self.block_size, self.block_size])
            txt1 = sf.render("1", True, WHITE)
            self.display.blit(txt1, (self.n_cols*self.block_size//4+70, self.n_rows*self.block_size+70))
            pygame.draw.rect(self.display, FOODCOLOR[2], [self.n_cols*self.block_size//2+50, self.n_rows*self.block_size+70, self.block_size, self.block_size])
            txt2 = sf.render("2", True, WHITE)
            self.display.blit(txt2, (self.n_cols*self.block_size//2+70, self.n_rows*self.block_size+70))
            pygame.draw.rect(self.display, FOODCOLOR[3], [self.n_cols*self.block_size*3//4+50, self.n_rows*self.block_size+70, self.block_size, self.block_size])
            txt3 = sf.render("3", True, WHITE)
            self.display.blit(txt3, (self.n_cols*self.block_size*3//4+70, self.n_rows*self.block_size+70))
            '''상단에 뱀의 길이 표시'''
            txt4 = sf.render("LEFT : " + str(self.objects[0].show_length()) + ' vs ' + str(self.objects[1].show_length()) + " : RIGHT", True, WHITE)
            self.display.blit(txt4, (self.n_cols*self.block_size//2-50, 25))

            for obj in self.active_objects():
                obj.draw()
            pygame.display.update()

            if self.game_over == True:
                sf = pygame.font.SysFont('Monospace', 30)
                if self.determine_win[1] > self.determine_win[2]:
                    result = sf.render("P1 Win", True, WHITE)
                elif self.determine_win[1] < self.determine_win[2]:
                    result = sf.render("P2 Win", True, WHITE)
                else:
                    result = sf.render('Tie', True, WHITE)
                self.display.blit(result, (self.n_cols*self.block_size*3//4, 10))
                pygame.display.update()
                pygame.time.wait(3000)

            self.clock.tick(10)

if __name__ == "__main__":
    Game(n_rows=40, n_cols=80).play(n_foods=20)
import pygame
import sys
import random
from typing import Literal
from pygame import Vector2


State = Literal['game', 'menu', 'result']
Qst = Literal[0, 1, 2, 3]
ClickedType = Literal['I', 'L', 'J', 'K', 'Z', 'O', 'T',]


# 位置
SIZE = 500, 800


class UserEvent:
    order = pygame.USEREVENT

    def __new__(cls):
        cls.order += 1
        return cls.order


# 游戏切换事件
GAMESHIFT = UserEvent()
# 游戏内部事件
BLOCK_DOWN =  UserEvent()


# 按钮
class Button:
    font: pygame.font.Font

    def __init__(self, text: str, center: tuple[int, int], event: pygame.event.Event) -> None:
        self.img = self.font.render(text, True, "#000000", "#DDDDDD")
        self.rect = self.img.get_rect(center=center)
        self.event = event

        self.border_rect = self.rect.inflate(50, 20)

        # pygame.event.post(self.event)


    def click(self, pos: tuple[int, int]) -> bool:
        if self.border_rect.collidepoint(pos):
            pygame.event.post(self.event)
            return True
        return False


    def draw(self):
        surf = pygame.display.get_surface()
        pygame.draw.rect(surf, "#DDDDDD", self.border_rect)
        surf.blit(self.img, self.rect)


class Result:
    def __init__(self) -> None:
        # 每一张问卷的
        self.qst_list = [
            pygame.transform.scale(pygame.image.load(f"res/QTS/{i}.jpg"), SIZE) for i in range(1, 4)
        ]
        self.rect_list = [
            img.get_rect(center=(SIZE[0] / 2, SIZE[1] / 2))
            for img in self.qst_list
        ]
        # 按钮
        self.back_button = Button(
            "点我返回",
            (SIZE[0] / 2, SIZE[1] / 2),
            pygame.event.Event(GAMESHIFT, {"state": "menu", "qst": 0})
        )
        self.qts = 0

    
    def update(self):
        # 控制
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button != 1:
                continue
            self.back_button.click(event.pos)
        # 绘制
        surf = pygame.display.get_surface()
        surf.blit(self.qst_list[self.qst - 1], self.rect_list[self.qst - 1])
        self.back_button.draw()


    def start_result(self, qts: Qst):
        self.qst = qts
        

class Menu:
    def __init__(self) -> None:
        self.buttons = [
            Button(
                "测试", (SIZE[0] / 2, SIZE[1] * 3 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 0})
            ),
            Button(
                "游戏1", (SIZE[0] / 2, SIZE[1] * 5 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 1})
            ),
            Button(
                "游戏2", (SIZE[0] / 2, SIZE[1] * 7 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 2})
            ),
            Button(
                "游戏3", (SIZE[0] / 2, SIZE[1] * 9 / 12),
                pygame.event.Event(GAMESHIFT, {"state": "game", "qst": 3})
            )
        ]


    def update(self):
        # 事件处理
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button != 1:
                continue
            for button in self.buttons:
                if button.click(event.pos):
                    break
        # 绘制
        for button in self.buttons:
            button.draw()


class Block:
    def __init__(self, image) -> None:
        self.image = image


class BlockSys:
    ROW = 23
    COLUMN = 14
    BS = 32
    BORDER = 5
    MARGIN_X = (SIZE[0] - COLUMN * BS) // 2 - BORDER
    MARGIN_Y = (SIZE[1] - ROW * BS) // 2 - BORDER


    def __init__(self) -> None:
        self.map: list[list[Block | None]] = []
        self.clicked: dict[Block, pygame.Vector2] = []
        # 下落冷却时间
        self.down_cool = 1000
        # 所有图像
        self.images = [
            pygame.transform.scale(pygame.image.load("res/img/blue.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/green.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/indigo.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/orange.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/pink.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/red.png").convert_alpha(), (self.BS, self.BS)),
            pygame.transform.scale(pygame.image.load("res/img/yellow.png").convert_alpha(), (self.BS, self.BS)),
        ]
        self.qts = 0
        # 核心位置,用于旋转
        self.clicked_type: ClickedType = 'I'
        center_x = self.COLUMN // 2
        # 生成
        self.create_block = [
            lambda: [Vector2(center_x - 1, 0), Vector2(center_x, 0), Vector2(center_x + 1, 0), Vector2(center_x + 2, 0)],
            lambda: [Vector2(center_x, 0), Vector2(center_x, 1), Vector2(center_x + 1, 0), Vector2(center_x + 1, 1)],
            lambda: [Vector2(center_x - 1, 0), Vector2(center_x, 0), Vector2(center_x + 1, 0), Vector2(center_x, 1)],
            lambda: [Vector2(center_x - 1, 0), Vector2(center_x, 0), Vector2(center_x + 1, 0), Vector2(center_x - 1, 1)],
            lambda: [Vector2(center_x - 1, 0), Vector2(center_x, 0), Vector2(center_x + 1, 0), Vector2(center_x + 1, 1)],
            lambda: [Vector2(center_x - 1, 0), Vector2(center_x, 0), Vector2(center_x, 1), Vector2(center_x + 1, 1)],
            lambda: [Vector2(center_x - 1, 1), Vector2(center_x, 1), Vector2(center_x, 0), Vector2(center_x + 1, 0)],
        ]
        # border
        self.border_rect = pygame.rect.Rect(
            self.MARGIN_X, self.MARGIN_Y, 
            self.COLUMN * self.BS + 2 * self.BORDER,
            self.ROW * self.BS + 2 * self.BORDER
        )
        self.sound = pygame.mixer.Sound(r'res\sound\getScore.wav')
        self.sound.set_volume(0.5)

    
    def update(self):
        self.contorl()
        self.down()

        self.draw()


    def contorl(self):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.move(pygame.Vector2(-1, 0))
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.move(pygame.Vector2(1, 0))
            elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.shift_clicked()

    
    def down(self):
        if not pygame.event.get(BLOCK_DOWN):
            return
        # 检测能不能下落
        for vect in self.clicked.values():
            if vect.y + 1 >= self.ROW or self.map[int(vect.y + 1)][int(vect.x)]:
                # 不能下落要开始放
                self.put()
                return
        # 下落
        for block in self.clicked:
            self.clicked[block].y += 1
        pygame.time.set_timer(BLOCK_DOWN, self.down_cool, 1)


    def put(self):
        """把手上的砖放在map上"""
        for block, vect in self.clicked.items():
            self.map[int(vect.y)][int(vect.x)] = block
        self.clicked.clear()
        # 检测清除
        if dead_row := self.ckeck_full():
            self.kill_row(dead_row)
        # 添加新的方块
        self.add_clicked()

    
    def draw(self):
        surf = pygame.display.get_surface()
        # border
        pygame.draw.rect(surf, "#DDDDDD", self.border_rect, self.BORDER)
        # map
        for row, blocks in enumerate(self.map):
            for column, block in enumerate(blocks):
                if block is None:
                    continue
                surf.blit(block.image, (self.MARGIN_X + self.BORDER + column * self.BS, self.MARGIN_Y + self.BORDER + row * self.BS))
        # clicked
        for block, vect in self.clicked.items():
            surf.blit(block.image, vect * self.BS + pygame.Vector2(self.MARGIN_X + self.BORDER, self.MARGIN_Y + self.BORDER))
        


    def ckeck_full(self) -> list[int]:
        dead_row = []
        for row in range(self.ROW - 1, -1, -1):
            for column in range(self.COLUMN):
                if self.map[row][column] is None :
                    break
            else:
                dead_row.append(row)
        return dead_row
    

    def move(self, vect: pygame.Vector2):
        # 检测能不能移动
        for vector in self.clicked.values():
            new_vect = vector + vect
            if (new_vect.x < 0 or new_vect.x >= self.COLUMN  
                or self.map[int(new_vect.y)][int(new_vect.x)]):
                return
        # 移动
        for vector in self.clicked.values():
            vector += vect


    def kill_row(self, dead_row: list[int]):
        # 除旧
        for index in dead_row:
            self.map.pop(index)
        # 添新
        self.map.extend([None] * self.COLUMN for _ in range(len(dead_row)))
        # 音效
        self.sound.play()


    def add_clicked(self):
        t = random.randint(0, 6)
        self.clicked = {
            Block(self.images[t]): vect
            for vect in self.create_block[t]()
        }
        for vector in self.clicked.values():
            if self.map[int(vector.y)][int(vector.x)]:
                self.reset()
                return
        # 一段时间后下落
        pygame.time.set_timer(BLOCK_DOWN, self.down_cool, 1)


    def reset(self):
        self.map = [[None] * self.COLUMN for _ in range(self.ROW)]
        self.add_clicked()


    def start_game(self, qts: Qst):
        self.qts = qts
        if qts == 0:
            pygame.time.set_timer(
                pygame.event.Event(GAMESHIFT, {"state": "menu" ,"qst": qts}),
                5 * 60 * 1000, 1 
            )
        else:
            pygame.time.set_timer(
                pygame.event.Event(GAMESHIFT, {"state": "result" ,"qst": qts}),
                5 * 60 * 1000, 1 
            )
        self.reset()

    
    def shift_clicked(self):
        x_max = 0
        x_lock = self.COLUMN
        y_lock = self.ROW
        for vect in self.clicked.values():
            x_max = max(x_max, vect.x)
            x_lock = min(x_lock, vect.x)
            y_lock = min(y_lock, vect.y)
        new_click = {
            block: vect.copy()
            for block, vect in self.clicked.items()
        }
        for vect in new_click.values():
            vect.update(x_lock - (vect.y - y_lock) + (x_max - x_lock) , y_lock + (vect.x - x_lock))
            x, y = int(vect.x), int(vect.y)
            if (x < 0 or x >= self.COLUMN or y < 0 or y >= self.ROW 
                or self.map[y][x]):
                return
        self.clicked = new_click


# 基础game组件
class Windows:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.surface = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()

        Button.font = pygame.font.Font(r'res\font\SmileySans-Oblique-3.otf', 40)


    def update(self):
        ...


    def run(self):
        while True:
            if pygame.event.get(pygame.QUIT):
                pygame.quit()
                sys.exit()
            self.update()
            # pygame.event.clear()
            pygame.display.flip()
            self.clock.tick(60)


# 游戏
class Game(Windows):
    def __init__(self) -> None:
        super().__init__()
        # 程序模式
        self.state: State = 'menu'
        self.qst: Qst = 0
        # 3个功能
        self.result = Result()
        self.block_sys = BlockSys()
        self.menu = Menu()


    def set_mode(self):
        if events := pygame.event.get(GAMESHIFT):
            self.state = events[-1].state
            if self.state == 'game':
                self.block_sys.start_game(events[-1].qst)
            elif self.state == 'result':
                self.result.start_result(events[-1].qst)


    def update(self):        
        self.surface.fill("#334d5c")
        if self.state == 'game':
            self.block_sys.update()
        elif self.state == 'menu':
            self.menu.update()
        else:
            self.result.update()

        self.set_mode()
        return super().update()


Game().run()
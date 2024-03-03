import pygame
import sys
import random
from typing import Literal


State = Literal['game', 'menu', 'result']
Qst = Literal[0, 1, 2, 3]


# 位置
SIZE = 600, 800


class UserEvent:
    order = pygame.USEREVENT

    def __new__(cls):
        cls.order += 1
        return cls.order


# 游戏切换事件
GAMESHIFT = UserEvent()
# 游戏内部事件
BLOCK_DOWN =  UserEvent()
NEED_NEXT =  UserEvent()
ELIMINATE_ROWS =  UserEvent()
# 
CAN_CONTROL = UserEvent()


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
        if self.rect.collidepoint(pos):
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
            pygame.image.load(f"res/QTS/{i}.jpg") for i in range(1, 4)
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

    
    def update(self, qst: Qst):
        # 控制
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button != 1:
                continue
            self.back_button.click(event.pos)
        # 绘制
        surf = pygame.display.get_surface()
        surf.blit(self.qst_list[qst - 1], self.rect_list[qst - 1])
        self.back_button.draw()
        

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
    ...


class BlockSys:
    ROW = 23
    COLUMN = 10

    def __init__(self) -> None:
        self.map: dict[tuple[int, int], Block] = {}
        self.clicked: dict[Block, pygame.Vector2] = []
    

    def update(self, qst: Qst):
        self.contorl()
        self.down()


    def contorl(self):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.move(pygame.Vector2(-1, 0))
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.move(pygame.Vector2(1, 0))
            elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                ...

    
    def down(self):
        if not pygame.event.get(BLOCK_DOWN):
            return
        # 检测能不能下落
        for vect in self.clicked.values():
            if tuple(vect + pygame.Vector2(0, 1)) in self.map or vect.y >= self.ROW:
                self.put()
                return
        # 下落
        for block in self.clicked:
            self.clicked[block].y += 1
        pygame.time.set_timer(BLOCK_DOWN, 1000, 1)


    def put(self):
        """把手上的砖放在map上"""
        for block, vect in self.clicked.items():
            self.map[tuple(vect)] = block
        self.clicked.clear()
        if dead_row := self.ckeck_full():
            self.kill_row(dead_row)

    
    def draw(self):
        ...


    def ckeck_full(self) -> list[int]:
        dead_row = []
        for row in range(self.ROW - 1, -1, -1):
            for column in random(self.COLUMN):
                if (column, row) not in self.map:
                    break
            else:
                dead_row.append(row)
        return dead_row
    

    def move(self, vect: pygame.Vector2):
        # 检测能不能移动
        for vector in self.clicked.values():
            new_vect = vector + vect
            if tuple(new_vect) in self.map or new_vect.x < 0 or new_vect.x >= self.COLUMN:
                return
        # 移动
        for vector in self.clicked.values():
            vector += vect


    def kill_row(self, dead_row: list[int]):
        ...


# 基础game组件
class Windows:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.surface = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("卡牌匹配")
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
            self.qst = events[-1].qst


    def update(self):        
        self.surface.fill("#334d5c")
        if self.state == 'game':
            self.block_sys.update(self.qst)
        elif self.state == 'menu':
            self.menu.update()
        else:
            self.result.update(self.qst)

        self.set_mode()
        return super().update()


Game().run()
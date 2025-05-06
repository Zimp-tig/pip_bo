import os
import time as tims 
import random
from pygame import *

# --- Инициализация Pygame ---
init()

# --------------- Настройка окна -----------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = time.Clock()

# ----- цвета RGB -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 223, 0)


# --------------- Настройка окна -----------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = time.Clock()

# --- поиск файлов изображений в директории где находится скрипт ---
script_dir = os.path.dirname(__file__)

# ------------------------------ фон -----------------------------------
background = image.load(os.path.join(script_dir, "fog.jpg")).convert()
background = transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# -------------------- Игрок -----------------------
player_image = os.path.join(script_dir, "boll.png")

# -------------------- первый игрок -----------------------
plod_image = os.path.join(script_dir, 'plod1.png')

# -------------------- второй игрок -----------------------
plod_image = os.path.join(script_dir, 'plod2.png')

# ---------------- низкое хп первого игрока ---------------
hp_low = os.path.join(script_dir, "hp_low.png")

# --------------- среднее хп первого игрока ---------------
hp_medium = os.path.join(script_dir, "hp_medium.png")

# ------------- полное хп первого игрока ---------------
hp_full = os.path.join(script_dir, "hp_full.png")

# ----------- почти полное хп первого игрока ---------------
hp_nonfull = os.path.join(script_dir, "hp_nonfull.png")

# ------------ общее нулевое хп ------------------
nonhp = os.path.join(script_dir, "nonhp.png")

font.init()
menu_font = font.Font(None, 50)

# --- группы спрайтов --
players = sprite.Group()
bullets = sprite.Group()
enemies = sprite.Group()
enemies_nonbullet = sprite.Group()
hp_sp = sprite.Group()
animation = sprite.Group()

# ---- удаление всех спрайтов ----
def remove_sprites():
    players.empty()
    bullets.empty()
    enemies.empty()
    enemies_nonbullet.empty()
    hp_sp.empty()
    animation.empty()

# ---- глобальные переменные ----
current_difficulty = "normal"
ret = 0 
hp_player1 = 3
hp_player2 = 3
win = False
over = False
game_over = False
hp_game = False

# ------------- использование текста -----------
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

class Anime(sprite.Sprite):
    def __init__(self, frames, pos=(200, 200), fps=10):
        super().__init__()
        
        # Список кадров анимации
        self.frames = frames
        self.current_frame = 0
        
        # Изображение и прямоугольник спрайта
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Таймер для контроля скорости смены кадров
        self.fps = fps
        self.clock = time.Clock()
        self.time_accumulator = 0
        self.frame_index = 0 
        self.game_stop = False
        
    def update(self, dt):
        if self.game_stop:
            return
        
        self.frame_index += 1
        
        if self.frame_index >= 85:
            self.kill()
            self.game_stop = True
            
        # Увеличиваем накопленное время    
        self.time_accumulator += dt
        
        # Сколько времени в секундах должно пройти между кадрами
        interval = self.fps
        
        # Если накопилось достаточно времени — переключаем кадр
        if self.time_accumulator >= interval:
            self.time_accumulator -= interval
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            
   
class Object(sprite.Sprite):
    def __init__(self, x, y, image_path, width, height):
        super().__init__()
        self.image = transform.scale(image.load(image_path), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class GameSprite(sprite.Sprite):
    def __init__(self, image_path, x, y, speed, width, height):
        super().__init__()
        self.image = transform.scale(image.load(image_path), (width, height))
        # числовые координаты
        self.x = x
        self.y = y
        # создаём rect сразу с нужными координатами
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.speed = speed
        

    def reset(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
    def _sync_rect(self):
        self.rect.topleft = (self.x, self.y)    

class Hero(GameSprite):
    def __init__(self, image_path, x, y, base_speed, width, height):
        global current_difficulty
        # Применяем множитель сложности к скорости
        if current_difficulty == "hard":
            adjusted_speed = base_speed * 0.7
        elif current_difficulty == "easy":
            adjusted_speed = base_speed * 1.2
        else:
            adjusted_speed = base_speed
            
        super().__init__(image_path, x, y, adjusted_speed, width, height)
    

class Dager(GameSprite):
    def __init__(self, image_path, x, y, base_speed, width, height):
        global current_difficulty
        # Применяем множитель сложности к скорости
        if current_difficulty == "hard":
            self.adjusted_speed = base_speed * 1.5
        elif current_difficulty == "easy":
            self.adjusted_speed = base_speed * 0.8
        else:
            self.adjusted_speed = base_speed
                
        super().__init__(image_path, x, y, self.adjusted_speed, width, height)
        
    def update(self):
        self.rect.y += self.adjusted_speed

class Player(Hero):
    def __init__(self, image_path, x, y, base_speed, width, height):
        super().__init__(image_path, x, y, base_speed, width, height) 

    def update(self, keys=None):
        #  запоминаем старые координаты
        self.old_x, self.old_y = self.x, self.y
        #  меняем числовые координаты
        if keys:
            if keys[K_LEFT] and self.x > 5:
                self.x -= self.speed
            if keys[K_RIGHT] and self.x < SCREEN_WIDTH - self.rect.width - 5:
                self.x += self.speed
        #  синхронизируем rect
        self.rect.topleft = (self.x, self.y)
     
def load_frames(prefix='death', count=8):
    """
    Загружает изображения с именами prefix0.png ... prefix{count-1}.png
    и возвращает список Surface с alpha-прозрачностью.
    """
    frames = []
    # путь к папке скрипта
    base = os.path.dirname(os.path.abspath(__file__))
    for i in range(count):
        filename = os.path.join(base, f"{prefix}{i}.png")
        img = image.load(filename).convert_alpha()
        frames.append(img)
    return frames        

def game_loop():
    global kills, ret, hp_player, game_over, over, win 
    ret = 0
    kills = 0
    
    # Сбрасываем глобальные флаги состояния при старте новой игры
    hp_player = 4 
    game_over = False
    over = False
    win = False
    

    arial = font.SysFont('arial', 30)

    # --- значения обьектов состояния хп ---
    x_hp = 748
    y_hp = 5
    hp_width = 50
    hp_height = 60

    # -------------- обьекты отображения состояния хп класса Object --------------
    full_hp = Object(x_hp, y_hp, hp_full, hp_width, hp_height)
    nonfull_hp = Object(x_hp, y_hp, hp_nonfull, hp_width, hp_height)
    medium_hp = Object(x_hp, y_hp, hp_medium, hp_width, hp_height)
    low_hp = Object(x_hp, y_hp, hp_low, hp_width, hp_height)
    hpnon = Object(x_hp, y_hp, nonhp, hp_width, hp_height)

    # Убедимся, что группы спрайтов пусты перед началом
    remove_sprites()
    
    # --------------------------------- обьект класса Player -----------------------------------
    player = Player(player_image, SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 100, 5, 50, 80)
    players.add(player)
    
    
    death_frames_loaded = load_frames(prefix='death', count=7) # Загружаем кадры заранее
    # ----------------------------- игровой цикл -------------------------------
    while running:
        dt = clock.tick(60) / 1000

        # ------------- Обработка событий --------------
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    if player_dying:
                        running = False

                elif e.key == K_SPACE:
                    if game_over:  
                        return main()
    # ---------------- Обновление игрового процесса --------------------
        if not game_over:
            spawn_timer1 += dt * 60 # Используем dt для таймеров спавна
            spawn_timer2 += dt * 60

            # Обновление спрайтов основной игры
            keys_pressed = key.get_pressed()
            player.update(keys_pressed) # Обновляем игрока (движение)
            players.update() 
            enemies.update()
            enemies_nonbullet.update()
            bullets.update()

            hp_sp.empty() 
            
            if hp_player == 4:
                hp_sp.add(full_hp)
            
            elif hp_player == 3:
                hp_sp.add(nonfull_hp)
            
            elif hp_player == 2:
                hp_sp.add(medium_hp)
            
            elif hp_player == 1:
                hp_sp.add(low_hp)

            # ------- Проверка на начало смерти игрока ------
            if hp_player1 <= 0:
                player_dying = True
                player_pos = player.rect.center 
                player.kill() 
                hp_sp.empty() 
                hp_sp.add(hpnon) 

                # Создаем анимацию взрыва
                death_anim = Anime(death_frames_loaded, pos=player_pos, fps=0.1) # Используем заранее загруженные кадры
                death_anim.rect.center = player_pos 
                animation.add(death_anim)
                print("Player death animation started")

            # ------- Проверка на другие условия завершения игры ------
            # Проверяем только если игрок еще не умирает
            if kills >= 10:
                game_over = True
                win = True
                print('победа')

            if ret >= 10:
                game_over = True
                over = True
                # remove_sprites()
                print('проигрыш все сбежали ')

        # ------- Обновление анимации --------
        animation.update(dt)
        hp_sp.update() 

        # ------- Проверка на завершение анимации смерти и переход к GAME OVER ------
        if player_dying and not animation: 
            if not game_over: 
                print("Player death animation finished. Game Over.")
                game_over = True
                over = True
                remove_sprites() 

        # -------------------------- Отрисовка ----------------------------
        screen.blit(background, (0, 0))

        if not game_over:
            # Рисуем игровые элементы
            enemies_nonbullet.draw(screen)
            players.draw(screen) # 1
            enemies.draw(screen)
            bullets.draw(screen)
            hp_sp.draw(screen) 
            animation.draw(screen)

            # Текстовые индикаторы
            draw_text(f"Убийства: {kills}", arial, WHITE, screen, 120, 20)
            draw_text(f"Сбежавшие: {ret}", arial, WHITE, screen, 120, 50)

            # Индикатор перезарядки (только если игрок жив)
            if player.alive() and player.reloading: # Проверяем жив ли игрок перед доступом к reloading
                 draw_text("ПЕРЕЗАРЯДКА", arial, YELLOW, screen,
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)


        # ------------------------------------ Отображение экрана "GAME OVER" / "YOU WIN" ----------------------------------
        if game_over:

            if over: # Проигрыш
                
                screen.fill(RED)
                draw_text("GAME OVER", arial, YELLOW, screen, SCREEN_WIDTH // 2, 150)
                draw_text("Нажмите SPACE чтобы вернуться в меню", arial, WHITE, screen, SCREEN_WIDTH // 2, 340)

            elif win: # Выигрыш
                screen.fill(GREEN)
                draw_text("YOU WIN", arial, RED, screen, SCREEN_WIDTH//2, 150)
                draw_text("Нажмите пробел чтобы вернуться в меню", arial, WHITE, screen, SCREEN_WIDTH//2, 340)

        display.flip() # Обновляем весь экран один раз в конце цикла
    pass

def main_menu():
    # - возвращение значений игры в изначальное состояние -
    global hp_player, over, win, game_over, hp_game
    
    hp_game = False
    menu_running = True
    hp_player = 4
    over = False
    win = False
    game_over = False
    
    # ----------------------------------- цикл меню --------------------------------------
    while menu_running:
        screen.fill(GRAY)
        start_button = Rect(300, 200, 200, 50)
        settings_button = Rect(300, 250, 200, 50)
        exit_button = Rect(300, 300, 200, 50)

        mouse_pos = mouse.get_pos()

        start_color = GREEN if start_button.collidepoint(mouse_pos) else WHITE
        settings_color = GREEN if settings_button.collidepoint(mouse_pos) else WHITE
        exit_color = RED if exit_button.collidepoint(mouse_pos) else WHITE

        draw_text("Старт", menu_font, BLACK, screen, 400, 225)
        draw_text("Настройки", menu_font, BLACK, screen, 400, 275)
        draw_text("Выход", menu_font, BLACK, screen, 400, 325)
        draw.rect(screen, start_color, start_button, 2)
        draw.rect(screen, settings_color, settings_button, 2)
        draw.rect(screen, exit_color, exit_button, 2)

        for e in event.get():
            if e.type == QUIT:
                return "exit"
            elif e.type == MOUSEBUTTONDOWN:
                if start_button.collidepoint(e.pos):
                    return "game"
                elif settings_button.collidepoint(e.pos):
                    return "settings"
                elif exit_button.collidepoint(e.pos):
                    return "exit"
        display.flip()

def settings_menu():
    global current_difficulty  # Добавляем доступ к глобальной переменной
    settings_running = True
    difficulty_texts = {
        "normal": "нормальная",
        "hard": "сложная", 
        "easy": "легкая"
    }
    
    while settings_running:
        screen.fill(GRAY)
        mouse_pos = mouse.get_pos()
        
        # Кнопка сложности
        settings_complexity = Rect(250, 100, 212, 50)
        current_text = difficulty_texts[current_difficulty]
        
        if current_difficulty == "normal":
            complexity_color = YELLOW if settings_complexity.collidepoint(mouse_pos) else WHITE
        
        elif current_difficulty == "hard":
            complexity_color = RED if settings_complexity.collidepoint(mouse_pos) else WHITE
            
        elif current_difficulty == "easy":
            complexity_color = GREEN if settings_complexity.collidepoint(mouse_pos) else WHITE    
        
        # Отрисовка элементов
        draw.rect(screen, complexity_color, settings_complexity, 2)
        draw_text(current_text, menu_font, BLACK, screen, 355, 125)
        
        
        
        # Остальные элементы интерфейса
        seting_indicator = Rect(50, 100, 200, 50)
        ramka = Rect(50, 175, 200, 50)
        
        draw_text("Сложность", menu_font, BLACK, screen, 150, 125)
        draw.rect(screen, WHITE, seting_indicator, 2)
        
        draw_text('god mode', menu_font, BLACK, screen, 150, 200)
        draw.rect(screen, WHITE, ramka, 2)
        
        draw_text("ESC возврат", menu_font, BLACK, screen, 130, 570)
        
        
        # Обработка событий
        for e in event.get():
            
            if e.type == QUIT:
                return "exit"
            
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return "menu"
            
            elif e.type == MOUSEBUTTONDOWN:
                
                # Циклическое переключение сложности
                if settings_complexity.collidepoint(e.pos):
                    if current_difficulty == "normal":
                        current_difficulty = "hard"
                    
                    elif current_difficulty == "hard":
                        current_difficulty = "easy"
                    
                    else:
                        current_difficulty = "normal"

        display.flip()

def main():
    current_state = "menu"
    while True:
        if current_state == "menu":
            current_state = main_menu()
        
        elif current_state == "settings":
            current_state = settings_menu()
        
        elif current_state == "game":
            game_loop()
            current_state = "exit"
        
        elif current_state == "exit":
            break

for e in event.get():
    if e.type == QUIT:
        quit()
        os.exit()

if __name__ == "__main__":
    main()

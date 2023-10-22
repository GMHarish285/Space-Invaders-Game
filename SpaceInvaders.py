import pygame, sys, random

pygame.init()
pygame.mixer.pre_init()


def draw_text(font, text, colour, pos_type, pos):
    surf = font.render(text, True, colour)
    rect = surf.get_rect()

    if pos_type == 'midtop':
        rect.midtop = pos
    if pos_type == 'topleft':
        rect.topleft = pos
    if pos_type == 'topright':
        rect.topright = pos

    screen.blit(surf, rect)
    return surf, rect

def make_button(font, text, colour_font, pos_type, pos, colour_inactive, colour_active, screen_change):
    global screen_window, is_pause

    surf = draw_text(font, text, colour_font, pos_type, pos)[0]
    rect = draw_text(font, text, colour_font, pos_type, pos)[1]

    if rect.collidepoint(mouse):
        colour_rect = colour_active
        if event.type == pygame.MOUSEBUTTONDOWN:
            play_sound(sound_button_click)
            screen_window = screen_change
    else:
        colour_rect = colour_inactive
    pygame.draw.rect(screen, colour_rect, rect)
    screen.blit(surf, rect)

def play_sound(sound):
    if sfx_button_state % 2 == 0:
        if sound == sound_lose_life:
            sound.play(maxtime=600)
        elif sound == sound_laser_collide:
            sound.play(maxtime=1000)
        else:
            sound.play()


music_file = 'Assets\\music_arcade_bg.wav'
audio_laser_file = 'Assets\\audio_laser.wav'
audio_laser_collide_file = 'Assets\\audio_laser_collide.wav'
audio_explosion_file = 'Assets\\audio_explosion.wav'
audio_lose_life_file = 'Assets\\audio_lose_life.mp3'
audio_button_click_file = 'Assets\\audio_gamebuttons.wav'
audio_cheats_file = 'Assets\\audio_cheats.mp3'
img_player_file = 'Assets\\player.png'
img_enemy_red_file = 'Assets\\enemy_red.png'
img_enemy_green_file = 'Assets\\enemy_green.png'
img_enemy_yellow_file = 'Assets\\enemy_yellow.png'
img_enemy_blue_file = 'Assets\\enemy_blue.png'
img_obstacles_file = 'Assets\\obstacle.png'
img_pause_button_file = 'Assets\\pause_button.png'
highscore_file = 'Assets\\highscore.txt'
font_style_file = 'Assets\\font_style_arcade.ttf'
img_logo_file = 'Assets\\logo.png'

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")
logo = pygame.image.load(img_logo_file).convert_alpha()
pygame.display.set_icon(logo)
clock = pygame.time.Clock()

pygame.mixer.music.load(music_file)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.7)
sound_laser = pygame.mixer.Sound(audio_laser_file)
sound_laser_collide = pygame.mixer.Sound(audio_laser_collide_file)
sound_explosion = pygame.mixer.Sound(audio_explosion_file)
sound_lose_life = pygame.mixer.Sound(audio_lose_life_file)
sound_button_click = pygame.mixer.Sound(audio_button_click_file)
sound_cheats = pygame.mixer.Sound(audio_cheats_file)
font_small = pygame.font.Font(font_style_file, 33)
font_medium = pygame.font.Font(font_style_file, 50)
font_large = pygame.font.Font(font_style_file, 80)
font_xlarge = pygame.font.Font(font_style_file, 110)

black = (0, 0, 0)
white = (255, 255, 255)
red_dark = (255, 0, 0)
red_light = (255, 127, 127)
green = (0, 255, 0)
blue_dark = (0, 0, 255)
blue_light = (150, 170, 255)

# player
player_surf = pygame.image.load(img_player_file).convert_alpha()
player_rect = player_surf.get_rect(midbottom=(screen_width/2, screen_height - 10))
player_speed = 0
player_speed_increment = 5
player_lives = 3
player_score = 0
player_high_score = 0
is_high_score = False

def update_player():
    screen.blit(player_surf, player_rect)

    if not is_pause:
        player_rect.x += player_speed
    if player_rect.left <= 0:
        player_rect.left = 0
    if player_rect.right >= screen_width:
        player_rect.right = screen_width

def update_high_score():
    global player_high_score, is_high_score

    with open(highscore_file, 'r') as f:  # 'r' to read from the file; 'w' to read,write on the file and if file doesnt exist it creates a new file also
        try:
            player_high_score = int(f.read())  # if nothing is in the file, it returns an error
        except:  # if the code in *try* block gives an error, this *except* block is executed
            player_high_score = 0

    if player_high_score < player_score:
        is_high_score = True
        with open(highscore_file, 'w') as f:
            f.write(str(player_score))
    if is_high_score:
        draw_text(font_medium, 'New High Score!', red_dark, 'midtop', (screen_width / 2, 0))

update_high_score()


# player bullet
player_bullet_surf = pygame.Surface((5, 20))
player_bullet_mask = pygame.mask.from_surface(player_bullet_surf)
player_bullet_rect = player_bullet_surf.get_rect()
player_bullet_state = False
player_bullet_speed = 10

def update_player_bullet():
    global player_bullet_state

    if player_bullet_state:
        pygame.draw.rect(screen, green, player_bullet_rect)
        if not is_pause:
            player_bullet_rect.y -= player_bullet_speed
        if player_bullet_rect.bottom <= 0:
            player_bullet_state = False
    else:
        player_bullet_rect.midbottom = player_rect.midbottom


# enemy
enemy_surf_red = pygame.image.load(img_enemy_red_file).convert_alpha()
enemy_surf_green = pygame.image.load(img_enemy_green_file).convert_alpha()
enemy_surf_yellow = pygame.image.load(img_enemy_yellow_file).convert_alpha()
enemy_speed = 20 * (1 + 1 / 10)
enemy_blue_speed = 2
enemy_surf_blue = pygame.image.load(img_enemy_blue_file).convert_alpha()
enemy_surf_blue_rect = enemy_surf_blue.get_rect(center=(2000, 50))
enemy_details = {'rect': [], 'surf': [], 'surf_colour': []}
last_enemy_movement = pygame.time.get_ticks()
enemy_movement_delay = 500

def make_enemy():
    global enemy_details
    enemy_details = {'rect': [], 'surf': [], 'surf_colour': []}

    for i in range(50, 470, 60):  # no. of columns - 7
        for j in range(100, 301, 50):  # no. of rows - 5
            enemy_details['rect'].append(pygame.Rect(i, j, 40, 32))

    for i in range(len(enemy_details['rect'])):
        if i % 5 == 3 or i % 5 == 4:
            enemy_details['surf'].append(enemy_surf_red)
            enemy_details['surf_colour'].append('red')
        if i % 5 == 1 or i % 5 == 2:
            enemy_details['surf'].append(enemy_surf_green)
            enemy_details['surf_colour'].append('green')
        if i % 5 == 0:
            enemy_details['surf'].append(enemy_surf_yellow)
            enemy_details['surf_colour'].append('yellow')

def update_enemy():
    for j, i in enumerate(enemy_details['surf']):
        screen.blit(i, enemy_details['rect'][j])

    screen.blit(enemy_surf_blue, enemy_surf_blue_rect)
    if not is_pause:
        enemy_surf_blue_rect.x -= enemy_blue_speed
    if enemy_surf_blue_rect.x <= -1000:
        enemy_surf_blue_rect.x = 2000

def move_enemy():
    global enemy_speed

    for i in enemy_details['rect']:
        i.x += enemy_speed

    for i in enemy_details['rect']:
        if enemy_details['rect'][0].left <= 0:
            enemy_speed = 20 * (1 + level_number / 10)
            i.y += 20
        if enemy_details['rect'][-1].right >= screen_width:
            enemy_speed = -(20 * (1 + level_number / 10))
            i.y += 20

make_enemy()


# enemy bullet
enemy_bullet_surf = pygame.Surface((5, 20))
enemy_bullet_mask = pygame.mask.from_surface(enemy_bullet_surf)
enemy_bullet_rect = enemy_bullet_surf.get_rect()
enemy_bullet_speed = 2 * (2.5 + 1 / 10)

def enemy_bullet_reset():
    if enemy_details['rect'] != []:
        enemy_bullet_rect.midtop = random.choice(enemy_details['rect']).midbottom

def update_enemy_bullet():
    pygame.draw.rect(screen, red_dark, enemy_bullet_rect)
    if not is_pause:
        enemy_bullet_rect.y += enemy_bullet_speed
    if enemy_bullet_rect.bottom >= screen_height:
        enemy_bullet_reset()

enemy_bullet_reset()


# obstacles
obstacles_surf = pygame.image.load(img_obstacles_file).convert_alpha()
obstacles_integrity = 25
obstacles_details = {'surf': [], 'mask': [], 'rect': [], 'integrity': [], 'integrity_rect': []}

def make_obstacles():
    global obstacles_details

    obstacles_details = {'surf': [], 'mask': [], 'rect': [], 'integrity': [], 'integrity_rect': []}

    for i in range(4):
        obstacles_details['surf'].append(obstacles_surf)
        obstacles_details['mask'].append(pygame.mask.from_surface(obstacles_details['surf'][i]))
        obstacles_details['rect'].append(obstacles_surf.get_rect())
        obstacles_details['rect'][i].center = (screen_width / 5 * (i + 1), screen_height - 100)
        obstacles_details['integrity'].append(obstacles_integrity)
        obstacles_details['integrity_rect'].append(pygame.Rect(0, 0, 20, 20))
        obstacles_details['integrity_rect'][i].center = (screen_width / 5 * (i + 1), screen_height - 90)

def update_obstacles():
    for i in obstacles_details['rect']:
        screen.blit(obstacles_surf, i)

    for j, i in enumerate(obstacles_details['integrity_rect']):
        obstacles_integrity_surf = font_small.render(str(obstacles_details['integrity'][j]), True, red_dark)
        screen.blit(obstacles_integrity_surf, i)

    for j, i in enumerate(obstacles_details['rect']):
        if obstacles_details['integrity'][j] <= 0:
            obstacles_details['rect'].remove(i)
            obstacles_details['integrity'].pop(j)
            obstacles_details['integrity_rect'].pop(j)

make_obstacles()


# level
level_number = 1

def update_level():
    global enemy_speed, enemy_bullet_speed, player_lives, level_number, enemy_movement_delay

    if enemy_details['rect'] == []:
        make_enemy()
        level_number += 1
        enemy_speed = 20 * (1 + level_number / 10)
        enemy_bullet_speed = 2 * (2.5 + level_number / 10)
        # enemy_movement_delay -= 10
        if player_lives < 3:
            player_lives += 1

    draw_text(font_medium, f'Lives: {player_lives}', white, 'topleft', (5, 5))
    draw_text(font_medium, f'Level: {level_number}', white, 'midtop', (screen_width / 2, 5))
    draw_text(font_medium, f'Score: {player_score}', white, 'topright', (screen_width - 5, 5))


# collisions
def collision_player_bullet():
    global player_score, player_bullet_state

    for j, i in enumerate(enemy_details['rect']):
        if player_bullet_rect.colliderect(i):
            play_sound(sound_explosion)
            enemy_details['rect'].remove(i)  # enemy_details['rect'].remove(enemy_details['rect'][j])
            enemy_details['surf'].pop(j)
            player_bullet_state = False
            if enemy_details['surf_colour'][j] == "red":
                player_score += 5
            if enemy_details['surf_colour'][j] == "green":
                player_score += 10
            if enemy_details['surf_colour'][j] == "yellow":
                player_score += 15
            enemy_details['surf_colour'].pop(j)

    if player_bullet_rect.colliderect(enemy_bullet_rect):
        play_sound(sound_laser_collide)
        player_bullet_state = False
    if player_bullet_rect.colliderect(enemy_surf_blue_rect):
        play_sound(sound_explosion)
        enemy_surf_blue_rect.center = (2000, 50)
        player_score += 100
        player_bullet_state = False

def collision_enemy_bullet():
    global player_lives
    if enemy_bullet_rect.colliderect(player_rect):
        play_sound(sound_lose_life)
        enemy_bullet_reset()
        player_lives -= 1
    if enemy_bullet_rect.colliderect(player_bullet_rect):
        enemy_bullet_reset()

def collision_obstacle():
    global player_bullet_state

    for j, i in enumerate(obstacles_details['rect']):
        offset_x_player_bullet = obstacles_details['rect'][j].topleft[0] - player_bullet_rect.left
        offset_y_player_bullet = obstacles_details['rect'][j].topleft[1] - player_bullet_rect.top
        offset_x_enemy_bullet = obstacles_details['rect'][j].topleft[0] - enemy_bullet_rect.left
        offset_y_enemy_bullet = obstacles_details['rect'][j].topleft[1] - enemy_bullet_rect.top
        if player_bullet_rect.colliderect(i):
            if player_bullet_mask.overlap(obstacles_details['mask'][j], (offset_x_player_bullet, offset_y_player_bullet)):
                obstacles_details['integrity'][j] -= 1
                player_bullet_state = False
        if enemy_bullet_rect.colliderect(i):
            if enemy_bullet_mask.overlap(obstacles_details['mask'][j], (offset_x_enemy_bullet, offset_y_enemy_bullet)):
                obstacles_details['integrity'][j] -= 1
                enemy_bullet_reset()


def reset_game():
    global player_speed, player_lives, player_score, is_high_score, player_bullet_state, \
        enemy_details, enemy_speed, enemy_blue_speed, enemy_surf_blue_rect, enemy_bullet_speed, \
        level_number, is_pause, cheat_string, player_speed_increment, player_bullet_speed

    # player
    player_rect.midbottom = (screen_width / 2, screen_height - 10)
    player_speed = 0
    player_lives = 3
    player_score = 0
    is_high_score = False

    # player bullet
    player_bullet_state = False

    # enemy
    make_enemy()

    enemy_speed = 20 * (1 + 1 / 10)
    enemy_blue_speed = 2
    enemy_surf_blue_rect = enemy_surf_blue.get_rect(center=(2000, 50))

    # enemy bullet
    enemy_bullet_speed = 2 * (2.5 + 1 / 10)

    # obstacles
    make_obstacles()

    # level
    level_number = 1

    is_pause = False

    # cheats
    cheat_string = ''
    player_speed_increment = 5
    player_bullet_speed = 10

def game_over():
    global screen_window
    if player_lives <= 0:
        screen_window = 'end'


# pause
is_pause = False
pause_surf = pygame.image.load(img_pause_button_file)
pause_rect = pause_surf.get_rect(midtop=(screen_width / 2 - 100, 0))
pause_rect_colour = red_dark
resume_text_surf = font_small.render("Resume", True, white)
resume_text_rect = resume_text_surf.get_rect(center=(screen_width / 2, 100))
restart_text_surf = font_small.render("Restart", True, white)
restart_text_rect = restart_text_surf.get_rect(center=(screen_width / 2, 150))
quit_text_surf = font_small.render("Quit", True, white)
quit_text_rect = quit_text_surf.get_rect(center=(screen_width / 2, 200))

def pause_screen():
    if is_pause:
        screen.blit(resume_text_surf, resume_text_rect)
        screen.blit(restart_text_surf, restart_text_rect)
        screen.blit(quit_text_surf, quit_text_rect)
        settings((screen_width / 2 + 50, 250), (screen_width / 2 + 50, 300), False, (screen_width / 2, 250), (screen_width / 2, 300))


# cheats
cheat_string = ''

def cheats():
    global cheat_string, player_lives, player_speed_increment, player_bullet_speed

    if 'deadpool' in cheat_string and player_lives < 3:
        play_sound(sound_cheats)
        player_lives += 1
        cheat_string = ''
    if 'theflash' in cheat_string and player_speed_increment < 10:
        play_sound(sound_cheats)
        player_speed_increment += 0.5
        cheat_string = ''
    if 'bloodsport' in cheat_string and player_bullet_speed < 15:
        play_sound(sound_cheats)
        player_bullet_speed += 0.5
        cheat_string = ''
    if 'strategichomelandinterventionenforcementandlogisticsdivision' in cheat_string:
        cheat_string = ''
        if not is_pause:
            play_sound(sound_cheats)
            make_obstacles()


# settings
music_button_bg_rect = pygame.Rect(screen_width / 2, 200, 30, 20)
music_button_switch_rect = pygame.Rect(screen_width / 2, 200, 12, 15)
music_button_bg_rect_colour = green
music_button_state = 0
sfx_button_bg_rect = pygame.Rect(screen_width / 2, 300, 30, 20)
sfx_button_switch_rect = pygame.Rect(screen_width / 2, 300, 12, 15)
sfx_button_bg_rect_colour = green
sfx_button_state = 0
music_button_bg_rect.topright = (screen_width / 2, 200)
music_button_switch_rect.midleft = music_button_bg_rect.midleft
sfx_button_bg_rect.topright = (screen_width / 2, 300)
sfx_button_switch_rect.midleft = sfx_button_bg_rect.midleft
last_click_music = pygame.time.get_ticks()
last_click_sfx = pygame.time.get_ticks()
last_click_pause = pygame.time.get_ticks()
click_delay = 200

def settings(music_button_bg_rect_pos, sfx_button_bg_rect_pos, settings_screen, music_text_pos, sfx_text_pos):
    global music_button_state, sfx_button_state, music_button_bg_rect_colour, sfx_button_bg_rect_colour, last_click_music, last_click_sfx
    now_click_music = pygame.time.get_ticks()
    now_click_sfx = pygame.time.get_ticks()

    music_button_bg_rect.topright = music_button_bg_rect_pos
    sfx_button_bg_rect.topright = sfx_button_bg_rect_pos

    if settings_screen:
        draw_text(font_large, 'Settings', white, 'midtop', (screen_width / 2, 50))
    draw_text(font_small, 'Music', white, 'topright', music_text_pos)
    draw_text(font_small, 'Sfx', white, 'topright', sfx_text_pos)

    pygame.draw.rect(screen, music_button_bg_rect_colour, music_button_bg_rect)
    pygame.draw.rect(screen, white, music_button_switch_rect)
    pygame.draw.rect(screen, sfx_button_bg_rect_colour, sfx_button_bg_rect)
    pygame.draw.rect(screen, white, sfx_button_switch_rect)

    if music_button_bg_rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN and now_click_music - last_click_music > click_delay:
        last_click_music = now_click_music
        music_button_state += 1
    if sfx_button_bg_rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN and now_click_sfx - last_click_sfx > click_delay:
        last_click_sfx = now_click_sfx
        sfx_button_state += 1

    if music_button_state % 2 == 0:
        pygame.mixer.music.set_volume(0.7)  # pygame.mixer.music.unpause()
        music_button_switch_rect.midleft = music_button_bg_rect.midleft
        music_button_bg_rect_colour = green
    if music_button_state % 2 == 1:
        pygame.mixer.music.set_volume(0)  # pygame.mixer.music.pause()
        music_button_switch_rect.midright = music_button_bg_rect.midright
        music_button_bg_rect_colour = red_light

    if sfx_button_state % 2 == 0:
        sfx_button_switch_rect.midleft = sfx_button_bg_rect.midleft
        sfx_button_bg_rect_colour = green
    if sfx_button_state % 2 == 1:
        sfx_button_switch_rect.midright = sfx_button_bg_rect.midright
        sfx_button_bg_rect_colour = red_light


screen_window = 'start'
while True:
    mouse = pygame.mouse.get_pos()


    if screen_window == 'start':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(black)
        make_button(font_large, 'Play', white, 'midtop', (screen_width / 2, 200), blue_dark, blue_light, 'game')
        make_button(font_large, 'Settings', white, 'midtop', (screen_width / 2, 300), blue_dark, blue_light, 'settings')
        make_button(font_large, 'Credits', white, 'midtop', (screen_width / 2, 400), blue_dark, blue_light, 'credits')
        draw_text(font_xlarge, 'SPACE INVADERS', white, 'midtop', (screen_width / 2, 50))
        reset_game()


    if screen_window == 'settings':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(black)
        make_button(font_medium, '<<Back', black, 'topleft', (0, 0), red_dark, red_light, 'start')
        settings((screen_width / 2, 200), (screen_width / 2, 300), True, (screen_width / 2 - 50, 200), (screen_width / 2 - 50, 300))


    if screen_window == 'credits':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(black)
        make_button(font_medium, '<<Back', black, 'topleft', (0, 0), red_dark, red_light, 'start')
        draw_text(font_xlarge, 'Credits', white, 'midtop', (screen_width / 2, 25))
        draw_text(font_medium, 'Project by:', white, 'midtop', (screen_width / 2, 125))
        draw_text(font_medium, 'Harish', white, 'midtop', (screen_width / 2, 175))

        draw_text(font_medium, 'Project assets from:', white, 'midtop', (screen_width / 2, 330))
        draw_text(font_medium, 'github-clear-code-projects', white, 'midtop', (screen_width / 2, 380))
        draw_text(font_medium, 'www.fesliyanstudios.com', white, 'midtop', (screen_width / 2, 420))
        draw_text(font_medium, 'www.pixabay.com', white, 'midtop', (screen_width / 2, 460))
        draw_text(font_medium, 'www.1001fonts.com', white, 'midtop', (screen_width / 2, 500))
        draw_text(font_medium, 'www.flaticon.com', white, 'midtop', (screen_width / 2, 540))


    if screen_window == 'game':
        now_click_pause = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # player controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_speed = -player_speed_increment
                if event.key == pygame.K_RIGHT:
                    player_speed = player_speed_increment
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not is_pause:
                    if not player_bullet_state:
                        play_sound(sound_laser)
                    player_bullet_state = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player_speed = 0
                if event.key == pygame.K_RIGHT:
                    player_speed = 0

            # pause
            if pause_rect.collidepoint(mouse) and not is_pause:
                pause_rect_colour = red_light
                if event.type == pygame.MOUSEBUTTONDOWN and now_click_pause - last_click_pause > click_delay:
                    last_click_pause = now_click_pause
                    play_sound(sound_button_click)
                    is_pause = True
            else:
                pause_rect_colour = red_dark

            if is_pause and event.type == pygame.MOUSEBUTTONDOWN:
                if resume_text_rect.collidepoint(mouse):
                    play_sound(sound_button_click)
                    is_pause = False
                if restart_text_rect.collidepoint(mouse):
                    play_sound(sound_button_click)
                    reset_game()
                if quit_text_rect.collidepoint(mouse):
                    play_sound(sound_button_click)
                    screen_window = 'end'

            # cheats
            if event.type == pygame.KEYDOWN:
                keyboard_input = event.unicode
                cheat_string += keyboard_input

        cheats()
        screen.fill(black)
        update_player_bullet()
        update_player()
        update_enemy()
        update_enemy_bullet()
        update_obstacles()
        update_level()
        pygame.draw.rect(screen, pause_rect_colour, pause_rect)
        screen.blit(pause_surf, pause_rect)
        collision_player_bullet()
        collision_enemy_bullet()
        collision_obstacle()
        pause_screen()
        game_over()

        now_enemy_movement = pygame.time.get_ticks()
        if now_enemy_movement - last_enemy_movement > enemy_movement_delay and not is_pause:
            last_enemy_movement = now_enemy_movement
            move_enemy()


    if screen_window == 'end':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        screen.fill(black)
        draw_text(font_medium, f'Score: {player_score}', red_dark, 'midtop', (screen_width / 2, 100))
        draw_text(font_medium, f'High Score: {player_high_score}', red_dark, 'midtop', (screen_width / 2, 200))
        make_button(font_large, 'Main Menu', white, 'midtop', (screen_width / 2, 500), blue_dark, blue_light, 'start')
        update_high_score()


    pygame.display.update()
    clock.tick(60)

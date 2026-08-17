import asyncio
import json
import math
import sys

import pygame

try:
    from js import localStorage
except ImportError:
    localStorage = None


def load_high_scores():
    default_scores = {'best_freeplay': 0, 'best_ammo': 0, 'best_timed': 0}

    if localStorage is not None:
        try:
            raw = localStorage.getItem('shoot_it_high_scores')
            if raw:
                data = json.loads(raw)
                default_scores.update(data)
        except Exception as e:
            print("Could not load from localStorage:", e)
    
    if sys.platform != "emscripten":
        try:
            with open('high_scores.txt', 'r') as file:
                lines = file.read().strip().splitlines()
            if len(lines) >= 3:
                default_scores['best_freeplay'] = int(lines[0])
                default_scores['best_ammo'] = int(lines[1])
                default_scores['best_timed'] = int(lines[2])
        except FileNotFoundError:
            pass
    return default_scores

def save_high_scores(best_freeplay, best_ammo, best_timed):
    score_data = {
        'best_freeplay': best_freeplay,
        'best_ammo': best_ammo,
        'best_timed': best_timed,
    }
    if localStorage is not None:
        try:
            localStorage.setItem('shoot_it_high_scores', json.dumps(score_data))
            return
        except Exception as e:
            print("Could not save to localStorage:", e)
    if sys.platform != "emscripten":
        with open('high_scores.txt', 'w') as file:
            file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')

async def main():
    pygame.init()

    fps = 60
    timer = pygame.time.Clock()
    font = pygame.font.Font('assets/font/my_font.ttf', 32)
    big_font = pygame.font.Font('assets/font/my_font.ttf', 60)
    WIDTH = 900
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])

    bgs = []
    banners = []
    guns = []
    target_images = [[], [], []]
    targets = {1: [8, 6, 4], 2: [12, 10, 8], 3: [15, 10, 8, 3]}

    level = 0
    points = 0
    total_shots = 0
    mode = 0
    ammo = 0
    time_passed = 0
    time_remaining = 0
    counter = 1
    shot = False
    menu = True
    game_over = False
    pause = False
    clicked = False
    write_values = False
    new_coords = True
    one_coords = [[], [], []]
    two_coords = [[], [], []]
    three_coords = [[], [], [], []]

    high_scores = load_high_scores()
    best_freeplay = high_scores['best_freeplay']
    best_ammo = high_scores['best_ammo']
    best_timed = high_scores['best_timed']

    menu_img = pygame.image.load('assets/menus/main_menu.png')
    game_over_img = pygame.image.load('assets/menus/game_over.png')
    pause_img = pygame.image.load('assets/menus/pause.png')

    for i in range(1, 4):
        bgs.append(pygame.image.load(f'assets/bgs/{i}.png'))
        banners.append(pygame.image.load(f'assets/banners/{i}.png'))
        guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (110, 110)))

        if i < 3:
            for j in range(1, 4):
                target_images[i - 1].append(
                    pygame.transform.scale(
                        pygame.image.load(f'assets/targets/{i}/{j}.png'),
                        (110 - (j * 18), 80 - (j * 12)),
                    )
                )
        else:
            for j in range(1, 5):
                target_images[i - 1].append(
                    pygame.transform.scale(
                        pygame.image.load(f'assets/targets/{i}/{j}.png'),
                        (120 - (j * 18), 80 - (j * 12)),
                    )
                )

    pygame.mixer.init()
    pygame.mixer.music.load('assets/sounds/bg_music.ogg')
    pygame.mixer.music.set_volume(.3)
    balloon_sound = pygame.mixer.Sound('assets/sounds/assets_sounds_balloon_pop.ogg')
    cup_sound = pygame.mixer.Sound('assets/sounds/assets_sounds_broken_plates.ogg')
    duck_sound = pygame.mixer.Sound('assets/sounds/assets_sounds_drill_gear.ogg')
    balloon_sound.set_volume(.5)
    cup_sound.set_volume(.5)
    duck_sound.set_volume(.5)
    pygame.mixer.music.play()

    def draw_score():
        nonlocal points, total_shots, time_passed, mode, ammo, time_remaining
        points_text = font.render(f'Points: {points}', True, 'black')
        screen.blit(points_text, (320, 660))
        shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
        screen.blit(shots_text, (320, 687))
        time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
        screen.blit(time_text, (320, 714))

        if mode == 0:
            mode_text = font.render(f'Freeplay! {points}', True, 'black')
        elif mode == 1:
            mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
        else:
            mode_text = font.render(f'Time Remaining: {time_remaining}', True, 'black')
        screen.blit(mode_text, (320, 741))

    def draw_gun():
        nonlocal level
        mouse_pos = pygame.mouse.get_pos()
        gun_point = (WIDTH / 2, HEIGHT - 200)
        lasers = ['green', 'purple', 'red']
        clicks = pygame.mouse.get_pressed()

        if mouse_pos[0] != gun_point[0]:
            slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
        else:
            slope = -100000

        angle = math.atan(slope)
        rotation = math.degrees(angle)

        if mouse_pos[0] < WIDTH / 2:
            gun = pygame.transform.flip(guns[level - 1], True, False)
            if mouse_pos[1] < 600:
                screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
                if clicks[0]:
                    pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
        else:
            gun = guns[level - 1]
            if mouse_pos[1] < 600:
                screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
                if clicks[0]:
                    pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)

    def move_level(coords):
        nonlocal level
        if level == 1 or level == 2:
            max_val = 3
        else:
            max_val = 4

        for i in range(max_val):
            for j in range(len(coords[i])):
                my_coords = coords[i][j]
                if my_coords[0] < -150:
                    coords[i][j] = (WIDTH, my_coords[1])
                else:
                    coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])
        return coords

    def draw_level(coords):
        nonlocal level
        if level == 1 or level == 2:
            target_rects = [[], [], []]
        else:
            target_rects = [[], [], [], []]

        for i in range(len(coords)):
            for j in range(len(coords[i])):
                target_rects[i].append(
                    pygame.rect.Rect((coords[i][j][0] + 10, coords[i][j][1]), (70 - i * 12, 70 - i * 12))
                )
                screen.blit(target_images[level - 1][i], coords[i][j])
        return target_rects

    def check_shot(target_rects, coords):
        nonlocal points, level
        mouse_pos = pygame.mouse.get_pos()

        for i in range(len(target_rects)):
            hit_index = None 
            for j in range(len(target_rects[i])): 
                if target_rects[i][j].collidepoint(mouse_pos): 
                    hit_index = j 
                    break 

            if hit_index is not None: 
                coords[i].pop(hit_index) 
                points += 10 + 10 * (i ** 2) 
            if level == 1: 
                balloon_sound.play() 
            elif level == 2: 
                cup_sound.play() 
            elif level == 3: 
                duck_sound.play() 
            break 
        return coords

    def draw_menu():
        nonlocal game_over, pause, mode, level, menu, time_passed, total_shots, points
        nonlocal ammo, time_remaining, best_ammo, best_freeplay, best_timed, write_values, clicked, new_coords

        game_over = False
        pause = False
        screen.blit(menu_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()

        freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
        ammo_button = pygame.rect.Rect((475, 524), (260, 100))
        timed_button = pygame.rect.Rect((170, 661), (260, 100))
        reset_button = pygame.rect.Rect((475, 661), (260, 100))

        screen.blit(font.render(f'{best_freeplay}', True, 'black'), (340, 580))
        screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 580))
        screen.blit(font.render(f'{best_timed}', True, 'black'), (350, 710))

        if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            mode = 0
            level = 1
            menu = False
            time_passed = 0
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True

        if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            mode = 1
            level = 1
            menu = False
            time_passed = 0
            ammo = 84
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True

        if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            mode = 2
            level = 1
            menu = False
            time_remaining = 30
            time_passed = 0
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True

        if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            best_freeplay = 0
            best_ammo = 0
            best_timed = 0
            clicked = True
            write_values = True

    def draw_game_over():
        nonlocal clicked, level, game_over, pause, menu, points, time_remaining, time_passed, total_shots, run

        if mode == 0:
            display_score = time_passed
        else:
            display_score = points

        screen.blit(game_over_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        exit_button = pygame.rect.Rect((170, 661), (260, 100))
        menu_button = pygame.rect.Rect((475, 661), (260, 100))
        screen.blit(big_font.render(f'{display_score}', True, 'black'), (650, 570))

        if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            clicked = True
            level = 0
            pause = False
            game_over = False
            menu = True
            points = 0
            total_shots = 0
            time_passed = 0
            time_remaining = 0

        if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            run = False

    def draw_pause():
        nonlocal level, pause, menu, points, time_remaining, time_passed, total_shots, clicked, new_coords, resume_level

        screen.blit(pause_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        resume_button = pygame.rect.Rect((170, 661), (260, 100))
        menu_button = pygame.rect.Rect((475, 661), (260, 100))

        if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            level = resume_level
            pause = False
            clicked = True

        if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            pygame.mixer.music.play()
            level = 0
            pause = False
            menu = True
            points = 0
            total_shots = 0
            time_passed = 0
            time_remaining = 0
            clicked = True
            new_coords = True

    run = True
    while run:
        timer.tick(fps)

        if level != 0:
            if counter < 60:
                counter += 1
            else:
                counter = 1
                time_passed += 1
                if mode == 2:
                    time_remaining -= 1

        if new_coords:
            one_coords = [[], [], []]
            two_coords = [[], [], []]
            three_coords = [[], [], [], []]

            for i in range(3):
                my_list = targets[1]
                for j in range(my_list[i]):
                    one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 50 * (j % 2)))

            for i in range(3):
                my_list = targets[2]
                for j in range(my_list[i]):
                    two_coords[i].append((WIDTH // (my_list[i]) * j, 340 - (i * 150) + 1 * (j % 2)))

            for i in range(4):
                my_list = targets[3]
                for j in range(my_list[i]):
                    three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 70 * (j % 2)))
            new_coords = False

        screen.fill('black')
        screen.blit(bgs[level - 1], (0, 0)) if level > 0 else None
        if level > 0:
            screen.blit(banners[level - 1], (0, HEIGHT - 200))

        if menu:
            level = 0
            draw_menu()
        if game_over:
            level = 0
            draw_game_over()
        if pause:
            level = 0
            draw_pause()

        if level == 1:
            target_boxes = draw_level(one_coords)
            one_coords = move_level(one_coords)
            if shot:
                one_coords = check_shot(target_boxes, one_coords)
                shot = False
        elif level == 2:
            target_boxes = draw_level(two_coords)
            two_coords = move_level(two_coords)
            if shot:
                two_coords = check_shot(target_boxes, two_coords)
                shot = False
        elif level == 3:
            target_boxes = draw_level(three_coords)
            three_coords = move_level(three_coords)
            if shot:
                three_coords = check_shot(target_boxes, three_coords)
                shot = False

        if level > 0:
            draw_gun()
            draw_score()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = pygame.mouse.get_pos()
                if 0 < mouse_position[0] < WIDTH and 0 < mouse_position[1] < HEIGHT - 200:
                    shot = True
                    total_shots += 1
                    if mode == 1:
                        ammo -= 1
                if 670 < mouse_position[0] < 860 and 660 < mouse_position[1] < 715:
                    resume_level = level
                    pause = True
                    clicked = True
                if 670 < mouse_position[0] < 860 and 715 < mouse_position[1] < 760:
                    menu = True
                    pygame.mixer.music.play()
                    clicked = True
                    new_coords = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
                clicked = False

        if level > 0:
            if target_boxes == [[], [], []] and level < 3:
                level += 1
            if (level == 3 and target_boxes == [[], [], [], []]) or (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0):
                new_coords = True
                pygame.mixer.music.play()
                if mode == 0:
                    if time_passed < best_freeplay or best_freeplay == 0:
                        best_freeplay = time_passed
                        write_values = True
                elif mode == 1:
                    if points > best_ammo:
                        best_ammo = points
                        write_values = True
                elif mode == 2:
                    if points > best_timed:
                        best_timed = points
                        write_values = True
                game_over = True

        if write_values:
            save_high_scores(best_freeplay, best_ammo, best_timed)
            write_values = False

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == '__main__':
    asyncio.run(main())

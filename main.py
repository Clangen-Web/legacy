# pylint: disable=no-member
import sys
import os
import platform
import asyncio
from scripts.screens import *

import scripts.platformwrapper as web
import pygame

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('resources/icon.png'))

async def main():
# LOAD cats & clan

    web.eval("window.fs_loaded = false")

    web.init_idbfs()

    os.mkdir("/saves-legacy")

    web.eval("""
    FS.mount(window.IDBFS, {'root': '.'}, '/saves-legacy')
    FS.syncfs(true, (err) => {
        if (err) {console.log(err)}
        else {
            console.log('IndexedDB mounted and synced!')
            window.fs_loaded = true
        }
    })

    window.onbeforeunload = async ()=>{
        FS.syncfs(false, (err) => {console.log(err)})
    }
    """)

    
    while platform.window.fs_loaded is False: # pylint: disable=no-member
        print("Waiting for fs to load...")
        await asyncio.sleep(0.1)
            
    if platform.window.localStorage.getItem('hasMigratedLeg') == None: 
        print('migrating')
        for i in range(platform.window.localStorage.length): # pylint: disable=no-member
            key = platform.window.localStorage.key(i) # pylint: disable=no-member
            value = platform.window.localStorage.getItem(key) # pylint: disable=no-member
                
            if key in ['hasMigrated', '/', '__test__']:
                continue
            os.makedirs(os.path.dirname(f"/saves-legacy/{key}"), exist_ok=True)
            with open(f"/saves-legacy/{key}", "w") as f:
                f.write(value)
        platform.window.localStorage.setItem("hasMigratedLeg", "true") # pylint: disable=no-member

        web.pushdb()
        print("Migration complete!")

    if os.path.exists('/saves-legacy/clanlist.txt'):
        with open('/saves-legacy/clanlist.txt', 'r') as f:
            clan_list = f.read()
    else:
        clan_list = ''
    if_clans = len(clan_list)
    if if_clans > 0:
        game.switches['clan_list'] = clan_list.split('\n')
        cat_class.load_cats()
        clan_class.load_clan()
        cat_class.thoughts()
        #    if not game.switches['error_message']:
        #        game.switches[
        #            'error_message'] = 'There was an error loading the cats file!'

        try:
            game.map_info = load_map('' + game.clan.name)
        except NameError:
            game.map_info = {}
        except:
            game.map_info = load_map("Fallback")
            print("Default map loaded.")

# LOAD settings
    game.load_settings()

# reset brightness to allow for dark mode to not look crap
    verdana.change_text_brightness()
    buttons.change_button_brightness()
    sprites.load_scars()

    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])

    while True:
        if game.settings['dark mode']:
            screen.fill((40, 40, 40))
        else:
            screen.fill((255, 255, 255))

        if game.settings_changed:
            verdana.change_text_brightness()
            buttons.change_button_brightness()

        mouse.check_pos()

    # EVENTS
        for event in pygame.event.get():
            if game.current_screen == 'profile screen':
                previous_cat = 0
                next_cat = 0
                the_cat = cat_class.all_cats.get(game.switches['cat'],
                                                 game.clan.instructor)
                for check_cat in cat_class.all_cats:
                    if cat_class.all_cats[check_cat].ID == the_cat.ID:
                        next_cat = 1
                    if next_cat == 0 and cat_class.all_cats[
                            check_cat].ID != the_cat.ID and cat_class.all_cats[
                                check_cat].dead == the_cat.dead and cat_class.all_cats[
                                    check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                        check_cat].exiled:
                        previous_cat = cat_class.all_cats[check_cat].ID
                    elif next_cat == 1 and cat_class.all_cats[
                            check_cat].ID != the_cat.ID and cat_class.all_cats[
                                check_cat].dead == the_cat.dead and cat_class.all_cats[
                                    check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                        check_cat].exiled:
                        next_cat = cat_class.all_cats[check_cat].ID
                    elif int(next_cat) > 1:
                        break
                if next_cat == 1:
                    next_cat = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and previous_cat != 0:
                        game.switches['cat'] = previous_cat
                    if event.key == pygame.K_RIGHT and next_cat != 0:
                        game.switches['cat'] = next_cat
                    if event.key == pygame.K_0:
                        game.switches['cur_screen'] = 'list screen'
                    if event.key == pygame.K_1:
                        game.switches['cur_screen'] = 'options screen'
                        game.switches['last_screen'] = 'profile screen'
            if game.current_screen == 'make clan screen' and game.switches[
                    'clan_name'] == '' and event.type == pygame.KEYDOWN:
                if event.unicode.isalpha(
                ):  # only allows alphabet letters as an input
                    if len(
                            game.switches['naming_text']
                    ) < game.max_name_length:  # can't type more than max name length
                        game.switches['naming_text'] += event.unicode
                elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                    game.switches['naming_text'] = game.switches[
                        'naming_text'][:-1]

            if game.current_screen == 'events screen' and len(
                    game.cur_events_list) > game.max_events_displayed:
                max_scroll_direction = len(
                    game.cur_events_list) - game.max_events_displayed
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and game.event_scroll_ct < 0:
                        game.cur_events_list.insert(0, game.cur_events_list.pop())
                        game.event_scroll_ct += 1
                    if event.key == pygame.K_DOWN and abs(
                            game.event_scroll_ct) < max_scroll_direction:
                        game.cur_events_list.append(game.cur_events_list.pop(0))
                        game.event_scroll_ct -= 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4 and game.event_scroll_ct < 0:
                        game.cur_events_list.insert(0, game.cur_events_list.pop())
                        game.event_scroll_ct += 1
                    if event.button == 5 and abs(
                            game.event_scroll_ct) < max_scroll_direction:
                        game.cur_events_list.append(game.cur_events_list.pop(0))
                        game.event_scroll_ct -= 1

            if game.current_screen == 'allegiances screen' and len(
                    game.allegiance_list) > game.max_allegiance_displayed:
                max_scroll_direction = len(
                    game.allegiance_list) - game.max_allegiance_displayed
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and game.allegiance_scroll_ct < 0:
                        game.allegiance_list.insert(0, game.allegiance_list.pop())
                        game.allegiance_scroll_ct += 1
                    if event.key == pygame.K_DOWN and abs(
                            game.allegiance_scroll_ct) < max_scroll_direction:
                        game.allegiance_list.append(game.allegiance_list.pop(0))
                        game.allegiance_scroll_ct -= 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4 and game.allegiance_scroll_ct < 0:
                        game.allegiance_list.insert(0, game.allegiance_list.pop())
                        game.allegiance_scroll_ct += 1
                    if event.button == 5 and abs(
                            game.allegiance_scroll_ct) < max_scroll_direction:
                        game.allegiance_list.append(game.allegiance_list.pop(0))
                        game.allegiance_scroll_ct -= 1
            if game.current_screen == 'patrol screen':
                random_options = []
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_9:
                        for u in range(12):
                            i_max = len(game.patrol_cats)
                            if u < i_max:
                                game.switches['current_patrol'].append(
                                    game.patrol_cats[u])
            if game.current_screen == 'change name screen' and game.switches[
                    'change_name'] == '' and event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() or event.unicode.isspace(
                ):  # only allows alphabet letters/space as an input
                    if len(game.switches['naming_text']
                           ) < 20:  # can't type more than max name length
                        game.switches['naming_text'] += event.unicode
                elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                    game.switches['naming_text'] = game.switches[
                        'naming_text'][:-1]
            if game.current_screen == 'change gender screen' and game.switches[
                    'change_name'] == '' and event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() or event.unicode.isspace(
                ):  # only allows alphabet letters/space as an input
                    if len(game.switches['naming_text']
                           ) < 20:  # can't type more than max name length
                        game.switches['naming_text'] += event.unicode
                elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                    game.switches['naming_text'] = game.switches[
                        'naming_text'][:-1]
            if game.current_screen in [
                    'list screen', 'starclan screen', 'other screen', 'relationship screen'
            ] and event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() or event.unicode.isspace(
                ):  # only allows alphabet letters/space as an input
                    if len(game.switches['search_text']
                           ) < 20:  # can't type more than max name length
                        game.switches['search_text'] += event.unicode
                elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                    game.switches['search_text'] = game.switches[
                        'search_text'][:-1]

            if event.type == pygame.QUIT:
                # close pygame
                pygame.display.quit()
                pygame.quit()
                sys.exit()

        # MOUSE CLICK
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.clicked = True

            if event.type == pygame.KEYDOWN:
                game.keyspressed = []
                keys = pygame.key.get_pressed()
                if keys[pygame.K_0]:
                    game.keyspressed.append(0)
                if keys[pygame.K_1]:
                    game.keyspressed.append(1)
                if keys[pygame.K_2]:
                    game.keyspressed.append(2)
                if keys[pygame.K_3]:
                    game.keyspressed.append(3)
                if keys[pygame.K_4]:
                    game.keyspressed.append(4)
                if keys[pygame.K_5]:
                    game.keyspressed.append(5)
                if keys[pygame.K_6]:
                    game.keyspressed.append(6)
                if keys[pygame.K_7]:
                    game.keyspressed.append(7)
                if keys[pygame.K_8]:
                    game.keyspressed.append(8)
                if keys[pygame.K_9]:
                    game.keyspressed.append(9)
                if keys[pygame.K_KP0]:
                    game.keyspressed.append(10)
                if keys[pygame.K_KP1]:
                    game.keyspressed.append(11)
                if keys[pygame.K_KP2]:
                    game.keyspressed.append(12)
                if keys[pygame.K_KP3]:
                    game.keyspressed.append(13)
                if keys[pygame.K_KP4]:
                    game.keyspressed.append(14)
                if keys[pygame.K_KP5]:
                    game.keyspressed.append(15)
                if keys[pygame.K_KP6]:
                    game.keyspressed.append(16)
                if keys[pygame.K_KP7]:
                    game.keyspressed.append(17)
                if keys[pygame.K_KP8]:
                    game.keyspressed.append(18)
                if keys[pygame.K_KP9]:
                    game.keyspressed.append(19)
                if keys[pygame.K_UP]:
                    game.keyspressed.append(20)
                if keys[pygame.K_RIGHT]:
                    game.keyspressed.append(21)
                if keys[pygame.K_DOWN]:
                    game.keyspressed.append(22)
                if keys[pygame.K_LEFT]:
                    game.keyspressed.append(23)

    # SCREENS
        game.all_screens[game.current_screen].on_use()

    # update
        game.update_game()
        if game.switch_screens:
            screens.all_screens[game.current_screen].screen_switches()
            game.switch_screens = False
    # END FRAME
        clock.tick(30)

        pygame.display.update()
        await asyncio.sleep(0)

asyncio.run(main())
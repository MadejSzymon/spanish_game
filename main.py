from sys import exit
from os.path import exists
import math
import json
from datetime import datetime
import pandas as pd
import pygame
import pygame_gui
from constants.constants import *
from classes.Light import Light
from classes.Scoreboard import Scoreboard
from classes.Uit import Textbox
from classes.WordBase import WordBase
from classes.Timer import Timer
from classes.Text import Text
from classes.Button import Button
from classes.Slider import Slider
from classes.Select import Select
from classes.Enums import GameStates


def show_objects(objects_to_show):
    objects_to_hide = [item for item in gui_list if item not in objects_to_show]
    for i_object in objects_to_show:
        if hasattr(i_object, 'manager'):
            i_object.show()
            i_object.manager.update(UI_REFRESH_RATE)
            i_object.manager.draw_ui(screen)
        if i_object.__class__.__name__ == 'Text':
            i_object.draw_text(main_font, screen)
    for i_object in objects_to_hide:
        if hasattr(i_object, 'manager'):
            i_object.hide()


def update_lights(light_on_idx):
    for i, light in enumerate(lights):
        if i == light_on_idx:
            light.light_index = 1
        else:
            light.light_index = 0
        light.update(screen, LIGHT_POS[i])


def check_answer(user_answer_):
    correct_text.text = CORRECT_TEXT + word_base.current_osobe
    answer_correct = word_base.check_answer(user_answer_)
    if answer_correct:
        scoreboard.add_point(answer_correct)
        right_sound.play()
        if answer_correct == 0.5:
            iscorrect_bool = False
            comment_text.text = "Wrong accent!"
            comment_text.text_color = MEDIUM_COLOR
        else:
            iscorrect_bool = True
            comment_text.text = "Great!"
            comment_text.text_color = GOOD_COLOR
    else:
        iscorrect_bool = False
        scoreboard.lose_point()
        wrong_sound.play()
        comment_text.text = "Wrong!"
        comment_text.text_color = BAD_COLOR
    timer.reset_timer()
    scoreboard_text.text = f"Wynik: {scoreboard.score}/{scoreboard.overall}"
    word_input.clear()
    return iscorrect_bool


def check_if_late():
    too_late = timer.too_late
    if too_late:
        word_base.pick_rand_osobe()
        scoreboard.lose_point()
        wrong_sound.play()
        comment_text.text = "Too Late!"
        comment_text.text_color = BAD_COLOR


def save_score():
    try:
        perc = [scoreboard.score / scoreboard.overall * 100]
    except ZeroDivisionError:
        perc = 0
    new_score = pd.DataFrame(
        {'Nickname': [nickname],
         'Score': [scoreboard.score],
         'Questions_number': [scoreboard.overall],
         'Percentage': perc,
         'Date_time': [now]})
    lead_exists = exists(PATH_TO_LEAD)
    new_score.to_csv(PATH_TO_LEAD, mode='a', index=False, header=not lead_exists)


def reset_game():
    timer.reset_timer()
    comment_text.text = ''
    scoreboard.reset_score()
    word_base.reset_wordbase()
    word_input.focus()
    word_input.clear()
    word_base_text.text = word_base.current_word


def get_leaderboard():
    try:
        leaderboard = pd.read_csv(PATH_TO_LEAD)
    except FileNotFoundError:
        leaderboard = pd.DataFrame({'Nickname': [],
                                    'Score': [],
                                    'Questions_number': [],
                                    'Percentage': [],
                                    'Date_time': []})

    leaderboard = leaderboard.loc[leaderboard.groupby('Nickname')['Score'].idxmax()]
    leaderboard_str = ''
    leaderboard_val = leaderboard.values.tolist()
    for idx, val in enumerate(leaderboard_val):
        leaderboard_str = leaderboard_str + str(leaderboard.loc[leaderboard.index[idx], 'Nickname']) + \
                          '    ' + str(leaderboard.loc[leaderboard.index[idx], 'Score']) + \
                          '/' + str(leaderboard.loc[leaderboard.index[idx], 'Questions_number']) + \
                          '    ' + str(leaderboard.loc[leaderboard.index[idx], 'Percentage']) + '%' + '\n'
    return leaderboard_str


def set_volume(volume, sounds_to_change):
    for sound in sounds_to_change:
        sound.set_volume(volume)


def save_settings():
    settings_for_save = {'Time_for_answer': timer.word_limit,
                         'Sound_volume': vol_slider.get_current_value(),
                         'Accent_mode': str(accent_select.get_single_selection()),
                         'Displayed_language': str(lang_select.get_single_selection()),
                         'Show_answer': str(correct_answer_select.get_single_selection())}
    with open(PATH_TO_SETTINGS, 'w') as file:
        file.write(json.dumps(settings_for_save))
    file.close()


def reset_leaderboard():
    empty_score = pd.DataFrame(
        {'Nickname': [],
         'Score': [],
         'Questions_number': [],
         'Percentage': [],
         'Date_time': []})
    empty_score.to_csv(PATH_TO_LEAD, mode='w', index=False)
    leaderboard_str__ = get_leaderboard()
    leaderboard_text.text = leaderboard_str__


def get_settings():
    try:
        file = open(PATH_TO_SETTINGS)
        settings = json.load(file)
    except FileNotFoundError:
        settings = {'Accent_mode': DEFAULT_ACCENT,
                    'Time_for_answer': DEFAULT_TIME_ANSWER,
                    'Sound_volume': DEFAULT_VOLUME,
                    'Displayed_language': DEFAULT_LANG,
                    'Show_answer': DEFAULT_SHOW}
    return settings


def create_lights():
    lights_list = []
    for _ in range(LIGHTS_NUM):
        lights_list.append(Light(LIGHT_SIZE, PATH_TO_LIGHT_ON, PATH_TO_LIGHT_OFF))
    return lights_list


def map_mode(mode, options):
    for idx, _ in enumerate(options):
        if mode == options[idx]:
            return idx


# INITIALIZATION - GENERAL
pygame.init()
pygame.display.set_caption(GAME_TITLE)
try:
    icon = pygame.image.load(PATH_TO_ICON)
    pygame.display.set_icon(icon)
except FileNotFoundError:
    pass
game_state = GameStates.MENU
current_settings = get_settings()
leaderboard_str_ = get_leaderboard()
accent_mode = map_mode(current_settings['Accent_mode'], ACCENT_CHECKING_OPTIONS)
lang_mode = map_mode(current_settings['Displayed_language'], LANG_SELECT_OPTIONS)
answer_mode = current_settings['Show_answer']
click_sound = pygame.mixer.Sound('sound/click.wav')
right_sound = pygame.mixer.Sound('sound/right.wav')
wrong_sound = pygame.mixer.Sound('sound/wrong.wav')
sounds = [click_sound, right_sound, wrong_sound]
set_volume(current_settings['Sound_volume'] / 100, sounds)
try:
    main_font = pygame.font.Font(PATH_TO_MAIN_FONT, MAIN_FONT_SIZE)
except FileNotFoundError:
    main_font = pygame.font.SysFont(SUBST_FONT, MAIN_FONT_SIZE)
user_answer = ''
nickname = ''
iscorrect = True

# INITIALIZATION - CREATE OBJECTS
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SCREEN_SIZE)
timer = Timer(word_limit=current_settings['Time_for_answer'])
scoreboard = Scoreboard(limit=SCOREBOARD_LIMIT)
word_base = WordBase(path_to_base=PATH_TO_BASE, osobe_num=LIGHTS_NUM, mode=accent_mode, lang_mode=lang_mode)

# INITIALIZATION - CREATE GUI OBJECTS
manager = pygame_gui.UIManager(SCREEN_SIZE)
word_input = Textbox(object_id=WORD_INPUT_ID, manager=manager, pos=WORD_INPUT_POS, size=WORD_INPUT_SIZE)
game_button = Button(object_id=GAME_BUTTON_ID, manager=manager,
                     pos=GAME_BUTTON_POS, size=GAME_BUTTON_SIZE, text=GAME_BUTTON_TEXT)
lead_button = Button(object_id=LEAD_BUTTON_ID, manager=manager,
                     pos=LEAD_BUTTON_POS, size=LEAD_BUTTON_SIZE, text=LEAD_BUTTON_TEXT)
settings_button = Button(object_id=SETTINGS_BUTTON_ID, manager=manager,
                         pos=SETTINGS_BUTTON_POS, size=SETTINGS_BUTTON_SIZE, text=SETTINGS_BUTTON_TEXT)
clear_lead_button = Button(object_id=CLEAR_LEAD_BUTTON_ID, manager=manager,
                           pos=CLEAR_LEAD_BUTTON_POS, size=CLEAR_LEAD_BUTTON_SIZE, text=CLEAR_LEAD_BUTTON_TEXT)
time_slider = Slider(object_id=TIME_SLIDER_ID, manager=manager,
                     pos=TIME_SLIDER_POS, size=TIME_SLIDER_SIZE,
                     start_value=current_settings['Time_for_answer'], value_range=TIME_SLIDER_RANGE)
vol_slider = Slider(object_id=VOL_SLIDER_ID, manager=manager,
                    pos=VOL_SLIDER_POS, size=VOL_SLIDER_SIZE,
                    start_value=current_settings['Sound_volume'], value_range=VOL_SLIDER_RANGE)
lead_textbox = Textbox(object_id=LEAD_TEXTBOX_ID, manager=manager, pos=LEAD_TEXTBOX_POS, size=LEAD_TEXTBOX_SIZE)
word_base_text = Text(text_color=NORMAL_COLOR, text_pos=WORD_POS, text=word_base.current_word)
timer_text = Text(text_color=NORMAL_COLOR, text_pos=TIMER_POS, text=str(math.floor(timer.time_left) + 1))
scoreboard_text = Text(text_color=NORMAL_COLOR, text_pos=SCOREBOARD_POS,
                       text=f"Wynik: {scoreboard.score}/{scoreboard.overall}")
comment_text = Text(text_color=GOOD_COLOR, text_pos=COMMENT_POS, text='')
exit_hint = Text(text_color=NORMAL_COLOR, text_pos=EXIT_HINT_POS, text=EXIT_HINT_TEXT)
leaderboards_hint = Text(text_color=NORMAL_COLOR, text_pos=LEAD_HINT_POS, text=LEAD_HINT_TEXT)
leaderboard_text = Text(text_color=NORMAL_COLOR, text_pos=LEAD_TXT_POS, text=leaderboard_str_)
time_slider_text = Text(text_color=NORMAL_COLOR,
                        text_pos=TIME_SLIDER_TEXT_POS, text=TIME_SLIDER_TEXT + str(time_slider.get_current_value()))
vol_slider_text = Text(text_color=NORMAL_COLOR,
                       text_pos=VOL_SLIDER_TEXT_POS, text=VOL_SLIDER_TEXT + str(vol_slider.get_current_value()))
accent_text = Text(text_color=NORMAL_COLOR,
                   text_pos=ACCENT_TEXT_POS, text=ACCENT_TEXT)
lang_text = Text(text_color=NORMAL_COLOR,
                 text_pos=LANG_TEXT_POS, text=LANG_TEXT)
correct_text = Text(text_color=NORMAL_COLOR,
                    text_pos=CORRECT_TEXT_POS, text=CORRECT_TEXT)
correct_answer_setting_text = Text(text_color=NORMAL_COLOR,
                                   text_pos=CORRECT_SETTING_TEXT_POS, text=CORRECT_SETTING_TEXT)
accent_select = Select(object_id=ACCENT_SELECT_ID, manager=manager,
                       pos=ACCENT_SELECT_POS, size=ACCENT_SELECT_SIZE,
                       item_list=ACCENT_CHECKING_OPTIONS,
                       default_selection=current_settings['Accent_mode'])
lang_select = Select(object_id=LANG_SELECT_ID, manager=manager,
                     pos=LANG_SELECT_POS, size=LANG_SELECT_SIZE,
                     item_list=LANG_SELECT_OPTIONS,
                     default_selection=current_settings['Displayed_language'])
correct_answer_select = Select(object_id=CORRECT_SELECT_ID, manager=manager,
                               pos=CORRECT_SELECT_POS, size=CORRECT_SELECT_SIZE,
                               item_list=CORRECT_SELECT_OPTIONS,
                               default_selection=current_settings['Show_answer'])
lights = create_lights()
gui_list = [word_input, game_button, lead_button, settings_button, clear_lead_button,
            time_slider, vol_slider, lead_textbox, timer_text, scoreboard_text, correct_answer_setting_text,
            comment_text, exit_hint, leaderboards_hint, leaderboard_text,
            time_slider_text, vol_slider_text, accent_text, accent_select,
            lang_text, lang_select, correct_answer_select, correct_text]

# MAIN LOOP
while True:
    UI_REFRESH_RATE = clock.tick(FRAMES_PER_SECOND) / 1000
    screen.fill(BACKGROUND_COLOR)
    # EXIT GAME
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_settings()
            pygame.quit()
            exit()

        match game_state:
            case GameStates.MENU:
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == GAME_BUTTON_ID:
                    click_sound.play()
                    game_state = GameStates.GAME_ON
                    reset_game()
                game_button.manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == LEAD_BUTTON_ID:
                    click_sound.play()
                    game_state = GameStates.SHOW_LEADERBOARDS
                lead_button.manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == SETTINGS_BUTTON_ID:
                    click_sound.play()
                    game_state = GameStates.SETTINGS
                settings_button.manager.process_events(event)
            case GameStates.GAME_ON:
                if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_object_id == WORD_INPUT_ID:
                    user_answer = event.text
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        iscorrect = check_answer(user_answer)
                        word_base_text.text = word_base.current_word
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameStates.TYPE_LEADERBOARDS
                word_input.manager.process_events(event)
            case GameStates.TYPE_LEADERBOARDS:
                if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_object_id == LEAD_TEXTBOX_ID:
                    nickname = event.text
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        save_score()
                        lead_textbox.clear()
                        leaderboard_str_ = get_leaderboard()
                        leaderboard_text.text = leaderboard_str_
                        game_state = GameStates.MENU
                lead_textbox.manager.process_events(event)
            case GameStates.SHOW_LEADERBOARDS:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameStates.MENU
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == CLEAR_LEAD_BUTTON_ID:
                    reset_leaderboard()
                clear_lead_button.manager.process_events(event)
            case GameStates.SETTINGS:
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and event.ui_object_id == TIME_SLIDER_ID:
                    timer.word_limit = time_slider.get_current_value()
                    time_slider_text.text = TIME_SLIDER_TEXT + str(timer.word_limit)
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and event.ui_object_id == VOL_SLIDER_ID:
                    vol_slider_text.text = VOL_SLIDER_TEXT + str(round(vol_slider.get_current_value()))
                    set_volume(round(vol_slider.get_current_value()) / 100, sounds)
                if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_object_id == ACCENT_SELECT_ID:
                        word_base.mode = map_mode(accent_select.get_single_selection(), ACCENT_CHECKING_OPTIONS)
                    if event.ui_object_id == LANG_SELECT_ID:
                        word_base.change_lang_mode(map_mode(lang_select.get_single_selection(), LANG_SELECT_OPTIONS))
                    if event.ui_object_id == CORRECT_SELECT_ID:
                        answer_mode = str(correct_answer_select.get_single_selection())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameStates.MENU
                time_slider.manager.process_events(event)
                vol_slider.manager.process_events(event)
                accent_select.manager.process_events(event)

    match game_state:
        case GameStates.MENU:
            show_objects([game_button, lead_button, settings_button])
        case GameStates.GAME_ON:
            timer.count_time()
            timer_text.text = str(math.floor(timer.time_left) + 1)
            check_if_late()
            update_lights(word_base.current_osobe_idx - 2)
            if not iscorrect and answer_mode == 'YES':
                show_objects([word_input, word_base_text, scoreboard_text,
                              comment_text, exit_hint, timer_text, correct_text])
            else:
                show_objects([word_input, word_base_text, scoreboard_text, comment_text, exit_hint, timer_text])
        case GameStates.TYPE_LEADERBOARDS:
            lead_textbox.focus()
            show_objects([lead_textbox, leaderboards_hint])
        case GameStates.SHOW_LEADERBOARDS:
            show_objects([leaderboard_text, exit_hint, clear_lead_button])
        case GameStates.SETTINGS:
            show_objects([time_slider, vol_slider,
                          accent_select, accent_text, exit_hint, vol_slider_text, correct_answer_select,
                          time_slider_text, lang_text, lang_select, correct_answer_setting_text])
    pygame.display.update()

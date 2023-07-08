import pandas as pd
from unidecode import unidecode
import random


class WordBase:

    def __init__(self, osobe_num, mode, path_to_base, lang_mode):
        self.words = pd.read_csv(path_to_base, encoding='latin-1')
        for column in self.words.columns.tolist():
            if column == 'w_bazie':
                pass
            else:
                self.words[column] = self.words[column].astype(str).str.replace(" ", "")
        self.words = self.words[self.words['w_bazie'] == 1]
        self.words = self.words.drop('w_bazie', axis=1)
        self.polish_bezokol = self.words['pol_tlumaczenie'].values.tolist()
        self.spanish_bezokol = self.words['hiszp_bezokol'].values.tolist()
        if lang_mode == 0:
            self.words_bezokol = self.polish_bezokol
        if lang_mode == 1:
            self.words_bezokol = self.spanish_bezokol
        self.current_word_idx = 0
        self.current_osobe_idx = 0
        self.picked_words_idx = []
        self.picked_osobe_idx = []
        self.current_word = None
        self.current_osobe = None
        self.current_time = 0
        self.start_time = 0
        self.osobe_num = osobe_num
        self.mode = mode

    def pick_rand_word(self):
        if len(self.picked_words_idx) == len(self.words_bezokol):
            self.picked_words_idx = []
        while True:
            self.current_word_idx = random.randint(0, len(self.words_bezokol) - 1)
            if self.current_word_idx not in self.picked_words_idx:
                self.current_word = self.words_bezokol[self.current_word_idx]
                self.picked_words_idx.append(self.current_word_idx)
                break

    def pick_rand_osobe(self):
        if len(self.picked_osobe_idx) == self.osobe_num:
            self.picked_osobe_idx = []
        while True:
            self.current_osobe_idx = random.randint(2, 7)
            if self.current_osobe_idx not in self.picked_osobe_idx:
                self.current_osobe = self.words.iloc[self.current_word_idx, self.current_osobe_idx]
                self.picked_osobe_idx.append(self.current_osobe_idx)
                break

    def check_answer(self, answer):
        no_accents = unidecode(self.current_osobe)
        result = 0
        match self.mode:
            case 0:
                if answer == no_accents:
                    result = 1
            case 1:
                if answer == self.current_osobe:
                    result = 1
                elif answer == no_accents:
                    result = 0.5
            case 2:
                if answer == self.current_osobe:
                    result = 1
        if len(self.picked_osobe_idx) == self.osobe_num:
            self.pick_rand_word()
        self.pick_rand_osobe()
        return result

    def change_lang_mode(self, lang_mode):
        if lang_mode == 0:
            self.words_bezokol = self.polish_bezokol
        elif lang_mode == 1:
            self.words_bezokol = self.spanish_bezokol
        self.reset_wordbase()

    def reset_wordbase(self):
        self.picked_words_idx = []
        self.picked_osobe_idx = []
        self.pick_rand_word()
        self.pick_rand_osobe()

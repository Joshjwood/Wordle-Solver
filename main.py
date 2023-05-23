import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import os
import json
from functions import *
from random import randint




class Wordle_Round:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.five_letter_words = []
        self.flw_no_dupe_letters = []
        self.active_word_list = []

        self.absent_letters = []


        #Clear the initial popup

    def setup(self):
        self.driver.get("https://wordlegame.org/")
        for i in range(0, 2):
            print(f"Waiting for {2 - i}...")
            time.sleep(1)


    def choose_first_word(self):
        #load words
        with open('words.json', 'r') as fd:
            wlist = json.load(fd)

        # Get word list
        self.five_letter_words = wlist

        # Filter word list for words with duplicate letters for the first guess
        # as this wastes potential guess letters
        filtered_words = filter_for_duplicate_letters(self.five_letter_words)
        self.flw_no_dupe_letters = filtered_words

        #Get a list of the top 5 most common letters in our list of words
        excluded_letters = []
        letter_frequency = GetLetterFrequency_v2(wlist)
        top_five = []
        for i in range(0, 5):
            top_five.append(letter_frequency[i][0])

        # ChatGPT wrote this
        # Find the words which contain the most letters from the list of the most common letters
        words_with_count = []
        for word in filtered_words:
            count = sum(word.count(letter) for letter in top_five)
            words_with_count.append((word, count))
        words_with_count.sort(key=lambda x: x[1], reverse=True)
        top_words = [word for word, _ in words_with_count[:1000]]
        #top_10_words = [word for word, _ in words_with_count[:10]]


        #print(top_10_words)
        return top_words[randint(0, len(top_words))]

    def choose_word_stage_2(self):
        # excluded_letters = self.absent_letters
        letter_frequency = GetLetterFrequency_v2(self.active_word_list)
        top_five = []
        print(f"Letter Freq = {letter_frequency}")
        for i in range(0, 5):
            top_five.append(letter_frequency[i][0])
        print(top_five)

        filtered_words = filter_for_duplicate_letters(self.active_word_list)

        # ChatGPT wrote this
        # Find the words which contain the most letters from the list of the most common letters
        words_with_count = []
        for word in filtered_words:
            count = sum(word.count(letter) for letter in top_five)
            words_with_count.append((word, count))
        words_with_count.sort(key=lambda x: x[1], reverse=True)
        top_10_words = [word for word, _ in words_with_count[:10]]
        return top_10_words[randint(0, 9)]

    def choose_word_stage_3(self):
        letter_frequency = GetLetterFrequency_v2(self.active_word_list)
        top_five = []
        print(f"Letter Freq = {letter_frequency}")
        top_x = 5
        if len(letter_frequency) < top_x:
            top_x = len(letter_frequency)

        for i in range(0, top_x):
            top_five.append(letter_frequency[i][0])
        print(top_five)
        words_with_count = []
        for word in self.active_word_list:
            count = sum(word.count(letter) for letter in top_five)
            words_with_count.append((word, count))
        words_with_count.sort(key=lambda x: x[1], reverse=True)
        top_10_words = [word for word, _ in words_with_count[:10]]
        return top_10_words[randint(0, 9)]




    def enter_word(self, word):
        letter_keys = self.driver.find_elements(By.CLASS_NAME, 'Game-keyboard-button')

        for letter in word:
            for i in letter_keys:
                if str(i.text.lower()) == letter.lower():
                    i.click()
                    time.sleep(1)

        for i in letter_keys:
            if i.text == "Enter":
                i.click()

        time.sleep(2)

    def filter_negative_matches(self):
        all_locked_rows = self.driver.find_elements(By.CLASS_NAME, "Row-locked-in")

        all_letters = all_locked_rows[-1].find_elements(By.CLASS_NAME, "Row-letter")

        for i in all_letters:
            if i.get_attribute("class").split(" ")[1] == "letter-absent":
                self.absent_letters.append(i.text)
            print(f"{i.text} - {i.get_attribute('class')}")

        print(self.absent_letters)
        new_filtered_wordlist = []

        for word in self.five_letter_words:
            if not any(letter in word for letter in self.absent_letters):
                new_filtered_wordlist.append(word)


        print(len(new_filtered_wordlist))
        print(len(self.five_letter_words))
        print(new_filtered_wordlist)

        self.active_word_list = new_filtered_wordlist

        time.sleep(2)
        return


Wordle_Round = Wordle_Round()
#
Wordle_Round.setup()


chosen_word = Wordle_Round.choose_first_word()
print(chosen_word)
Wordle_Round.enter_word(chosen_word)
Wordle_Round.filter_negative_matches()

second_word = Wordle_Round.choose_word_stage_2()
print(second_word)
Wordle_Round.enter_word(second_word)
Wordle_Round.filter_negative_matches()

third_word = Wordle_Round.choose_word_stage_2()
print(third_word)
Wordle_Round.enter_word(third_word)
Wordle_Round.filter_negative_matches()

for round in range(0, 3):
    try:
        word = Wordle_Round.choose_word_stage_3()
    except:
        time.sleep(30000)
    print(word)
    Wordle_Round.enter_word(word)
    Wordle_Round.filter_negative_matches()

time.sleep(20000)

# Next task is to identify letters that are highlighted as relevant and non-relevant
# Will need to find a way to get a new list of words that have letters that ARE or ARENT in the indicated places
# Exclude all words with letters that are now greyed out
# def Filter_words_for_greyed_letters









# Website used, for reference - https://eslforums.com/5-letter-words/
# Get5LetterWords("https://github.com/tabatkins/wordle-list/blob/main/words")
# letter_frequency = GetLetterFrequency()
# print(letter_frequency)




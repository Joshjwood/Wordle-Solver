import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import json
from functions import *
from random import randint


class Wordle_Round:
    def __init__(self, name):
        self.name = name
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        self.five_letter_words = []
        self.flw_no_dupe_letters = []
        self.active_word_list = []

        self.tested_letters = []

        self.absent_letters = []
        self.present_letters = []
        self.correct_letters = ["", "", "", "", ""]

        # Clear the initial popup

    def setup(self):
        self.driver.get("https://wordlegame.org/")
        for i in range(0, 2):
            print(f"Waiting for {2 - i}...")
            time.sleep(1)
        # load words
        # Get word list
        with open('words.json', 'r') as fd:
             self.five_letter_words = json.load(fd)
        self.active_word_list = self.five_letter_words
        print(f"Length of word list: {len(self.five_letter_words)}")

    def choose_first_word(self):
        # Filter word list for words with duplicate letters for the first guess
        # as this wastes potential guess letters
        filtered_words = filter_for_duplicate_letters(self.five_letter_words)
        self.flw_no_dupe_letters = filtered_words

        # Get a list of the top 5 most common letters in our list of words
        excluded_letters = []
        letter_frequency = GetLetterFrequency_v2(self.five_letter_words)
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
        top_words = [word for word, _ in words_with_count[:100]]
        # top_10_words = [word for word, _ in words_with_count[:10]]
        # print(top_10_words)
        word_submission = top_words[randint(0, len(top_words))]
        self.tested_letters = [i for i in word_submission]
        print(f"Tested letters: {self.tested_letters}")
        return word_submission


    def choose_word_stage_2(self):
        #print(self.active_word_list)
        #print(f"Length of word list by the start of STAGE 2: {len(self.active_word_list)}")
        # excluded_letters = self.absent_letters
        letter_frequency = GetLetterFrequency_v2(self.active_word_list)
        top_fifteen = []
        # print(f"Letter Freq = {letter_frequency}")
        for i in range(0, 15):
            if letter_frequency[i][0] in self.tested_letters:
                continue
            else:
                top_fifteen.append(letter_frequency[i][0])
        print(f"Top {len(top_fifteen)} common letters in word-list: {top_fifteen}")

        filtered_words = filter_for_duplicate_letters(self.active_word_list)

        # ChatGPT wrote this
        # Find the words which contain the most letters from the list of the most common letters
        words_with_count = []
        for word in filtered_words:
            count = sum(word.count(letter) for letter in top_fifteen)
            words_with_count.append((word, count))
        words_with_count.sort(key=lambda x: x[1], reverse=True)
        top_10_words = [word for word, _ in words_with_count[:10]]
        word_submission = top_10_words[randint(0, 9)]
        for i in word_submission:
            self.tested_letters.append(i)
        return word_submission

    def choose_word_stage_3(self):
        all_locked_rows = self.driver.find_elements(By.CLASS_NAME, "Row-locked-in")
        print(f"Number of Locked Rows: {len(all_locked_rows)}")
        previous_word_letters = all_locked_rows[-1].find_elements(By.CLASS_NAME, "Row-letter")

        print(f"Length of word list: {len(self.active_word_list)} ||| Word list = {self.active_word_list}")
        letter_frequency = GetLetterFrequency_v2(self.active_word_list)
        top_five = []
        top_x = 5
        if len(letter_frequency) < top_x:
            top_x = len(letter_frequency)

        if self.correct_letters != ["", "", "", "", ""]:

            filtered_by_correct_letters = []
            for word in self.active_word_list:
                # print(word)
                for i in range(0, 5):
                    if word[i] == self.correct_letters[i]:
                        filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        good = False

        while not good:
            word_submission = max(set(self.active_word_list), key=self.active_word_list.count)
            word_list = []
            for i in self.active_word_list:
                if i == word_submission:
                    continue
                else:
                    word_list.append(i)
            self.active_word_list = word_list
            present_letters = []
            for i in self.present_letters:
                if i.isalpha():
                    present_letters.append(i)
            #print(f"Considering submission... {word_submission}")
            good = all(letter in word_submission for letter in present_letters)

        word_list = []
        for i in self.active_word_list:
            if i == word_submission:
                continue
            else:
                word_list.append(i)
        self.active_word_list = word_list

        return word_submission

    def CheckIfGameOver(self):
        all_locked_rows = self.driver.find_elements(By.CLASS_NAME, "Row-locked-in")
        previous_word_letters = all_locked_rows[-1].find_elements(By.CLASS_NAME, "Row-letter")
        finish_state = "INIT"
        # Check if it's over and we lost
        if len(all_locked_rows) >= 6:
            won = True
            for i in previous_word_letters:
                if i.get_attribute("class").split(" ")[1] != "letter-correct":
                    won = False
                    #print("not letter-correct")
                else:
                    #print("letter-correct")
                    continue
            if won == True:
                print("Won on the last turn.")
                finish_state = "SUCCESS"

            if won == False:
                print("Used all turns and failed")
                finish_state = "FAIL"

        # Check if it's over and we won
        complete = True
        for i in previous_word_letters:
            if i.get_attribute("class").split(" ")[1] != "letter-correct":
                complete = False
            else:
                continue
        if complete == True:
            print("THIS IS SUCCESS EXIT")
            finish_state = "SUCCESS"
        return finish_state

    def enter_word(self, word):
        letter_keys = self.driver.find_elements(By.CLASS_NAME, 'Game-keyboard-button')

        for letter in word:
            for i in letter_keys:
                if str(i.text.lower()) == letter.lower():
                    i.click()
                    time.sleep(0.2)

        for i in letter_keys:
            if i.text == "Enter":
                i.click()

        time.sleep(1.5)

    def negative_and_positive_matches(self):
        all_locked_rows = self.driver.find_elements(By.CLASS_NAME, "Row-locked-in")
        previous_word_letters = all_locked_rows[-1].find_elements(By.CLASS_NAME, "Row-letter")

        for i in previous_word_letters:

            if i.get_attribute("class").split(" ")[1] == "letter-absent":
                self.absent_letters.append(i.text)
            elif i.get_attribute("class").split(" ")[1] == "letter-correct" or "letter_elsewhere":
                self.present_letters.append(i.text)
                self.present_letters = list(set(self.present_letters))
            # except:
            #     print(i.get_attribute("class").split(" "))



        # If you submit a word with duplicate letters, and the correct answer only has it once
        # the letter will be added to both of the above lists
        # So we must compare the lists and remove offending items from 'absent_letters'
        new_absent = []
        for letter in self.absent_letters:
            if letter in self.present_letters:
                continue
            else:
                new_absent.append(letter)
        self.absent_letters = new_absent

        print(f"Incorrect letters: {self.absent_letters}")
        print(f"Present letters: {self.present_letters}")

        # remove words with absent letters
        new_filtered_wordlist = []
        for word in self.active_word_list:
            if not any(letter in word for letter in self.absent_letters):
                new_filtered_wordlist.append(word)
        self.active_word_list = new_filtered_wordlist
        # remove words without present letters
        if len(self.present_letters) >= 3:
            new_filtered_wordlist = []
            for word in self.active_word_list:
                if any(letter in word for letter in self.present_letters):
                    new_filtered_wordlist.append(word)
            self.active_word_list = new_filtered_wordlist
        time.sleep(2)
        return

    def identify_correct_letters(self):
        all_locked_rows = self.driver.find_elements(By.CLASS_NAME, "Row-locked-in")
        previous_word_letters = all_locked_rows[-1].find_elements(By.CLASS_NAME, "Row-letter")

        for i in range(0, len(previous_word_letters)):
            if previous_word_letters[i].get_attribute("class").split(" ")[1] == "letter-correct":
                self.correct_letters[i] = previous_word_letters[i].text
        print(f"Known letters: {self.correct_letters}")

    def NextGame(self):
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE)

count = 0
while True:
    # Establish game
    WordleRound = Wordle_Round(f"Round {count}.")
    WordleRound.setup()

    # Initial submission
    chosen_word = WordleRound.choose_first_word()
    WordleRound.enter_word(chosen_word)
    WordleRound.negative_and_positive_matches()
    WordleRound.identify_correct_letters()

    # Two further exploratory submissions
    for round in range(0, 2):
        word = WordleRound.choose_word_stage_2()
        WordleRound.enter_word(word)
        WordleRound.negative_and_positive_matches()
        WordleRound.identify_correct_letters()

    # Guessing in earnest x 3
    count = 3
    for round in range(0, 4):
        count += 1
        try:
            word = WordleRound.choose_word_stage_3()
            WordleRound.enter_word(word)
            finish_state = WordleRound.CheckIfGameOver()

            if finish_state == "SUCCESS":
                print(f"Success! The last word was {word}.")
                with open("results.txt", 'a') as file:
                    file.write(word + f" | {count}th guess | {finish_state}\n")
                break
            elif finish_state == "INIT":
                print("Game continuing")
            elif finish_state == "FAIL":
                print("Game over. FAIL")
                with open("results.txt", 'a') as file:
                    file.write(word + f" | {count}th guess | {finish_state}\n")
                break

            WordleRound.negative_and_positive_matches()
            WordleRound.identify_correct_letters()
        except:
            print(f"You either broke it or you won. The last word was {word}.")
            with open("results.txt", 'a') as file:
                file.write(word + f" | {count}th guess | {finish_state}\n")
            break
    time.sleep(3)
    WordleRound.NextGame()
    del WordleRound

# Next task is to identify letters that are highlighted as relevant and non-relevant
# Will need to find a way to get a new list of words that have letters that ARE or ARENT in the indicated places
# Exclude all words with letters that are now greyed out
# def Filter_words_for_greyed_letters


# Website used, for reference - https://eslforums.com/5-letter-words/
# Get5LetterWords("https://github.com/tabatkins/wordle-list/blob/main/words")
# letter_frequency = GetLetterFrequency()
# print(letter_frequency)

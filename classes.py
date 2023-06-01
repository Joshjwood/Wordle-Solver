
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
import os
import json
from functions import *
from random import randint




class Wordle_Round:
    def __init__(self, name):
        self.name = name

        options = webdriver.ChromeOptions()
        #options.add_argument('headless')
        '''
        This will minimize and raise to monitor above, remove below two lines for default settings
        Enable line above for headless mode
        '''
        options.add_argument("--window-position=220,-1150")
        options.add_argument("--window-size=200,700")

        self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

        self.five_letter_words = []
        self.flw_no_dupe_letters = []
        self.active_word_list = []

        self.tested_letters = []

        self.absent_letters = []
        self.present_letters = []
        self.correct_letters = ["", "", "", "", ""]

        # Incorrect letter positioning - i'm sure there was a better way to format this rather than using
        # multiple lists. Hopefully I can come back to this with better structuring knowledge and update.
        self.first_letter_not = []
        self.second_letter_not = []
        self.third_letter_not = []
        self.fourth_letter_not = []
        self.fifth_letter_not = []


    def setup(self):
        self.driver.get("https://wordlegame.org/")
        wait_for = 5
        for i in range(0, wait_for):
            print(f"Waiting for {wait_for - i}...")
            time.sleep(1)
        # load words
        # Get word list
        with open('words.json', 'r') as fd:
             self.five_letter_words = json.load(fd)
        self.active_word_list = self.five_letter_words

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

        # ChatGPT wrote parts of this, the sorting with key=lambda is currently outside my understanding.
        # Find the words which contain the most letters from the list of the most common letters.
        words_with_count = []
        for word in filtered_words:
            count = sum(word.count(letter) for letter in top_five)
            words_with_count.append((word, count))
        words_with_count.sort(key=lambda x: x[1], reverse=True)
        top_words = [word for word, _ in words_with_count[:100]]
        #word_submission = top_words[randint(0, len(top_words))]

        try:
            word_submission = top_words[randint(0, len(top_words) - 1)]
        except:
            print("Exception at word_submission, printing top 10 word list.")
            print(top_words)
            time.sleep(10000)

        self.tested_letters = [i for i in word_submission]
        return word_submission


    def choose_word_stage_2(self):
        letter_frequency = GetLetterFrequency_v2(self.active_word_list)
        top_fifteen = []
        for i in range(0, len(letter_frequency)):
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
        top_10_words = [word for word, _ in words_with_count[:100]]
        try:
            word_submission = top_10_words[randint(0, len(top_10_words) - 1)]
        except:
            print("Exception at word_submission, printing top 10 word list.")
            print(top_10_words)
            time.sleep(10000)
        for i in word_submission:
            self.tested_letters.append(i)
        return word_submission

    def choose_word_stage_3(self):
        # If we know some of the letters, filter by them
        # This will create duplicate words in the list, if they have more than one of the letters, useful below.
        if self.correct_letters != ["", "", "", "", ""]:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                # print(word)
                for i in range(0, 5):
                    if word[i] == self.correct_letters[i]:
                        filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        # Filter by FIRST letter
        if self.first_letter_not != False:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                if word[0] in self.first_letter_not:
                    continue
                else:
                    filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        # Filter by SECOND letter
        if self.second_letter_not != False:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                if word[1] in self.second_letter_not:
                    continue
                else:
                    filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        # Filter by THIRD letter
        if self.third_letter_not != False:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                if word[2] in self.third_letter_not:
                    continue
                else:
                    filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        # Filter by FOURTH letter
        if self.fourth_letter_not != False:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                if word[3] in self.fourth_letter_not:
                    continue
                else:
                    filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        # Filter by FIFTH letter
        if self.fifth_letter_not != False:
            filtered_by_correct_letters = []
            for word in self.active_word_list:
                if word[4] in self.fifth_letter_not:
                    continue
                else:
                    filtered_by_correct_letters.append(word)
            self.active_word_list = filtered_by_correct_letters

        '''
        The following loop suggests a word based on the frequency it appears in our active word list. 
        The highest frequency word is suggested first, compared to the confirmed present letters, then used or discarded.
        '''
        good = False
        while not good:
            word_submission = max(set(self.active_word_list), key=self.active_word_list.count)
            word_list = []
            '''
            this part removes the currently proposed word from the active word list, so that whether
            it's discarded or used, it's not suggested again.
            '''
            for i in self.active_word_list:
                if i == word_submission:
                    continue
                else:
                    word_list.append(i)
            self.active_word_list = word_list
            '''
            Pulls in the letters that are green or yellow then checks it's not reading a blank.
            '''
            present_letters = []
            for i in self.present_letters:
                if i.isalpha():
                    present_letters.append(i)
            '''
            The main event. Returns true when all the confirmed green or yellow letters appear in the suggested word.
            Breaking the loop and allowing that word to be submitted.
            '''
            good = all(letter in word_submission for letter in present_letters)

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
                else:
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

        for i in range(0, len(previous_word_letters)):

            if previous_word_letters[i].get_attribute("class").split(" ")[1] == "letter-absent":
                self.absent_letters.append(previous_word_letters[i].text)
            elif previous_word_letters[i].get_attribute("class").split(" ")[1] == "letter-correct" or "letter-elsewhere":
                self.present_letters.append(previous_word_letters[i].text)
                self.present_letters = list(set(self.present_letters))

            # Identify correct letters in the wrong position and record them.
            # I'm certain there's a more graceful way to handle this. Probably a dictionary instead of 5 variables.
            if previous_word_letters[i].get_attribute("class").split(" ")[1] == "letter-elsewhere":
                if i == 0:
                    self.first_letter_not.append(previous_word_letters[i].text)
                if i == 1:
                    self.second_letter_not.append(previous_word_letters[i].text)
                if i == 2:
                    self.third_letter_not.append(previous_word_letters[i].text)
                if i == 3:
                    self.fourth_letter_not.append(previous_word_letters[i].text)
                if i == 4:
                    self.fifth_letter_not.append(previous_word_letters[i].text)

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

        '''
        Identifies the letters which are green (correct) and stores them in a class variable.
        '''
        for i in range(0, len(previous_word_letters)):
            if previous_word_letters[i].get_attribute("class").split(" ")[1] == "letter-correct":
                self.correct_letters[i] = previous_word_letters[i].text
        print(f"Known correct letters: {self.correct_letters}")

    def NextGame(self):
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE)
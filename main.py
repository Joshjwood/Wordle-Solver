import sys
import time
import os
import json
from classes import *





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
        print("---------------------------------------------")
        word = WordleRound.choose_word_stage_2()
        WordleRound.enter_word(word)
        WordleRound.negative_and_positive_matches()
        WordleRound.identify_correct_letters()


    # Guessing in earnest x 3
    count = 3
    for round in range(0, 3):
        print("---------------------------------------------")
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
            print(f"You won. The last word was {word}.")
            with open("results.txt", 'a') as file:
                file.write(word + f" | {count}th guess | {finish_state}\n")
            break
    time.sleep(3)
    WordleRound.NextGame()
    del WordleRound

# Get5LetterWords("https://github.com/tabatkins/wordle-list/blob/main/words")

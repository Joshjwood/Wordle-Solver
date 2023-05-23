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
import string

def Get5LetterWords(web_address):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(web_address)
    list = driver.find_element(By.XPATH, "/html/body").text.split("\n")
    list = [i.upper() for i in list]
    five_letter_words = []
    for i in list:
        if len(i) == 5:
            if i.upper() in five_letter_words:
                continue
            else:
                five_letter_words.append(i.upper())
    with open('words.json', 'w') as fd:
        json.dump(five_letter_words, fd)
        print("json dumped")

def GetLetterFrequency(excluded_letters):
    with open('words.json', 'r') as fd:
        wlist = json.load(fd)
    alphabet = list(string.ascii_uppercase)
    freq = {}
    for i in wlist:
        for item in i:
            if (item in freq):
                freq[item] += 1
            else:
                freq[item] = 1

    sorted_freq = sorted(freq.items(), key=lambda x: x[1])
    print("below is sorted freq")
    print(sorted_freq)

    # This slice is taking the 10 most commonly used of the 26 letters
    # in the alphabet and returning them in descending order.
    return sorted_freq[26:15:-1]

def GetLetterFrequency_v2(wlist):
    freq = {}
    for i in wlist:
        for item in i:
            if (item in freq):
                freq[item] += 1
            else:
                freq[item] = 1
    sorted_freq = sorted(freq.items(), key=lambda x: x[1])

    # This slice is taking the 10 most commonly used of the 26 letters
    # in the alphabet and returning them in descending order.
    return sorted_freq[26:0:-1]

#Chat GPT wrote the two functions below
def has_duplicates(word):
    """
    Checks if a word contains duplicates of the same letter.
    Returns True if duplicates are found, False otherwise.
    """
    char_count = {}
    for char in word:
        if char in char_count:
            return True
        char_count[char] = 1
    return False

def filter_for_duplicate_letters(word_list):
    """
    Filters a list of words and removes words that contain duplicates of the same letter.
    Returns a new list with filtered words.
    """
    filtered_list = []
    for word in word_list:
        if not has_duplicates(word):
            filtered_list.append(word)
    return filtered_list
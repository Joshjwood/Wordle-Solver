# Wordle-Solver

Spotted someone mention a similar project on /r/LearnPython and figured i'd give it a try going in blind.

This works using a near-exhaustive list of 5 letter words (taken from https://github.com/tabatkins/wordle-list/blob/main/words) and then gradually filters that list down based on the games feedback as you submit words.

For the first 3 guesses it simply trys to cover as much of the alphabet as possible, and on the 4th attempt it uses the information gathered (correct letters, incorrect letters, letters that are correct but in the wrong position) to make an earnest guess. It gets it right on the first guess surprisingly frequently, and i'm both pleased and impressed with it.

Since completing it, i've only seen it get it wrong on rare occassions the word isn't in the initial word list. I assume it's possible it may get it wrong if the word is one where 4 letters are identical but there are many options for the 5th such as Hunch, Munch, Bunch, Punch, Lunch, but given the first 3 guesses attempt to use as many of the most common letters of the alphabet as possible, even this should be largely mitigated.

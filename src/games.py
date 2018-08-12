"""Rock paper sciccors voice game"""

import sys
from random import randint

from .aiy.audio import say
from .aiy.cloudspeech import get_recognizer


def rock_paper_scissors() -> None:
    """Rock paper scissors game"""
    recognizer = get_recognizer()
    computer_choice = randint(0, 2)
    choices = ["rock", "scissors", "paper"]
    for choice in choices:
        recognizer.expect_phrase(choice)
    say("Ok lets play. Say your choice in 3...2...1")
    text = recognizer.recognize()
    if text is None:
        say("Sorry, I did not hear you.")
        return
    if sys.stdout.isatty():
        print("You said:", text)
    for choice in choices:
        if choice in text:
            player_choice = choices.index(choice)
            break
    if player_choice is None:
        say("Sorry, I did not hear you.")
        return
    say("I chose {}".format(choices[computer_choice]))
    if player_choice == computer_choice:
        say("Draw i guess")
    elif (
        (computer_choice == 0 and player_choice == 2)
        or (computer_choice == 1 and player_choice == 0)
        or (computer_choice == 2 and player_choice == 1)
    ):
        say("You Win")
    else:
        say("I Win")

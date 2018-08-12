"""Rock paper sciccors voice game"""

import sys
from random import randint

import aiy.audio
import aiy.cloudspeech


def rock_paper_scissors() -> None:
    """Rock paper scissors game"""
    recognizer = aiy.cloudspeech.get_recognizer()
    computer_choice = randint(1, 3)
    choices = {
        1: 'rock',
        2: 'scissors',
        3: 'paper',
    }
    for num, choice in choices.items():
        recognizer.expect_phrase(choice)
    aiy.audio.say('Ok lets play. Say your choice in 3...2...1')
    text = recognizer.recognize()
    if text is None:
        if sys.stdout.isatty():
            print('Sorry, I did not hear you.')
        return
    if sys.stdout.isatty():
        print('You said:', text)
    for num, choice in choices.items():
        if choice in text:
            player_choice = num
            break
    if player_choice is None:
        if sys.stdout.isatty():
            print('Sorry, I did not hear you.')
        return
    aiy.audio.say('I chose %s' % choices[computer_choice])
    if player_choice == computer_choice:
        aiy.audio.say('Draw i guess')
    elif ((player_choice > computer_choice and player_choice == 3) or
          (player_choice == 3 and computer_choice == 1)):
        aiy.audio.say('You Win')
    else:
        aiy.audio.say('I Win')

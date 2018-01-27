#!/usr/bin/env python3
"""Basic Bot that recognises simple commands

The Google Assistant Library can be installed with:
    pip install -r requirements.txt

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import json
import logging
import subprocess
import sys
import threading
import urllib

from google.assistant.library import Assistant
from google.assistant.library.event import EventType

import aiy.assistant.auth_helpers
import aiy.assistant.device_helpers
import aiy.audio
import aiy.voicehat
from games import rock_paper_scissors

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s")

with open('./config.json') as data:
    CONF = json.load(data)


class Butler(object):
    """Basic google Assistant for Raspberry PI"""

    def __init__(self):
        self._task = threading.Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None
        self.commands = {
            'power off': self.power_off_pi,
            'reboot': self.reboot_pi,
            'what is your ip address': self.say_ip,
            'is zen up?': self.check_zen,
            'backup zen': self.backup_zen,
            'migrate data warehouse': self.migrate_warehouse,
            'want a beer?': self.to_the_pub,
            'lets play rock paper scissors': rock_paper_scissors,
        }

    def start(self):
        """Starts the assistant."""
        self._task.start()

    def _run_task(self):
        credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
        model_id = aiy.assistant.device_helpers.get_ids(credentials)
        with Assistant(credentials, model_id) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

    def _process_event(self, event):
        status_ui = aiy.voicehat.get_status_ui()
        if event.type == EventType.ON_START_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            aiy.voicehat.get_button().on_press(self._on_button_pressed)
            if sys.stdout.isatty():
                print('Say "OK, Google" or press the button, then speak. '
                      'Press Ctrl+C to quit...')
        elif (event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and
              event.args):
            if sys.stdout.isatty():
                print('You said:', event.args['text'])
            text = event.args['text'].lower()
            # If it doesnt have the command let Google handle it
            if hasattr(self.commands, text):
                self._assistant.stop_conversation()
                self.commands[text]()
        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self._can_start_conversation = False
            status_ui.status('listening')
        elif event.type == EventType.ON_END_OF_UTTERANCE:
            status_ui.status('thinking')
        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True
        elif (event.type == EventType.ON_ASSISTANT_ERROR and event.args and
              event.args['is_fatal']):
            if sys.stdout.isatty():
                print('Fatal Error')
            sys.exit(1)

    def _on_button_pressed(self):
        if self._can_start_conversation:
            self._assistant.start_conversation()

    @staticmethod
    def power_off_pi():
        """Turns off Pi"""
        aiy.audio.say('Good bye!')
        subprocess.call('sudo shutdown now', shell=True)

    @staticmethod
    def reboot_pi():
        """Reboots Pi"""
        aiy.audio.say('See you in a bit!')
        subprocess.call('sudo reboot', shell=True)

    @staticmethod
    def say_ip():
        """Gets local ip of Assistant"""
        ip_address = subprocess.check_output(
            "hostname -I | cut -d' ' -f1", shell=True)
        aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))

    @staticmethod
    def backup_zen():
        """Wrapper around kubctl to run backup job"""
        subprocess.call(
            'kubectl replace --force -f ./%s' % CONF.backup, shell=True)
        aiy.audio.say('Backing up zen now')

    @staticmethod
    def migrate_warehouse():
        """Wrapper around kubctl to run migration job"""
        subprocess.call(
            'kubectl replace --force -f ./%s' % CONF.migrate, shell=True)
        aiy.audio.say('Migrating data Warehouse now')

    @staticmethod
    def check_zen():
        """ Check if zen is up"""
        responce = urllib.request.urlopen(CONF.zen_url).getcode()
        if responce == 200:
            aiy.audio.say('Yep, Zen is up')
        else:
            aiy.audio.say('Nope, Zen is down')

    @staticmethod
    def to_the_pub():
        """To the pub"""
        aiy.audio.say("Always, too o'Neil's")


if __name__ == '__main__':
    Butler().start()

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library with button support.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

from logging import INFO, basicConfig
from platform import machine
from sys import exit as _exit
from sys import stdout
from threading import Thread

from google.assistant.library.event import EventType

from .aiy.assistant.auth_helpers import get_assistant_credentials
from .aiy.assistant.library import Assistant
from .aiy.voicehat import get_button, get_status_ui

basicConfig(level=INFO, format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s")


class VoiceAssistant:
    """An assistant that runs in the background.

    The Google Assistant Library event loop blocks the running thread entirely.
    To support the button trigger, we need to run the event loop in a separate
    thread. Otherwise, the on_button_pressed() method will never get a chance
    to be invoked.
    """

    def __init__(self, commands: dict = {}) -> None:
        if machine() not in ("armv8", "armv7"):
            if stdout.isatty():
                print("Can only run on Pi 2 and 3")
            _exit(-1)
        self._task = Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None
        self._commands = commands

    def start(self):
        """Starts the assistant.

        Starts the assistant event loop and begin processing events.
        """
        self._task.start()

    def _run_task(self):
        with Assistant(get_assistant_credentials()) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

    def _process_event(self, event):
        if stdout.isatty():
            print(event)
        status_ui = get_status_ui()
        if event.type == EventType.ON_START_FINISHED:
            status_ui.status("ready")
            self._can_start_conversation = True
            # Start the voicehat button trigger.
            get_button().on_press(self._on_button_pressed)
            if stdout.isatty():
                print(
                    'Say "OK, Google" or press the button, then speak. '
                    "Press Ctrl+C to quit..."
                )
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            if stdout.isatty():
                print("You said:", event.args["text"])
            text = event.args["text"].lower()
            # If it doesnt have the command let Google handle it
            if hasattr(self._commands, text):
                self._assistant.stop_conversation()
                self._commands[text]()

        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self._can_start_conversation = False
            status_ui.status("listening")

        elif event.type == EventType.ON_END_OF_UTTERANCE:
            status_ui.status("thinking")

        elif (
            event.type == EventType.ON_CONVERSATION_TURN_FINISHED
            or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
            or event.type == EventType.ON_NO_RESPONSE
        ):
            status_ui.status("ready")
            self._can_start_conversation = True

        elif (
            event.type == EventType.ON_ASSISTANT_ERROR
            and event.args
            and event.args["is_fatal"]
        ):
            if stdout.isatty():
                print("Fatal Error")
            _exit(1)

    def _on_button_pressed(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()

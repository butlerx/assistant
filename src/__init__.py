from subprocess import call, check_output

from .aiy.audio import say
from .assistant import VoiceAssistant
from .games import rock_paper_scissors
from .tetris import play_tetris


class Butler(VoiceAssistant):
    """Basic google Assistant for Raspberry PI"""

    def __init__(self, conf):
        self.config = conf
        super().__init__(
            commands={
                "power off": self.power_off_pi,
                "reboot": self.reboot_pi,
                "what is your ip address": self.say_ip,
                "lets play rock paper scissors": rock_paper_scissors,
                "play tetris": play_tetris,
            }
        )

    @staticmethod
    def power_off_pi():
        """Turns off Pi"""
        say("Good bye!")
        call("sudo shutdown now", shell=True)

    @staticmethod
    def reboot_pi():
        """Reboots Pi"""
        say("See you in a bit!")
        call("sudo reboot", shell=True)

    @staticmethod
    def say_ip():
        """Gets local ip of Assistant"""
        ip_address = check_output("hostname -I | cut -d' ' -f1", shell=True)
        say("My IP address is %s" % ip_address.decode("utf-8"))

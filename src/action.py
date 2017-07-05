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

"""Carry out voice commands by recognising keywords."""

import datetime
import logging
import subprocess

import phue
from rgbxy import Converter

import actionbase
from spotify import Spotify

# =============================================================================
#
# Hey, Makers!
#
# This file contains some examples of voice commands that are handled locally,
# right on your Raspberry Pi.
#
# Do you want to add a new voice command? Check out the instructions at:
# https://aiyprojects.withgoogle.com/voice/#makers-guide-3-3--create-a-new-voice-command-or-action
# (MagPi readers - watch out! You should switch to the instructions in the link
#  above, since there's a mistake in the MagPi instructions.)
#
# In order to make a new voice command, you need to do two things. First, make a
# new action where it says:
#   "Implement your own actions here"
# Secondly, add your new voice command to the actor near the bottom of the file,
# where it says:
#   "Add your own voice commands here"
#
# =============================================================================

# Actions might not use the user's command. pylint: disable=unused-argument


# Example: Say a simple response
# ================================
#
# This example will respond to the user by saying something. You choose what it
# says when you add the command below - look for SpeakAction at the bottom of
# the file.
#
# There are two functions:
# __init__ is called when the voice commands are configured, and stores
# information about how the action should work:
#   - self.say is a function that says some text aloud.
#   - self.words are the words to use as the response.
# run is called when the voice command is used. It gets the user's exact voice
# command as a parameter.

class SpeakAction(object):

    """Says the given text via TTS."""

    def __init__(self, say, words):
        self.say = say
        self.words = words

    def run(self, voice_command):
        self.say(self.words)


# Example: Tell the current time
# ==============================
#
# This example will tell the time aloud. The to_str function will turn the time
# into helpful text (for example, "It is twenty past four."). The run function
# uses to_str say it aloud.

class SpeakTime(object):

    """Says the current local time with TTS."""

    def __init__(self, say):
        self.say = say

    def run(self, voice_command):
        time_str = self.to_str(datetime.datetime.now())
        self.say(time_str)

    def to_str(self, dt):
        """Convert a datetime to a human-readable string."""
        HRS_TEXT = ['midnight', 'one', 'two', 'three', 'four', 'five', 'six',
                    'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
        MINS_TEXT = ["five", "ten", "quarter", "twenty", "twenty-five", "half"]
        hour = dt.hour
        minute = dt.minute

        # convert to units of five minutes to the nearest hour
        minute_rounded = (minute + 2) // 5
        minute_is_inverted = minute_rounded > 6
        if minute_is_inverted:
            minute_rounded = 12 - minute_rounded
            hour = (hour + 1) % 24

        # convert time from 24-hour to 12-hour
        if hour > 12:
            hour -= 12

        if minute_rounded == 0:
            if hour == 0:
                return 'It is midnight.'
            return "It is %s o'clock." % HRS_TEXT[hour]

        if minute_is_inverted:
            return 'It is %s to %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])
        return 'It is %s past %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])


# Example: Run a shell command and say its output
# ===============================================
#
# This example will use a shell command to work out what to say. You choose the
# shell command when you add the voice command below - look for the example
# below where it says the IP address of the Raspberry Pi.

class SpeakShellCommandOutput(object):

    """Speaks out the output of a shell command."""

    def __init__(self, say, shell_command, failure_text):
        self.say = say
        self.shell_command = shell_command
        self.failure_text = failure_text

    def run(self, voice_command):
        output = subprocess.check_output(self.shell_command, shell=True).strip()
        if output:
            self.say(output.decode('utf-8'))
        elif self.failure_text:
            self.say(self.failure_text)


# Example: Change the volume
# ==========================
#
# This example will can change the speaker volume of the Raspberry Pi. It uses
# the shell command SET_VOLUME to change the volume, and then GET_VOLUME gets
# the new volume. The example says the new volume aloud after changing the
# volume.

class VolumeControl(object):

    """Changes the volume and says the new level."""

    GET_VOLUME = r'amixer get PCM | grep "Mono:" | sed "s/.*\[\([0-9]\+\)%\].*/\1/"'
    SET_VOLUME = 'amixer -q set PCM %d%%'
    LAST_VOL = 60

    def __init__(self, say, change):
        self.say = say
        self.change = change

    def run(self, voice_command):
        vol = self.change_vol(self.change, False)
        # self.say(_('Volume at %d %%.') % vol)

    @staticmethod
    def change_vol(change, history=True):
        res = subprocess.check_output(VolumeControl.GET_VOLUME, shell=True).strip()
        last_vol = int(res)
        vol = last_vol + change
        vol = max(0, min(100, vol))
        try:
            logging.info("volume: %s", res)
            subprocess.call(VolumeControl.SET_VOLUME % vol, shell=True)
        except (ValueError, subprocess.CalledProcessError):
            logging.exception("Error using amixer to adjust volume.")

        if history:
            VolumeControl.LAST_VOL = last_vol
        else:
            VolumeControl.LAST_VOL = vol

        print("Volume was " + str(VolumeControl.LAST_VOL))
        print("Volume set to " + str(vol))

    @staticmethod
    def undo():
        try:
            print("Volume reset to " + str(VolumeControl.LAST_VOL))
            subprocess.call(VolumeControl.SET_VOLUME % VolumeControl.LAST_VOL, shell=True)
        except (ValueError, subprocess.CalledProcessError):
            logging.exception("Error using amixer to adjust volume.")



# Example: Repeat after me
# ========================
#
# This example will repeat what the user said. It shows how you can access what
# the user said, and change what you do or how you respond.

class RepeatAfterMe(object):

    """Repeats the user's command."""

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):
        # The command still has the 'repeat after me' keyword, so we need to
        # remove it before saying whatever is left.
        to_repeat = voice_command.replace(self.keyword, '', 1)
        self.say(to_repeat)


# Example: Change Philips Light Color
# ====================================
#
# This example will change the color of the named bulb to that of the
# HEX RGB color and respond with 'ok'
#
# actor.add_keyword(_('change to ocean blue'), \
# 		ChangeLightColor(say, "philips-hue", "Lounge Lamp", "0077be"))

class ChangeLightColor(object):

    """Change a Philips Hue bulb color."""

    def __init__(self, say, bridge_address, bulb_name, hex_color):
        self.converter = Converter()
        self.say = say
        self.hex_color = hex_color
        self.bulb_name = bulb_name
        self.bridge_address = bridge_address

    def run(self):
        bridge = self.find_bridge()
        if bridge:
            light = bridge.get_light_objects("name")[self.bulb_name]
            light.on = True
            light.xy = self.converter.hex_to_xy(self.hex_color)
            self.say(_("Ok"))

    def find_bridge(self):
        try:
            bridge = phue.Bridge(self.bridge_address)
            bridge.connect()
            return bridge
        except phue.PhueRegistrationException:
            logging.info("hue: No bridge registered, press button on bridge and try again")
            self.say(_("No bridge registered, press button on bridge and try again"))


# Power: Shutdown or reboot the pi
# ================================
# Shuts down the pi or reboots with a response
#

class PowerCommand(object):
    """Shutdown or reboot the pi"""

    def __init__(self, say, command):
        self.say = say
        self.command = command

    def run(self, voice_command):
        if self.command == "shutdown":
            self.say("Shutting down, goodbye")
            subprocess.call("sudo shutdown now", shell=True)
        elif self.command == "reboot":
            self.say("Rebooting")
            subprocess.call("sudo shutdown -r now", shell=True)
        else:
            logging.error("Error identifying power command.")
            self.say("Sorry I didn't identify that command")

# =========================================
# Makers! Implement your own actions here.
# =========================================


class RgbLightCommand(object):
    """Control RGB Light"""

    def __init__(self, say, color):
        self.say = say
        self.color = color

    def run(self, voice_command):
        print(voice_command)
        subprocess.call(["/usr/bin/irsend", "SEND_ONCE", "rgb_controller", self.color])
        self.say("Light set to " + self.color)


class SpotifyCommand(object):
    """Control Spotify"""

    def __init__(self, say, mpd, command):
        self.say = say
        self.command = command
        self.mpd = mpd

    def run(self, voice_command):
        print(voice_command)
        if 'playlist' in self.command.lower():
            # playlist_name = self.command.replace('playlist', '').strip()
            playlist_name = voice_command.replace(self.keyword, '', 1)
            print(playlist_name)
            self.respond(self.mpd.shuffle_playlist(playlist_name), playlist_name)
        elif 'pause' in self.command.lower():
            self.mpd.pause()
        else:
            print(command)
            self.respond(self.mpd.play_song(self.command))

    def respond(self, status, extra=''):
        if status is self.mpd.SUCCESS:
            self.say(extra + ' playing')
        if status is self.mpd.FAILED_TO_CONNECT:
            self.say('Sorry, I could not connect')
        if status is self.mpd.PLAYLIST_NOT_FOUND:
            self.say('Sorry, I thing this playlist doesn\'t exist')
        if status is self.mpd.SONG_NOT_FOUND:
            self.say('Are you sure this song exists?')


def make_actor(say):
    """Create an actor to carry out the user's commands."""

    actor = actionbase.Actor()

    actor.add_keyword(
        _('ip address'), SpeakShellCommandOutput(
            say, "ip -4 route get 1 | head -1 | cut -d' ' -f8",
            _('I do not have an ip address assigned to me.')))

    actor.add_keyword(_('volume up'), VolumeControl(say, 10))
    actor.add_keyword(_('volume down'), VolumeControl(say, -10))
    actor.add_keyword(_('max volume'), VolumeControl(say, 100))

    actor.add_keyword(_('repeat after me'),
                      RepeatAfterMe(say, _('repeat after me')))

    # =========================================
    # Makers! Add your own voice commands here.
    # =========================================

    actor.add_keyword(_('raspberry power off'), PowerCommand(say, 'shutdown'))
    actor.add_keyword(_('raspberry reboot'), PowerCommand(say, 'reboot'))

    # My commands
    rgb_color_actor(actor, say)
    spotify_actor(actor, say)

    return actor


def spotify_actor(actor, say):
    mpd = Spotify()
    actor.add_keyword(_('listen to playlist'), SpotifyCommand(say, mpd, _('playlist')))
    actor.add_keyword(_('pause spotify'), SpotifyCommand(say, mpd, 'pause'))


def rgb_color_actor(actor, say):
    # RGB Light
    colors = [('green', 'green'),
              ('g1', 'green 1'),
              ('g2', 'green 2'),
              ('g3', 'green 3'),
              ('g4', 'green 4'),
              ('blue', 'blue'),
              ('b1', 'blue 1'),
              ('b2', 'blue 2'),
              ('b3', 'blue 3'),
              ('b4', 'blue 4'),
              ('red', 'red'),
              ('r1', 'red 1'),
              ('r2', 'red 2'),
              ('r3', 'red 3'),
              ('r4', 'red 4'),
              ('white', 'white')]

    for code, keyword in colors:
        actor.add_keyword(_('turn ' + keyword + ' light'), RgbLightCommand(say, code))
        actor.add_keyword(_('set light to ' + keyword), RgbLightCommand(say, code))

    actor.add_keyword(_('turn off the light'), RgbLightCommand(say, 'off'))
    actor.add_keyword(_('calm light'), RgbLightCommand(say, 'b3'))
    actor.add_keyword(_('hot light'), RgbLightCommand(say, 'r1'))
    actor.add_keyword(_('turn off the light'), RgbLightCommand(say, 'off'))
    actor.add_keyword(_('turn on the light'), RgbLightCommand(say, 'on'))
    actor.add_keyword(_('dim up the light'), RgbLightCommand(say, 'dim_u'))
    actor.add_keyword(_('dim down the light'), RgbLightCommand(say, 'dim_d'))
    actor.add_keyword(_('shuffle light'), RgbLightCommand(say, 'smooth'))


def add_commands_just_for_cloud_speech_api(actor, say):
    """Add simple commands that are only used with the Cloud Speech API."""
    def simple_command(keyword, response):
        actor.add_keyword(keyword, SpeakAction(say, response))

    simple_command('alexa', _("We've been friends since we were both starter projects"))
    simple_command(
        'beatbox',
        'pv zk pv pv zk pv zk kz zk pv pv pv zk pv zk zk pzk pzk pvzkpkzvpvzk kkkkkk bsch')
    simple_command(_('clap'), _('clap clap'))
    simple_command('google home', _('She taught me everything I know.'))
    simple_command(_('hello'), _('hello to you too'))
    simple_command(_('tell me a joke'),
                   _('What do you call an alligator in a vest? An investigator.'))
    simple_command(_('three laws of robotics'),
                   _("""The laws of robotics are
0: A robot may not injure a human being or, through inaction, allow a human
being to come to harm.
1: A robot must obey orders given it by human beings except where such orders
would conflict with the First Law.
2: A robot must protect its own existence as long as such protection does not
conflict with the First or Second Law."""))
    simple_command(_('where are you from'), _("A galaxy far, far, just kidding. I'm from Seattle."))
    simple_command(_('your name'), _('A machine has no name'))

    actor.add_keyword(_('time'), SpeakTime(say))

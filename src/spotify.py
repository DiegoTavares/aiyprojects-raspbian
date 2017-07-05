#!/usr/bin/env python3
import mpd


class Spotify(object):
    """Play songs in Spotify"""

    def __init__(self, server='localhost', port=6600):
        self.SUCCESS = 'success'
        self.FAILED_TO_CONNECT = 'connection failed'
        self.PLAYLIST_NOT_FOUND = 'playlist not found'
        self.SONG_NOT_FOUND = 'song not found'

        self.server = server
        self.port = port
        self.client = mpd.MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None

    def connect(self):
        try:
            self.client.connect(self.server, self.port)
        except:
            return self.FAILED_TO_CONNECT
        return self.SUCCESS

    def disconnect(self):
        try:
            self.client.close()
            self.client.disconnect()
        except:
            print('Nothing to disconnect')

    def shuffle_playlist(self, playlist_name):
        status = self.connect()
        if status is not self.SUCCESS:
            return status

        self.client.clear()
        try:
            self.client.load(playlist_name)
        except mpd.CommandError:
            return self.PLAYLIST_NOT_FOUND

        self.client.shuffle()
        self.client.play(0)
        self.disconnect()

        return self.SUCCESS

    def play_song(self, song_query):
        pass

    def pause(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status
        self.client.pause()
        self.disconnect()

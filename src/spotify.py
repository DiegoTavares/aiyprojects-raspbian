#!/usr/bin/env python3
impiort mpd


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
            for item in self.client.listplaylists():
                if playlist_name.lower() in item['playlist'].lower():
                    self.client.load(item['playlist'])
                    break

        except mpd.CommandError:
            self.disconnect()
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

    def resume(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status
        self.client.pause(1)
        self.disconnect()

    def next(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status
        self.client.next()
        self.disconnect()

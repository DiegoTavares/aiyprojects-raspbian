#!/usr/bin/env python3
import mpd
import time


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

        try:
            for item in self.client.listplaylists():
                if playlist_name.lower() in item['playlist'].lower():
                    self.client.clear()
                    self.client.load(item['playlist'])
                    break

        except mpd.CommandError:
            self.disconnect()
            return self.PLAYLIST_NOT_FOUND

        self.client.shuffle()
        self.client.play(0)
        self.disconnect()

        return self.SUCCESS

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
        self.client.pause()
        self.disconnect()

    def next(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status
        self.client.next()
        self.disconnect()

    def play_song(self, song_name):
        status = self.connect()
        if status is not self.SUCCESS:
            return status

        playlist_name = 'now_playing_' + time.strftime("%Y%m%d%H%M%S")
        self.client.searchaddpl(playlist_name, 'song', song_name)
        if song_list:
            self.client.load(playlist_name)
            self.client.play(1)

    def list_playlists(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status

        for item in self.client.listplaylists():
            yield item['playlist'].lower()

    def refresh(self):
        status = self.connect()
        if status is not self.SUCCESS:
            return status

        self.client.refresh()

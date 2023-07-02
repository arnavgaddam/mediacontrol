import asyncio
import os
import sys
from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import \
    DataReader, Buffer, InputStreamOptions, FileOutputStream
from colorthief import ColorThief
import json


class MediaPlayer:
    
    def __init__(self):
        self.sessions = None
        self.current_session = None

    async def create(self):
        self.sessions = await MediaManager.request_async()
        self.current_session = self.sessions.get_current_session()

    async def get_media_info(self):
        sessions = await MediaManager.request_async()

        # This source_app_user_model_id check and if statement is optional
        # Use it if you want to only get a certain player/program's media
        # (e.g. only chrome.exe's media not any other program's).

        # To get the ID, use a breakpoint() to run sessions.get_current_session()
        # while the media you want to get is playing.
        # Then set TARGET_ID to the string this call returns.

        current_session = sessions.get_current_session()
        timeline = current_session.get_timeline_properties().position

        if current_session:  # there needs to be a media session running
            # if current_session.source_app_user_model_id == TARGET_ID:
            info = await current_session.try_get_media_properties_async()

            # song_attr[0] != '_' ignores system attributes
            info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

            # converts winrt vector to list
            info_dict['genres'] = list(info_dict['genres'])
            info_dict['timeline'] = timeline

            # print(info_dict)
            # print(info_dict['thumbnail'])
            return info_dict

        # It could be possible to select a program from a list of current
        # available ones. I just haven't implemented this here for my use case.
        # See references for more information.
        raise Exception('TARGET_PROGRAM is not the current media session')

    async def read_stream_into_buffer(self, stream_ref, buffer):
        readable_stream = await stream_ref.open_read_async()
        readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)


    def update_thumbnail(self):
        # create the current_media_info dict with the earlier code first
        currentinfo = asyncio.run(self.get_media_info())
        thumb_stream_ref = currentinfo['thumbnail']
        # 5MB (5 million byte) buffer - thumbnail unlikely to be larger
        thumb_read_buffer = Buffer(10000000)
        # copies data from data stream reference into buffer created above
        asyncio.run(self.read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer))
        template_folder = ""
        static_folder = ""
        if getattr(sys, 'frozen', False):
            template_folder = os.path.join(sys._MEIPASS, 'templates')
            static_folder = os.path.join(sys._MEIPASS, 'static')
        with open(os.path.join(static_folder, "media_thumb.jpg"), 'wb') as fobj:
            fobj.write(bytearray(thumb_read_buffer))
        color_thief = ColorThief(os.path.join(static_folder, "media_thumb.jpg"))
        # get the dominant color
        dominant_color = color_thief.get_color(quality=6)
        palette = color_thief.get_palette(color_count=4)
        with open(os.path.join(static_folder, "colors.json"), "w") as outfile:
            json.dump(palette, outfile)

    async def play_pause(self):
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()

        if current_session:
            current_session.try_toggle_play_pause_async()

    async def next_track(self):
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()

        if current_session:
            current_session.try_skip_next_async()

    async def previous_track(self):
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()

        if current_session:
            current_session.try_skip_previous_async()






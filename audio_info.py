import os
import datetime
from mutagen.mp4 import MP4

class AudioInfo:
    @staticmethod
    def get_m4a_info(file_path):
        audio = MP4(file_path)
        creation_date = datetime.datetime.fromtimestamp(os.path.getctime(file_path), datetime.timezone.utc)
        info = {
            'size': os.path.getsize(file_path),
            'duration': audio.info.length,
            'tags': audio.tags,
            'creation_date': creation_date
        }
        return info

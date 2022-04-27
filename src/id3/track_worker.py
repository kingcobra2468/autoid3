from curses import meta
from shazamio import Shazam


from shazamio import Shazam
from id3.shazam_parser import ShazamParser

class TrackWorker:

    def __init__(self, track_queue):
        self._track_queue = track_queue
        self._shazam_client = Shazam()
    
    async def populate_track(self):
        while True:
            try:
                mp3_file = self._track_queue.get_nowait()
            except:
                break
            metadata = await self._shazam_client.recognize_song(mp3_file)
            
            parser = ShazamParser(metadata, mp3_file)
            await parser.fill_id3_data()
            
            self._track_queue.task_done()

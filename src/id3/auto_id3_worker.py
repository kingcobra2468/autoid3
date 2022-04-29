import asyncio

from aiohttp.client_exceptions import ClientConnectorError
from shazamio import Shazam
from id3.shazam_parser import ShazamParser


class AutoID3Worker:
    """AutoID3 worker that reads from a shared queue and process
    a track by doing Shazam recognition and ID3 tag filling. 
    """
    RECOGNITION_ATTEMPTS = 5
    
    def __init__(self, mp3_queue):
        """Constructor.

        Args:
            mp3_queue (asyncio.Queue): Queue that holds mp3 track file
            paths.
        """
        self._mp3_queue = mp3_queue
        self._shazam_client = Shazam()

    async def process_track(self):
        """Processes mp3 tracks from the queue. Each track is run against
        Shazam in order to extract metadata about the track. Select metadata
        is then saved within the track's ID3 tags   
        """
        while True:
            try:
                mp3_file = self._mp3_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            print(mp3_file, self._mp3_queue.qsize())

            metadata = await self._recognize_song(mp3_file)
            if not metadata:
                print(f'NO rec {mp3_file}')
                self._mp3_queue.task_done()
                continue

            parser = ShazamParser(metadata, mp3_file)
            parser.populate_id3_tags()

            self._mp3_queue.task_done()

    async def _recognize_song(self, mp3_file):
        """Attempts to recognize the track using Shazam up to RECOGNITION_ATTEMPTS
        tries to accomodate cases where the connection to Shazam might fail or error out.

        Args:
            mp3_file (str): Path to the mp3 track file.

        Returns:
            dict: The Shazam recognition of the track.
        """
        for _ in range(self.RECOGNITION_ATTEMPTS):
            try:
                return await asyncio.wait_for(self._shazam_client.recognize_song(mp3_file), 120)
            except (ConnectionResetError, ClientConnectorError, asyncio.TimeoutError):
                await asyncio.sleep(10)
                continue

        return None

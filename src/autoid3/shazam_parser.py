from pydub import AudioSegment
import eyed3
import httpx


class ShazamParser:
    """Parser which deals with the output of a track's Shazam recognition
    into compliant ID3 tags.  
    """

    def __init__(self, recognition, mp3_file):
        """Constructor.

        Args:
            recognition (dict): Shazam's recognition of a given track.
            mp3_file (_type_): Path of the mp3 file to which the
            ID3 tags will be changed.
        """
        self._recognition = recognition
        self._mp3_file = mp3_file

        self._audiofile = eyed3.load(self._mp3_file)

        # The input file is not actually an mp3 file. Converts the audio file
        # into an mp3 file.
        if not self._audiofile:
            sound = AudioSegment.from_file(self._mp3_file)
            sound.export(self._mp3_file, format="mp3")

            self._audiofile = eyed3.load(self._mp3_file)
            self._audiofile.initTag()

    def populate_id3_tags(self):
        """Adds various ID3 tag data to a given track that was extracted from
        the Shazam recognition.
        """
        self._audiofile.tag.title = self._get_title()
        self._audiofile.tag.artist = self._get_artist()
        self._audiofile.tag.album = self._get_album()
        self._audiofile.tag.genre = self._get_genre()

        self._audiofile.tag.save(encoding='utf-8')

        # TODO: make async
        with httpx.Client() as client:
            # retrieves the cover art and adds it as id3 image data
            cover_art_url = self._get_cover_art_url()
            # cover art not found
            if not cover_art_url:
                return

            response = client.get(cover_art_url)
            # cover art image doesn't exist
            if response.status_code != 200:
                return

            self._audiofile.tag.images.set(
                type_=1, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            self._audiofile.tag.images.set(
                type_=2, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            self._audiofile.tag.images.set(
                type_=3, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            self._audiofile.tag.images.set(
                type_=4, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)

        self._audiofile.tag.save(encoding='utf-8')

    def _get_title(self):
        """Fetches the title from the Shazam recognition.

        Returns:
            str: Title of the track.
        """
        try:
            return self._recognition['track']['title']
        except:
            return None

    def _get_album(self):
        """Fetches the album from the Shazam recognition.

        Returns:
            str: Album of the track
        """
        try:
            section = self.find_section(
                self._recognition['track']['sections'], 'SONG')
            metadata = self.find_metadata(section['metadata'], 'Album')

            return metadata['text']
        except:
            return None

    def _get_artist(self):
        """Fetches the artist from the Shazam recognition.

        Returns:
            str: Artist of the track
        """
        try:
            section = self.find_section(
                self._recognition['track']['sections'], 'ARTIST')
            return section['name']
        except:
            return None

    def _get_genre(self):
        """Fetches the genre from the Shazam recognition.

        Returns:
            str: Genre of the track
        """
        try:
            genres = self._recognition['track']['genres']['primary']
            return genres.split('/')[0]
        except:
            return None

    def _get_cover_art_url(self):
        """Fetches the cover art url from the Shazam recognition.

        Returns:
            str: Cover art url of the track
        """
        try:
            images_urls = self._recognition['track']['images']
            for image in ['coverart', 'coverarthq', 'background']:
                if image in images_urls:
                    return images_urls[image]

            return None
        except:
            return None

    def find_section(self, sections, name):
        """Finds the queried section from the "sections" component of the
        Shazam recognition.

        Args:
            sections (dict): The "sections" part of the Shazam recognition response. 
            name (str): Value of the "type" attribute of a section on which the query
            is performed.

        Returns:
            dict|None: If section exists, return its contents. Otherwise return None.
        """
        for section in sections:
            if section['type'] == name:
                return section

        return None

    def find_metadata(self, metadata, name):
        """Finds the queried metadata from the "metadata" component of the
        Shazam recognition.

        Args:
            metadata (dict): The "metadata" part of the Shazam recognition response. 
            name (str): Value of the "title" attribute of the metadata on which the query
            is performed.

        Returns:
            dict|None: If section exists, return its contents. Otherwise return None.
        """
        for data in metadata:
            if data['title'] == name:
                return data

        return None

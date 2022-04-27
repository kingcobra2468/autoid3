import eyed3
import httpx

class ShazamParser:
    def __init__(self, recognition, mp3_file):
        self._recognition = recognition
        self._mp3_file = mp3_file
        
    async def fill_id3_data(self):
        audiofile = eyed3.load(self._mp3_file)

        audiofile.tag.artist = self._get_artist()
        audiofile.tag.album = self._get_album()
        audiofile.tag.title = self._get_title()
        audiofile.tag.genre = self._get_genre()
        
        async with httpx.AsyncClient() as client:
            cover_art_url = self._get_cover_art_url()
            response = await client.get(cover_art_url)
            # cover art image doesn't exist
            if response.status_code != 200:
                return
            
            audiofile.tag.images.set(type_=1, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            audiofile.tag.images.set(type_=2, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            audiofile.tag.images.set(type_=3, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
            audiofile.tag.images.set(type_=4, img_data=response.content, mime_type="image/jpeg", img_url=cover_art_url)
        
        audiofile.tag.save()
                
    def _get_title(self):
        try:
            return self._recognition['track']['title']
        except:
            return None
    
    def _get_album(self):
        try:
            return self._recognition['track']['sections'][0]['metadata'][0]['text']
        except:
            return None
        
    def _get_artist(self):
        try:
            return self._recognition['track']['sections'][3]['name']
        except:
            return None
        
    def _get_genre(self):
        try:
            genres = self._recognition['track']['genres']['primary']
            return genres.split('/')[0]
        except:
            return None
    
    def _get_cover_art_url(self):
        try:
            return self._recognition['track']['images']['coverart']
        except:
            return None
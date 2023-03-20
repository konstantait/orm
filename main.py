from database import Database
from model import Model, StringField, IntegerField
from logger import root_logger

logger = root_logger()


class Playlists(Model):
    PlaylistId = IntegerField(primary_key=True)
    Name = StringField()


class Genres(Model):
    GenreId = IntegerField(primary_key=True)
    Name = StringField()


if __name__ == '__main__':
    db = Database('chinook.db')
    Playlists.objects.backend = db
    logger.info(f'Playlists.__dict__: {Playlists.__dict__}')
    for playlist in Playlists.objects.all():
        print(playlist.get('Name'))
    Playlists.objects.backend.close()

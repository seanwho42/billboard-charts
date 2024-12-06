import billboard
from lyricsgenius import Genius
import pandas as pd
import re

# really should make this an env variable but its free so I trust you with my token nathan
token = '0mpgH1IG8C2h8Yoik-R-bS-OuSNvzMKaOeJ_9spWaUXFeGHvacfrICRFbLgLqrbU'
genius = Genius(token, skip_non_songs=True, timeout=20, retries=10)

max_tries = 20

def get_songs_lyrics():
    '''
    main function... currently prints out the song info as we see it
    '''
    songs_lyrics = pd.DataFrame({
        'year':[],
        'month':[],
        'title':[],
        'artist':[],
        'rank': [],
        'lyrics':[]
    })
    for y in range(2018,2023):
        for m in range(1,13):
            top_30 = get_top_month(m, y)
            rank = 1
            for song in top_30:
                print(f'{song.title} in {m}-{y} by {song.artist} at number {rank}')

                # todo: parse out all artists included when the songs have collaborators
                first_artist, all_artists = parse_artist(song.artist)
                print(f'first_artist = {first_artist}, all_artists = {all_artists}')

                # need a while loop here to try until get_lyrics actually works because it was timing out a lot
                lyrics = get_lyrics(song.title, first_artist, all_artists)
                cleaned_lyrics = clean_lyrics(lyrics)
                songs_lyrics = songs_lyrics._append({
                    'year':y,
                    'month':m,
                    'title':song.title,
                    'artist':song.artist,
                    'rank':rank,
                    'lyrics':cleaned_lyrics
                }, ignore_index=True)
                rank += 1
                songs_lyrics.to_csv('songs-lyrics.csv', index=False)

def parse_artist(billboard_artist_name):
    '''
    Parses the artist names if multiple are listed
        billboard_artist_name: artist name returned by billboard.py song.artist
        return: the first artist name as string
        # todo: see about including collaborators to ensure we find the right songs
    '''
    # so billboard.py separates multiple artists with "Featuring"
    # now lets just delete everything that isn't the first artist....
    first_artist = re.sub(' Featuring.*', '', billboard_artist_name)

    second_artist = re.sub('.*Featuring ', '', billboard_artist_name)

    # adding this in for silk sonic
    first_artist = re.sub(' \(Bruno Mars & Anderson .Paak\)', '', first_artist)

    return first_artist, second_artist

def get_top_month(m, y):
    '''
    Gets the top 30 songs from the month
        m: month # as an integer
        y: year # as an integer
        return: list of top ten from billboard 100 in given month and year as billboard.py song objects
    '''
    # need to add arbitrary 01 to the end to have a date in YYYY-MM-DD format for ChartData()
    billboard_date='{year}-{month:0{width}}-01'.format(year=y, month=m, width=2)
    chart = billboard.ChartData('hot-100', date=billboard_date)
    top_thirty = chart[0:30]
    return top_thirty

def get_lyrics(title, first_artist, second_artist):
    '''
    Gets lyrics from genius and returns them given artist and song title
        title: song title as string
        artist: artist as string
        return: lyrics as string
    '''
    # todo: figure out if there is a way to search for someone as a collaborator
    # song = genius.search_song(title=title, artist=artist)

    # trying search by artist?
    # lyrics = song.lyrics
    try:
        # dumb thing thinks I want it to gather all of the songs which takes a million years, so we set max to 0
        artist = genius.search_artist(artist_name=f'{first_artist}', max_songs=0)
        print(f'Found artist: {artist.name}')
        print(f'artist id: {artist.id}')
    except:
        lyrics = f'Lyrics not found -- no artist found searching for artist_name {first_artist}'
        return lyrics

    print(artist)
    # need to pull the actual songs from the dictionary
    songs = genius.search_artist_songs(artist_id=artist.id, search_term=title, sort='popularity')['songs']
    for song in songs:
        song_artists = song['artist_names']
        print(song_artists)
        # todo: fuzzy match instead??
        if (second_artist in song_artists) and (first_artist in song_artists):
            print(f'song_artists "{song_artists}" matches first_artist "{first_artist}" and second_artist "{second_artist}"')
            lyrics = genius.lyrics(song_url=song['url'])
            return lyrics

    # going back through if there wasn't a match on both
    for song in songs:
        song_artists = song['artist_names']
        print(song_artists)
        if first_artist in song_artists:
            print(f'unable to match off of all_artists, matched off of first_artist "{first_artist}"')
            lyrics = genius.lyrics(song_url=song['url'])
            return lyrics

    lyrics = f'Lyrics not found -- no songs matched {title} by {second_artist} in {first_artist} discology'
    return lyrics

def clean_lyrics(rough_lyrics):
    # there are a few slip ups with the lyricsgenius library WRT web scarping...
    # this attempts to clean those up using regex

    # cutting out the numberEmbed thing
    no_embed_lyrics = re.sub("\d*Embed", "", rough_lyrics)
    # cutting out the ContributorTranslator gibberish
    no_contributor_lyrics = re.sub("^\d+.*\[", "[", no_embed_lyrics)
    # cutting out the weird partial image closing tag thing (this happens only 8 times as of writing this code)
    no_i_tag_lyrics = re.sub("/i>", "", no_contributor_lyrics)
    # no more bracket label things over the verses
    cut_out_bracket_labels = re.sub("\[.*]", "", no_i_tag_lyrics)
    # in case more things need to be cut out in the future
    # cleaned_lyrics = no_i_tag_lyrics
    cleaned_lyrics = cut_out_bracket_labels
    # print(cleaned_lyrics)
    return cleaned_lyrics


if __name__ == '__main__':
    get_songs_lyrics()


import billboard
from lyricsgenius import Genius
import pandas as pd
import re


token = '0mpgH1IG8C2h8Yoik-R-bS-OuSNvzMKaOeJ_9spWaUXFeGHvacfrICRFbLgLqrbU'
genius = Genius(token)


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
                parsed_artist_name = parse_artist()
                print(f'parsed_artist_name = {parsed_artist_name}')

                # need a while loop here to try until get_lyrics actually works because it was timing out a lot
                lyrics = get_lyrics(song.title, song.artist)
                print(lyrics)
                search_tries = 0
                while True:
                    print(f'searching for lyrics')
                    try:
                        search_tries += 1
                        if search_tries > 15:
                            lyrics = 'Lyrics not found -- timed out'
                            break
                        lyrics = get_lyrics(song.title, song.artist.name)
                        break
                    except:
                        pass
                # need to remove XXXEmbed -- though it could be as low as XEmbed where X is any given int
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

    # adding this in for silk sonic
    first_artist = re.sub(' \(Bruno Mars & Anderson .Paak\)', '', first_artist)

    return first_artist

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

def get_lyrics(title, artist_name):
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
    artist = genius.search_artist(search_term=f'{artist_name}')
    songs = artist.get_songs(sort='popularity')
    # if statement to match song title looping through each of the songs?
    # might run into issues with song titles having parentheses i.e. the amazing spiderman version of sunflower

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
    cut_out_bracket_labels = re.sub("^\[.*]$", "", no_i_tag_lyrics)

    # in case more things need to be cut out in the future
    # cleaned_lyrics = no_i_tag_lyrics
    cleaned_lyrics = cut_out_bracket_labels
    # print(cleaned_lyrics)
    return cleaned_lyrics


if __name__ == '__main__':
    get_songs_lyrics()


from test import assess_rap_lyrics



if __name__=="__main__":

    artist = input("ARTIST:  ")
    song = input("SONG:  ")
    dec = assess_rap_lyrics(artist, song)
    print(dec)
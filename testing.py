game = 'Valorant'
vidTitle = 'ValorantEliGEClip8.mp4'

# streamerName = vidTitle[len(game):]
streamerName = vidTitle[len(game):].split('Clip')[0]
print(streamerName)
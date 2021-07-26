vidNumber = 0
game = 'Just Chatting'
games = ['Valorant', 'GTAV', 'Just Chatting']
with open('videoCounter.txt', 'r') as fp:
    counts = []
    data = fp.readlines()
    for item in data:
        number = item.split(':')[1].strip()
        print(number)
        counts.append(number)

# List containing number of vids created for each game
print(counts)
if game == 'Valorant':
        vidNumber = counts[0]
        counts[0] = int(counts[0]) + 1
elif game == 'GTAV':
    vidNumber = counts[1]
    counts[1] = int(counts[1]) + 1
elif game == 'Just Chatting':
    vidNumber = counts[2]
    counts[2] = int(counts[2]) + 1

newFile = ''
for i in range(len(games)):
    newFile = newFile + f'{games[i]}: {counts[i]}\n'

print(newFile)
with open('videoCounter.txt', 'w') as fp:
    fp.write(newFile)

print(vidNumber)
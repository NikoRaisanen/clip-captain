import os

# directory = os.mkdir('testdir')
# print(directory)

test = os.walk('.')
print(test)

dirlist = os.listdir()
print(dirlist)
for item in dirlist:
    print(os.path.isdir(item))
print(os.getcwd())

os.getcwd

new = os.path.join(os.getcwd(), 'newHAHA')
os.mkdir(new)
print(new)
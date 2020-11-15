from pygame import mixer
import resources

class Sound:
    def __init__(self):
        self.sound = {}
        self.music = {}
        self.music_channels = {}
        self.channelIndex = 5
        self.MAX_INDEX = 15
        self.loadSound(resources.backgroundSound, 'background', True)
        mixer.set_num_channels(self.MAX_INDEX) # Being safe and getting 15 channels
        # Channels 0-4 are for music
        # Channels 5-14 are for SFX

    def loadSound(self, filename, keyword, isMusic = False):
        if isMusic:
            self.music[keyword] = mixer.Sound(filename)
            self.music_channels[keyword] = -1
        else:
            self.sound[keyword] = mixer.Sound(filename)

    def playSound(self, keyword):
        mixer.Channel(channelIndex).play(self.sound[keyword])
        channelIndex += 1
        if channelIndex >= 15:
            channelIndex = 5
    
    def playMusic(self, keyword):
        usedChannels = [n for n in self.music_channels.values]

        for n in range(5):
            if not (n in usedChannels):
                self.music_channels[keyword] = n
                mixer.Channel(n).play(self.music[keyword], -1)
    
    def stopMusic(self, keyword):
        mixer.Channel(self.music_channels[keyword]).stop()


from pydub import AudioSegment

# AudioSegment.from_wav('cut_endgame.wav').export('best.mp3', format='mp3')
AudioSegment.from_mp3('best.mp3').export('convert_best.wav', format='wav')

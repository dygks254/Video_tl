import os

os.system("ffmpeg -i \"English-Steve-Jobs.mp4\" -vf \" subtitles='build_trans/English-Steve-Jobsmp4_ko.txt.srt':fontsdir='/usr/share/fonts/truetype/nanum/NanumSquareL.ttf':force_style='FontName='NanumSquareL'' \" \"output_test.mp4\"")

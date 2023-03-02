from moviepy.editor import *
import pytesseract

# 자막 파일 읽기
subtitle = open('all_text.txt', 'r').read()

# 비디오 파일 읽기
video = VideoFileClip('video_translated_ko.mp4')

# 자막 영역 생성
subtitles = TextClip(subtitle, fontsize=24, color='white').set_pos(('center', 'bottom')).set_duration(video.duration)

# 자막 파일 저장
subtitles.write_vtt('subtitle.vtt')

# 자막 적용
video = video.set_subtitle('subtitle.vtt')

# 비디오 파일 저장
video.write_videofile('output.mp4')
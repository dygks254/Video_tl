#!/usr/bin/env python3.7

# coding=utf8
from gtts import gTTS
import gradio as gr
import os, datetime
import speech_recognition as sr
from googletrans import Translator, constants
from pprint import pprint
from moviepy.editor import *
from pydub import AudioSegment
from pydub.silence import split_on_silence
import soundfile as sf
import ffmpeg

import argparse
from pathlib import Path

def parser():
    parse = argparse.ArgumentParser("Transltation video text")

    parse.add_argument("--source"  , type=str, help="source mp4 video", required=True)
    parse.add_argument("--out_file", type=str, help="Translated file", default="")
    return parse

def get_large_audio_transcription(path2):

  tmp_str_trans = str_trans = str_source = ""


  ed_time = st_time = 0.000001
  translator = Translator()

  r = sr.Recognizer()
  sound = AudioSegment.from_wav(path2)

  chunks = split_on_silence(sound,
    min_silence_len = 500,
    silence_thresh = sound.dBFS-14,
    keep_silence=500,
  )
  
  text = ""

  for i, audio_chunk in enumerate(chunks[0], start=1):
    chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
    audio_chunk.export(chunk_filename, format="wav")
    with sr.AudioFile(chunk_filename) as source:
      audio_listened = r.record(source)

      f = sf.SoundFile( chunk_filename )
      print(chunks[1][i-1])
      
      st_time = chunks[1][i-1]['start'] / 1000.0 #(f.frames / f.samplerate)
      if i == 1:
        st_time = 0.0001
      ed_time = chunks[1][i-1]['end'] / 1000.0   #(f.frames / f.samplerate)

      try:
        text = r.recognize_google(audio_listened)
      except sr.UnknownValueError as e:
        print("Error:", str(e))
        pass
      else:
        text = f"{text.capitalize()}. "

        date_st = str( datetime.timedelta(seconds=st_time) ).replace(".",",")[0:-3]
        date_ed = str( datetime.timedelta(seconds=ed_time) ).replace(".",",")[0:-3]

        str_source += f"{i}\n{date_st} --> {date_ed}\n{text}\n\n"

        translation = translator.translate(text, dest='ko')
        str_trans += f"{i}\n{date_st} --> {date_ed}\n{text}\n{translation.text}\n\n"

        print(chunk_filename, ":", text)
        print(chunk_filename, ":", translation.text)
        print( datetime.timedelta(seconds=(f.frames / f.samplerate)))


    tmp_str_trans += text

  return str_source, str_trans

if __name__ == '__main__':
  args = parser().parse_args()

  file_name = str(args.source).split("/")[-1].replace(".","")

  folder_name = f"build/{file_name}"
  if os.path.isdir(folder_name):
    import shutil
    shutil.rmtree(folder_name, ignore_errors=True)
  os.makedirs(folder_name)

  videoclip = VideoFileClip(args.source)
  videoclip.audio.write_audiofile(f"{folder_name}/test.wav",codec='pcm_s16le')

  str_source = str_trans = ""
  str_source, str_trans = get_large_audio_transcription(f"{folder_name}/test.wav")

  if not os.path.isdir("build_trans"):
    os.makedirs("build_trans")
  output_file_name = file_name
  print(output_file_name)
  with open(f"build_trans/{output_file_name}_en.txt.srt".replace(" ",""),'w') as f_s:
    f_s.write(str_source)
  with open(f"build_trans/{output_file_name}_ko.txt.srt".replace(" ",""),'w') as f_o:
    f_o.write(str_trans)

  if not os.path.isdir("build_video"):
    os.makedirs("build_video")
  video = ffmpeg.input(args.source)
  audio = video.audio
  ffmpeg.concat(video.filter("subtitles", f"build_trans/{output_file_name}_en.txt.srt"), audio, v=1, a=1).output(f"build_video/{output_file_name}_en.mp4".replace(" ","")).run()
  
  os.system(f" ffmpeg -i \"{args.source}\" -vf \" subtitles='build_trans/{output_file_name}_ko.txt.srt':fontsdir='/usr/share/fonts/truetype/nanum/NanumSquareL.ttf':force_style='OutlineColour=&H80000000,BorderStyle=4,BackColour=&H80000000,Outline=0,Shadow=0,MarginV=15,Fontname=Arial,Fontsize=10,Alignment=2,FontName='NanumSquareL'' \" \"build_video/{output_file_name}_ko.mp4\" ")

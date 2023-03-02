#!/usr/bin/env python3.7

# coding=utf8
from gtts import gTTS
import gradio as gr
import os
import speech_recognition as sr
from googletrans import Translator, constants
from pprint import pprint
from moviepy.editor import *
from pydub import AudioSegment
from pydub.silence import split_on_silence

import argparse
from pathlib import Path

def parser():
    parse = argparse.ArgumentParser("Transltation video text")
    
    parse.add_argument("--source"  , type=Path, help="source mp4 video", required=True)
    parse.add_argument("--out_file", type=str, help="Translated file", default="")
    return parse

def get_large_audio_transcription(path2):
  
  tmp_str_trans = str_trans = str_source = ""
  
  r = sr.Recognizer()
  sound = AudioSegment.from_wav(path2)  
  
  chunks = split_on_silence(sound,
    min_silence_len = 1000,
    silence_thresh = sound.dBFS-14,
    keep_silence=500,
  )
    
  for i, audio_chunk in enumerate(chunks, start=1):
    chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
    audio_chunk.export(chunk_filename, format="wav")
    with sr.AudioFile(chunk_filename) as source:
      audio_listened = r.record(source)
      try:
        text = r.recognize_google(audio_listened)
      except sr.UnknownValueError as e:
        print("Error:", str(e))
      else:
        text = f"{text.capitalize()}. "
        print(chunk_filename, ":", text)
        str_source += text
        
    tmp_str_trans += text
        
    if i%5 == 0:
      translator = Translator()
      translation = translator.translate(tmp_str_trans, dest='ko')
      str_trans += translation.text
      tmp_str_trans = ""
    
  translator = Translator()
  translation = translator.translate(tmp_str_trans, dest='ko')
  str_trans += translation.text
  tmp_str_trans = ""
  
  return str_source, str_trans

if __name__ == '__main__':
  args = parser().parse_args()
  
  
  folder_name = "build"
  if os.path.isdir(folder_name):
    import shutil
    shutil.rmtree(folder_name, ignore_errors=True)  
  os.mkdir(folder_name)
  
  videoclip = VideoFileClip(str(args.source))
  videoclip.audio.write_audiofile("build/test.wav",codec='pcm_s16le')
  
  str_source, str_trans = get_large_audio_transcription("build/test.wav")
  
  
  if not os.path.isdir("build_trans"):
    os.makedirs("build_trans")
  output_file_name = str(args.source).split("/")[-1].replace("\ ","")
  with open(f"build_trans/{output_file_name}_en.txt",'w') as f_s:
    f_s.write(str_source)
  with open(f"build_trans/{output_file_name}_ko.txt",'w') as f_o:
    f_o.write(str_trans)
  
  # print(str_source)
  # print(str_trans)
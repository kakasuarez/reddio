import os
from time import sleep
from selenium import webdriver
from PIL import Image
from gtts import gTTS
from shutil import rmtree
from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.audio.io.AudioFileClip import AudioFileClip
# from moviepy.video.compositing.concatenate import concatenate_videoclips


class Capturer:
	def __init__(self):
		directories = ["audios", "videos", "images"]
		# * Clear out everything from the directories and remove them
		for directory in directories:
			if os.path.exists(directory):
				print(f"Directory {directory} found, clearing it\n")
				rmtree(directory)

		# * Create fresh directories
		for directory in directories:
			print(f"Creating new directory {directory}\n")
			os.mkdir(directory)
	
	def create_screenshot(self, url, post_number,is_comment=False,  comment_number=0):
		"""
		Takes a screenshot of the given url and crops it.
		"""
		save_path = f"images/post_{post_number}_uncropped.png"
		class_name = "Post"
		if is_comment:
			url = "https://reddit.com" + url
			class_name = "Comment"
			save_path = f"images/post_{post_number}_comment_{comment_number}_uncropped.png"
		with webdriver.Firefox() as driver:
			try:
				print(f"Going to url {url}\n")
				driver.get(url)
			except:
				print(f"Got an error, retrying in 5 seconds\n")
				sleep(5)
				driver.get(url)
			
			print(f"Creating screenshot {save_path}\n")
			driver.save_screenshot(save_path)

			element = driver.find_element_by_class_name(class_name)
			location = element.location
			size = element.size
			x = int(location["x"])
			y = int(location["y"])
			width =  x + int(size['width'])
			height = y + int(size['height'])
			self.__crop_screenshot(x, y, width, height, post_number, save_path)

	def __crop_screenshot(self, x, y, width, height, post_number, uncropped_path):
		"""
		Crops a given screenshot and saves it.
		"""
		print(f"Cropping screenshot {uncropped_path}\n")
		new_path = uncropped_path.replace("_uncropped", "")
		img = Image.open(uncropped_path)
		img = img.crop((x, y, width, height))
		os.remove(uncropped_path)
		print(f"Saving cropped screenshot {new_path}\n")
		img.save(new_path)
	
	def create_videoclip(self, post_number, is_comment=False, comment_number=0):
		"""
		Creates a video from the given details from the image and video paths.
		"""
		aud_path = f"audios/post_{post_number}.mp3"
		img_path = f"images/post_{post_number}.png"
		out_path = f"videos/post_{post_number}.mp4"
		if is_comment:
			aud_path = f"audios/post_{post_number}_comment_{comment_number}.mp3"
			img_path = f"images/post_{post_number}_comment_{comment_number}.png"
			out_path = f"videos/post_{post_number}_comment_{comment_number}.mp4"
		print(f"Creating video {out_path} from audio {aud_path} and image {img_path}\n")
		aud_clip = AudioFileClip(aud_path)
		vid_clip = ImageClip(img_path)
		vid_clip = vid_clip.set_audio(aud_clip).set_duration(aud_clip.duration)
		vid_clip.write_videofile(out_path, preset="medium", temp_audiofile='temp-audio.m4a', remove_temp=True, codec="mpeg4", audio_codec="aac", fps=24)
	
	def create_final_video(self, post_number, last_comment_number):
		"""
		Creates the final video by concatenating the previously made videos.
		"""
		print("Creating final video\n")
		audio_paths = []
		image_paths = []
		video_paths = []
		videos = []
		for i in range(1, post_number):
			audio_paths.append(f"audios/post_{i}.mp3")
			image_paths.append(f"images/post_{i}.png")
			video_paths.append(f"videos/post_{i}.mp4")
			videos.append(VideoFileClip(f"videos/post_{i}.mp4"))
			for j in range(1, last_comment_number + 1):
				audio_paths.append(f"audios/post_{i}_comment_{j}.mp3")
				image_paths.append(f"images/post_{i}_comment_{j}.png")
				video_paths.append(f"videos/post_{i}_comment_{j}.mp4")
				videos.append(VideoFileClip(f"videos/post_{i}_comment_{j}.mp4"))
		final_clip = concatenate_videoclips(videos, method="compose")
		final_clip.write_videofile("videos/final_video.avi", temp_audiofile='temp-audio-final.m4a', remove_temp=True, codec="png", audio_codec="aac", preset="medium", fps=24)
		# * Now that everything is done, remove the intermediate videos, audios and images
		for video in video_paths:
			print(f"Removing video {video}\n")
			os.remove(video)
		for audio in audio_paths:
			print(f"Removing audio {audio}\n")
			os.remove(audio)
		for image in image_paths:
			print(f"Removing image {image}\n")
			os.remove(image)


	def create_speech(self, content, post_number, is_comment=False, comment_number=0):
		"""
		Converts the given content to speech and saves it.
		"""
		save_path = f"audios/post_{post_number}.mp3"
		if is_comment:
			save_path = f"audios/post_{post_number}_comment_{comment_number}.mp3"
		print(f"Creating audio {save_path}\n")
		audio = gTTS(text=content, lang="en", slow=False)
		audio.save(save_path)

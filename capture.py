import os
from shutil import rmtree
from time import sleep

from gtts import gTTS
from moviepy.editor import (AudioFileClip, ImageClip, VideoFileClip,
                            concatenate_videoclips)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Capturer:
	def __init__(self):
		directories = ["audios", "videos", "images"]
		# Clear out everything from the directories and remove them
		for directory in directories:
			if os.path.exists(directory):
				print(f"Directory {directory} found, clearing it\n")
				rmtree(directory)

		# Create fresh directories
		for directory in directories:
			print(f"Creating new directory {directory}\n")
			os.mkdir(directory)
		
		self.driver = webdriver.Firefox()
		self.closed_sign_in_popup = False

	def __del__(self):
		self.driver.quit()
	
	def expand_shadow_element(self, element):
		# return a list of elements
		shadowRoot = self.driver.execute_script('return arguments[0].shadowRoot.children', element)
		return shadowRoot

	def _close_sign_in_popup(self):
		experience_tree = self.driver.find_element(By.TAG_NAME, "shreddit-experience-tree")
		first_shadow_root = self.expand_shadow_element(experience_tree)
		iframe_manager = first_shadow_root[0].find_element(By.TAG_NAME, "accountmanager-iframe")
		second_shadow_root = self.expand_shadow_element(iframe_manager)
		iframe_container = second_shadow_root[0]
		iframe = iframe_container.find_element(By.TAG_NAME, 'iframe')
		WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((iframe)))
		WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))) # There is an iframe inside an iframe.

		# Click on the close popup.
		WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "close"))).click()
		self.driver.switch_to.default_content() # Switch back from the iframes.
		self.closed_sign_in_popup = True

	def create_screenshot(self, url, post_number,is_comment=False, comment_number=0, has_replies=False):
		"""
		Takes a screenshot of the given url and crops it.
		"""
		save_path = f"images/post_{post_number}.png"
		class_name = "shreddit-post"
		if is_comment:
			url = "https://reddit.com" + url
			class_name = "shreddit-comment"
			save_path = f"images/post_{post_number}_comment_{comment_number}.png"
		try:
			print(f"Going to url {url}\n")
			self.driver.get(url)
		except:
			print(f"Got an error, retrying in 5 seconds\n")
			sleep(5)
			self.driver.get(url)
		sleep(5) # Prevents various errors by waiting for load.
		if not self.closed_sign_in_popup: # Only need to close the sign in popup once.
			self._close_sign_in_popup()

		print(f"Creating screenshot {save_path}\n")
		if is_comment:
			if has_replies:
				sc = self.driver.find_element(By.TAG_NAME, 'shreddit-comment')
				sr = self.expand_shadow_element(sc)[0]
				minus_button = sr.find_element(By.ID, "comment-fold-button")
				minus_button.click()
		element = self.driver.find_element(By.TAG_NAME, class_name)
		element.screenshot(save_path)
	
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
		final_clip.write_videofile("videos/final_video.mov", temp_audiofile='temp-audio-final.m4a', remove_temp=True, codec="mpeg4", audio_codec="aac", preset="medium", fps=24)
		# Now that everything is done, remove the intermediate videos, audios and images
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

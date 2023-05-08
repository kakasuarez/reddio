import os
from shutil import rmtree
from time import sleep

from gtts import gTTS
from moviepy.editor import (AudioFileClip, ImageClip, VideoFileClip,
                            concatenate_videoclips)
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configuration import use_custom_path, get_custom_path

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
		
		if use_custom_path:
			binary = FirefoxBinary(get_custom_path())
			self.driver = webdriver.Firefox(firefox_binary=binary)
		else:
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
		element = self.driver.find_element(By.TAG_NAME, class_name)
		if is_comment:
			if element.get_attribute("collapsed") is not None:
				# Need to click on the comment to open it.
				element.click()
			if has_replies:
				sc = self.driver.find_element(By.TAG_NAME, 'shreddit-comment')
				sr = self.expand_shadow_element(sc)[0]
				minus_button = sr.find_element(By.ID, "comment-fold-button")
				minus_button.click()
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
		audio_paths = os.listdir("audios")
		image_paths = os.listdir("images")
		video_paths = os.listdir("videos")
		videos = []
		for i in range(1, post_number):
			videos.append(VideoFileClip(f"videos/post_{i}.mp4"))
			comment_videos = []
			for j in video_paths:
				if j.startswith(f"post_{i}_comment"):
					comment_videos.append(f"videos/{j}")
			comment_videos.sort() # Just in case comment 2 is placed before comment 1, and so on.
			for comment_video in comment_videos:
				videos.append(VideoFileClip(comment_video))
		final_clip = concatenate_videoclips(videos, method="compose")
		final_clip.write_videofile("videos/final_video.mov", temp_audiofile='temp-audio-final.m4a', remove_temp=True, codec="mpeg4", audio_codec="aac", preset="medium", fps=24)
		# Now that everything is done, remove the intermediate videos, audios and images
		for video in video_paths:
			if video == "final_video.mov":
				continue
			print(f"Removing video videos/{video}\n")
			os.remove(f"videos/{video}")
		for audio in audio_paths:
			print(f"Removing audio audios/{audio}\n")
			os.remove(f"audios/{audio}")
		for image in image_paths:
			print(f"Removing image images/{image}\n")
			os.remove(f"images/{image}")


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

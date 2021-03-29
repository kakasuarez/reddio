import sys

import praw

from argument_help import get_args, get_options
from authenticate import authenticate
from capture import Capturer


def is_safe(post: praw.models.reddit.submission.Submission) -> bool:
	"""
	Takes a post and returns whether it is safe to put in a video.
	"""
	return not post.stickied and not post.over_18 and not post.spoiler and post.is_self


def save_comments(post: praw.models.reddit.submission.Submission, cpt: Capturer, post_number: int, comment_limit: int) -> None:
	"""
	Takes a post and creates images, audios, and videos for its comments.
	"""
	# Setting up comments
	post.comment_sort = "top"
	comment_number = 1
	# Getting top comments and saving
	for comment in post.comments:
		if comment.stickied:
			# Skip stickied comments (most likely bot or moderator comments)
			continue
		cpt.create_screenshot(comment.permalink, post_number, is_comment=True, comment_number=comment_number)
		cpt.create_speech(f"{comment.author} said: {comment.body}", post_number, is_comment=True, comment_number=comment_number)
		cpt.create_videoclip(post_number, is_comment=True,  comment_number=comment_number)
		if comment_number == comment_limit:
			break
		comment_number +=  1



def scrape_reddit(reddit: praw.Reddit, subreddit: praw.models.reddit.subreddit.Subreddit, post_limit: int, comment_limit: int) -> None:
	"""
	Scrapes reddit, captures images, videos, and audios and creates the final video.
	"""
	post_number = 1
	cpt = Capturer()
	for post in reddit.subreddit(subreddit).hot(limit=post_limit):
		if is_safe(post):
			title = post.title
			author = post.author
			url = post.url
			selftext = post.selftext
			# Getting the post and saving
			cpt.create_screenshot(url, post_number)
			cpt.create_speech(f"Post by {author}: {title}\n{selftext}", post_number)
			cpt.create_videoclip(post_number)
			save_comments(post, cpt, post_number, comment_limit)
			post_number += 1
	cpt.create_final_video(post_number, comment_limit)



def main():
	options = get_options(sys.argv[1:])
	subreddit, post_limit, comment_limit = get_args(options)
	reddit = authenticate()
	print("Starting\n")
	scrape_reddit(reddit, subreddit, post_limit, comment_limit)



if __name__ == "__main__":
    main()

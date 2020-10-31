import sys
import getopt
import praw
from authenticate import authenticate
from screenshot_capture import Capturer

def input_help(exit_code=0):
	"""
	Provides help with command line arguments and exits the process with the given exit code.
	"""
	print("reddit_bot.py -s <subreddit expression> -p <post limit> -c <last_comment_number>")
	print("reddit_bot.py -s <subreddit expression> --pl <post limit> --cl <last_comment_number>")
	print("reddit_bot.py --subreddit <subreddit expression> --post_limit <post limit> --last_comment_number <comment limit>")
	sys.exit(exit_code)

def get_args(options):
	"""
	Takes the options list and returns the chosen `subreddit`, `post_limit`, and `last_comment_number`. If some options are not provided, returns the default values for them. If a different option is provided, invokes the `input_help` function.
	"""
	subreddit = "AskReddit"
	post_limit = 10
	last_comment_number = 3
	for option, argument in options:
		if option in ("-h", "--help"):
			input_help()
		elif option in ("-s", "--subreddit"):
			subreddit = argument
		elif option in ("-p", "--pl", "--post_limit"):
			post_limit = int(argument)
		elif option in ("-c", "--lcn", "--last_comment_number"):
			last_comment_number = int(argument)
		else:
			input_help(1)
	return subreddit, post_limit, last_comment_number

def main():
	try:
		options, arguments = getopt.getopt(sys.argv[1:], "s:p:c:h", ["subreddit=", "post_limit=", "pl=", "last_comment_number=", "cl=", "help"])
	except getopt.GetoptError:
		input_help(2)
	subreddit, post_limit, last_comment_number = get_args(options)
	post_number = 1
	cpt = Capturer()
	reddit = authenticate()
	print("Starting\n")
	for post in reddit.subreddit(subreddit).hot(limit=post_limit):
		if not post.stickied and not post.over_18 and not post.spoiler:
			# * Post is safe
			title = post.title
			author = post.author
			url = post.url
			# * Getting the post and saving
			cpt.create_screenshot(url, post_number)
			cpt.create_speech(f"Question by {author}: {title}", post_number)
			cpt.create_videoclip(post_number)
			post.comment_sort = "top"
			comment_number = 1
			# * Getting top comments and saving
			for comment in post.comments:
				if comment.stickied:
					# * Skip stickied comments (most likely bot or moderator comments)
					continue
				cpt.create_screenshot(comment.permalink, post_number, is_comment=True, comment_number=comment_number)
				cpt.create_speech(f"{comment.author} said: {comment.body}", post_number, is_comment=True, comment_number=comment_number)
				cpt.create_videoclip(post_number,is_comment=True,  comment_number=comment_number)
				if comment_number == last_comment_number:
					break
				comment_number +=  1
			post_number += 1
	cpt.create_final_video(post_number, last_comment_number)



if __name__ == "__main__":
    main()

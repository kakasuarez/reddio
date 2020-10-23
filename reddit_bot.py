import praw
from authenticate import authenticate
from screenshot_capture import Capturer

def main():
	post_number = 1
	cpt = Capturer()
	reddit = authenticate()
	subreddit = input("""Please enter the subreddit (leave blank for "AskReddit") : \n""") or "AskReddit"
	post_limit = int(input("""Please specify the limit of posts (leave blank for "10") : \n""") or "10")
	last_comment_number = int(input("""Please specify the number of comments (leave blank for "3") : \n""") or "3")
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

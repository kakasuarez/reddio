import getopt
import sys
from configuration import get_default_arguments

def get_options(argv):
	"""
	Takes `sys.argv[1:]` as parameter and returns the options chosen. If there is an error with the options, invokes the `input_help` function.
	"""
	try:
		options, arguments = getopt.getopt(argv, "s:p:c:h:u:", ["subreddit=", "post_limit=", "pl=", "comment_limit=", "cl=", "help", "upload="])
	except getopt.GetoptError:
		input_help(2)
	return options

def input_help(exit_code=0):
	"""
	Provides help with command line arguments and exits the process with the given exit code.
	"""
	print("python bot.py -s <subreddit expression> -p <post limit> -c <comment_limit> -u <0 or 1>")
	print("python bot.py -s <subreddit expression> --pl <post limit> --cl <comment_limit> --upload <0 or 1>")
	print("python bot.py --subreddit <subreddit expression> --post_limit <post limit> --comment_limit <comment limit> --upload_choice <0 or 1>")
	sys.exit(exit_code)

def get_args(options):
	"""
	Takes the options list and returns the chosen `subreddit`, `post_limit`, and `comment_limit`. If some options are not provided, returns the default values for them. If a different option is provided, invokes the `input_help` function.
	"""
	default_args = get_default_arguments()
	subreddit = default_args["subreddit"]
	post_limit = default_args["post_limit"]
	comment_limit = default_args["comment_limit"]
	upload_choice = int(default_args["upload_choice"])
	upload_subreddit = default_args["upload_subreddit"]
	for option, argument in options:
		if option in ("-h", "--help"):
			input_help()
		elif option in ("-s", "--subreddit"):
			subreddit = argument
		elif option in ("-p", "--pl", "--post_limit"):
			post_limit = int(argument)
		elif option in ("-c", "--cl", "--comment_limit"):
			comment_limit = int(argument)
		elif option in ("-u", "--upload", "--upload_choice"):
			upload_choice = int(argument)
		else:
			input_help(1)
	return subreddit, post_limit, comment_limit, upload_choice, upload_subreddit

import getopt
import sys


def get_options(argv):
	"""
	Takes `sys.argv[1:]` as parameter and returns the options chosen. If there is an error with the options, invokes the `input_help` function.
	"""
	try:
		options, arguments = getopt.getopt(argv, "s:p:c:h", ["subreddit=", "post_limit=", "pl=", "comment_limit=", "cl=", "help"])
	except getopt.GetoptError:
		input_help(2)
	return options

def input_help(exit_code=0):
	"""
	Provides help with command line arguments and exits the process with the given exit code.
	"""
	print("python bot.py -s <subreddit expression> -p <post limit> -c <comment_limit>")
	print("python bot.py -s <subreddit expression> --pl <post limit> --cl <comment_limit>")
	print("python bot.py --subreddit <subreddit expression> --post_limit <post limit> --comment_limit <comment limit>")
	sys.exit(exit_code)

def get_args(options):
	"""
	Takes the options list and returns the chosen `subreddit`, `post_limit`, and `comment_limit`. If some options are not provided, returns the default values for them. If a different option is provided, invokes the `input_help` function.
	"""
	subreddit = "AskReddit"
	post_limit = 10
	comment_limit = 3
	for option, argument in options:
		if option in ("-h", "--help"):
			input_help()
		elif option in ("-s", "--subreddit"):
			subreddit = argument
		elif option in ("-p", "--pl", "--post_limit"):
			post_limit = int(argument)
		elif option in ("-c", "--cl", "--comment_limit"):
			comment_limit = int(argument)
		else:
			input_help(1)
	return subreddit, post_limit, comment_limit

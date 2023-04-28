# reddio
Reddit video maker written in python.
A simple project which generates videos with audio and images of hot posts on reddit.


# Set up

 - Clone the repository.
 - Create a reddit application from the [official reddit website](https://www.reddit.com/prefs/apps/).
 - Install the `virtualenv` library: `pip install virtualenv`.
 - Create a virtual environment: `python -m venv env`.
 - Start the virtual environment (```env\Scripts\activate``` on Windows).
 - Install the libraries required: ```pip install -r requirements.txt```.
 - Create a `praw.ini` file in the working directory as described [here](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html).
 - Create an `authenticate.py` file in the working directory and add code similar to this in it:
    ```py
    import praw

    def authenticate():
	    return praw.Reddit("your application name which you added in the praw.ini file", user_agent="test bot")
    ```
 - Install Geckodriver (if you wish to use Firefox):
   1. Go to the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases). Find the latest version of the driver for your platform and download it.
   2. Extract it.
   3. (For Windows) Add it to Path using Command Prompt: ```setx path "%path%;GeckoDriver Path"```.
 - If you want to upload the video to reddit, create a `thumbnail.png` file in the working directory which will be the thumbnail for the video on reddit.
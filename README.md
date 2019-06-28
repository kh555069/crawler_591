# crawler_591
using python-3.5.2

1. `pip install -r package.txt`

2. replace token in run.py

3. `python run.py`

![image](https://github.com/kh555069/crawler_591/blob/master/image.png)


#### Setup a cron job to run every x minutes
1. Input `crontab -e` in command line

2. If you use vim to edit files,
press `i` and input `*/10 * * * * python /PATH/TO/crawler_591/run.py`

3. Press `Esc` to finish, `:wq` to save and quit.

After setup is complete, it will crawl 591 and sent notify to your Line every 10 minutes.

# import os
import functools
import os
import random
import schedule
import time
import git
import requests
import json

# bing
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Connection": "close",
}
wallpaper_path = "/Users/xind/projects/idea/auto-scripts"

# git
git_repo_path = "/Users/xind/projects/idea/auto-scripts"


def dump_bing_wp():
    # 解析 URL
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx={}&n={}".format(1, 1)
    res = requests.get(url, headers=headers)
    res.encoding = 'utf8'

    json_data = json.loads(res.text)
    uri = json_data['images'][0]['url']

    # get picture
    img = requests.get("https://s.cn.bing.net/" + uri, headers=headers).content
    desc = str(json_data['images'][0]['copyright']).split("，")[0]
    dt = json_data['images'][0]['startdate']

    # output path
    output = git_repo_path + '/bingwp/'
    if not os.path.exists(output):
        os.mkdir(output)
    name = '{}.jpg'.format(dt + "_" + desc)

    out = open(output + name, 'wb')
    out.write(img)
    return name


def random_commit(t):
    repo = git.Repo(git_repo_path)
    # update
    repo.git.pull()

    # get pict
    name = dump_bing_wp()

    if name is None:
        print(t, " - name: ", name, " invalid, not commit.")
        return

    repo.git.add(A=True)

    repo.git.commit(m="add {}".format(name))
    print(t, " - will commit: ", name)
    repo.git.push()
    print(t, " - push successful.")


def job():
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    r = random.Random()
    r_int = r.randint(1, 100)
    if r_int > 50:
        print(t, " - random percent: ", r_int, "%, execute auto-commit ...")

        random_commit(t)
    else:
        print(t, " - random percent: ", r_int, "%, terminal process.")


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                # job()
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=False)
def bad_task():
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(t, " - will execute schedule task...")
    job()
    return True


schedule.every().second.do(bad_task)
# schedule.every(2).hours.do(bad_task)

while True:
    schedule.run_pending()
    time.sleep(10)

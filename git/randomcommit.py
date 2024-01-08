import functools
import json
import os
import random
import time

import git
import requests
import schedule

# bing
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Connection": "close",
}

# git
# git_repo_path = "/Users/xind/projects/idea/auto-scripts"
git_repo_path = "/home/xind/workspace/auto-scripts"

# all execute count
execute_count = 1

# every day limit
current_day = ''
current_day_count = 1
current_day_limit = 3


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

    desc = str.replace(desc, "/", "_").replace(" ", "_")
    # output path
    output = git_repo_path + '/bingwp/'
    if not os.path.exists(output):
        os.mkdir(output)
    name = '{}.jpg'.format(dt + "_" + desc)
    # 如果次数小于3次name加时间戳
    if os.path.exists(output + name):
        if current_day_count < current_day_limit:
            name = '{}_{}_{}.jpg'.format(dt, desc, current_day_count)
        else:
            print("{}-{} exists".format(dt, desc))
            return "exists"

    out = open(output + name, 'wb')
    out.write(img)
    return name


def execute_commit():
    repo = git.Repo(git_repo_path)
    # update
    repo.git.pull()

    # get pict
    name = dump_bing_wp()
    if name is None:
        print("{}, name is None, not commit".format(name))
        return False
    if name == "exists":
        print("{}, exists, not commit".format(name))
        return False

    repo.git.add(A=True)
    #repo.git.commit(" -m {}".format(name))
    repo.git.execute(["git", "commit", "-m", "add-{}".format(name)])
    print("will commit: {}".format(name))
    repo.git.push()
    print("push successful")
    return True


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=False)
def job():
    global execute_count
    global current_day, current_day_count

    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # every day limit
    if current_day_count >= current_day_limit:
        print("{} - every day limit. day: {}, day-total: {}".format(ts, current_day, current_day_count))
        return False
    # touch every count limit
    cu_day = time.strftime('%Y%m%d', time.localtime())
    if current_day == '' or current_day is None or current_day != cu_day:
        current_day = cu_day
        current_day_count = 1
        print("{} - touch every count limit. day: {}, day-total: {}".format(ts, current_day, current_day_count))

    print("{} - execute task, count: {}, day: {}, day-total: {}".format(ts,execute_count, current_day, current_day_count))
    # main job start --------------------------
    r = random.Random()
    r_int = r.randint(1, 100)
    if r_int > 50:
        print('{} - {}%, execute auto-commit...'.format(ts, r_int))
        rlt = execute_commit()
        #rlt = True
        if rlt:
            current_day_count += 1
    else:
        print('{} - {}%, terminal.'.format(ts, r_int))
    # main job end --------------------------
    execute_count += 1
    return True


#schedule.every(10).seconds.do(job)
# 每隔10秒钟执行一次
# schedule.every(1).minute.at(":02").do(job)
# 每过2个小时的12分执行
schedule.every(2).hours.at(":12").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

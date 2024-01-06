# import os
import functools
import logging
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

LOG_FORMAT = "%(asctime)s [%(levelname)7s:%(lineno)-3d]: %(message)s"
# 对logger进行配置——日志等级&输出格式
logging.basicConfig(filename='./log.log', level=logging.INFO, format=LOG_FORMAT)

# git
#git_repo_path = "/Users/xind/projects/idea/auto-scripts"
git_repo_path = "/home/xind/workspace/auto-scripts"

# all execute count
execute_count = 1

# every day limit
current_day = ''
current_day_count = 1


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


def execute_commit():
    repo = git.Repo(git_repo_path)
    # update
    repo.git.pull()

    # get pict
    name = dump_bing_wp()
    if name is None:
        logging.warning("{}, name is None, not commit".format(name))
        return

    repo.git.add(A=True)
    repo.git.commit(m="'add {}'".format(name))
    logging.info("will commit: {}".format(name))
    repo.git.push()
    logging.info("push successful")


def job():
    global execute_count
    global current_day, current_day_count

    # every day limit
    if current_day_count > 5:
        logging.warning("every day limit. day: {}, day-total: {}".format(current_day, current_day_count))
        return False
    # touch every count limit
    cu_day = time.strftime('%Y%m%d', time.localtime())
    if current_day == '' or current_day is None:
        current_day = cu_day
    if current_day != cu_day and current_day_count >= 5:
        current_day = cu_day

    logging.info("execute task, count: {}, day: {}, day-total: {}".format(execute_count, current_day, current_day_count))
    # main job start --------------------------
    r = random.Random()
    r_int = r.randint(1, 100)
    if r_int > 50:
        logging.info('{}%, execute auto-commit...'.format(r_int))
        execute_commit()
        if current_day == cu_day:
            current_day_count += 1
    else:
        logging.info('{}%, terminal.'.format(r_int))
    # main job end --------------------------
    execute_count += 1


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                logging.error("error: {}".format(traceback.format_exc()))
                # print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=False)
def bad_task():
    job()
    return True


# schedule.every().second.do(bad_task)
# 每隔10秒钟执行一次
#schedule.every(1).minute.at(":02").do(bad_task)
# 每过2个小时的12分执行
schedule.every(2).hours.at(":12").do(bad_task)

while True:
    schedule.run_pending()
    time.sleep(1)

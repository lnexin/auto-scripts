import functools
import json
import os
import random
import time
import datetime
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
current_day_limit = 25


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
        # if current_day_count < current_day_limit:
        #     name = '{}_{}_{}.jpg'.format(dt, desc, current_day_count)
        # else:
        #     print("{}-{} exists".format(dt, desc))
        #     return "exists"
        print("{}-{} exists, discard this picture save  ".format(dt, desc))
        return "exists"

    out = open(output + name, 'wb')
    out.write(img)
    return name

# 拉图片任务
def execute_commit():
    repo = git.Repo(git_repo_path)
    # update
    repo.git.pull()

    allow = can_generate()
    if not allow:
        print("can not allow generate, not commit")
        return False
    # get pict
    name = dump_bing_wp()
    if name is None:
        print("{}, name is None, not commit".format(name))
        return False
    if name == "exists":
        print("{}, exists, not commit".format(name))
        return False

    repo.git.add(A=True)
    # repo.git.commit(" -m {}".format(name))
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



# 公共变量
max_daily_generations = None
current_generation_count = 0
is_initialized = False

def can_generate():
    global max_daily_generations, current_generation_count, is_initialized

    # 获取当前日期和是否为工作日的信息
    today = datetime.datetime.now()
    is_weekday = today.weekday() < 5  # 0-4 是工作日

    # 初始化每日参数
    if not is_initialized or today.hour == 0:
        if is_weekday:
            # 工作日：80% 几率大于 0，但不超过 30，总次数不能大于 3
            if random.random() < 0.8:
                max_daily_generations = random.randint(1, min(30, 3))
            else:
                max_daily_generations = 0
        else:
            # 非工作日：70% 的几率为 0，总次数不能大于 3
            if random.random() < 0.7:
                max_daily_generations = 0
            else:
                max_daily_generations = random.randint(1, 3)

        current_generation_count = 0
        is_initialized = True

    # 检查是否达到最大生成次数
    if current_generation_count >= max_daily_generations:
        return False

    # 检查是否允许生成
    if is_weekday:
        # 工作日首次允许的几率为 100%
        if current_generation_count == 0:
            current_generation_count += 1
            return True
        else:
            # 几率随着次数增加而变小，但不低于 30%
            chance = max(0.3, 1 - current_generation_count / max_daily_generations)
            if random.random() < chance:
                current_generation_count += 1
                return True
    else:
        # 非工作日允许的几率不变，但不大于 30%
        if random.random() < 0.3:
            current_generation_count += 1
            return True

    return False


def generate_random_number():
    timestamp = int(time.time())
    random_number = random.getrandbits(54)  # 54 bits of randomness
    return (timestamp << 54) | random_number


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

    print("{} - execute task, count: {}, day: {}, day-total: {}".format(ts, execute_count, current_day,
                                                                        current_day_count))
    # main job start --------------------------
    r = random.Random()
    r_int = r.randint(1, 100)
    if r_int > 50:
        print('{} - {}%, execute auto-commit...'.format(ts, r_int))
        rlt = execute_commit()
        # rlt = True
        if rlt:
            current_day_count += 1
    else:
        print('{} - {}%, terminal.'.format(ts, r_int))
    # main job end --------------------------
    execute_count += 1
    return True


# schedule.every(10).seconds.do(job)
# 每隔10秒钟执行一次
# schedule.every(1).minute.at(":02").do(job)
# 每过2个小时的12分执行
schedule.every(1).hours.at(":12").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

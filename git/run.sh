#!/bin/bash
echo "start random commit task..."
> log.log
#python3 ./randomcommit.py > run.log &
nohup python3 -u ./randomcommit.py &
#nohup python3 -u ./randomcommit.py > log.log 2>&1 &

# nohup python -u Job.py > log.log 2>&1 &
# 说明：
# 末尾的 &：表示后台运行程序
# nohup ：保证程序不被挂起
# python：调用 python 解释器
# -u：表示不启用缓存，实时输出打印信息到日志文件(如果不加-u，则会导致日志文件不会实时刷新代码中的print函数的信息)
# Job.py：是 python 的源代码文件
# log.log：是输出的日志文件
# >：是指将打印信息重定向到日志文件
# 2>&1：将标准错误输出转变化标准输出，可以将错误信息也输出到日志文件中(0-> stdin, 1->stdout, 2->stderr)

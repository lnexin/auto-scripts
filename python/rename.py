import os
from pathlib import Path

path = Path("/Volumes/xindwebdav.ddnsto.com/sata1-18040367200/视频/电视剧/风起陇西.HD1080P.全24集")

# path = "/Volumes/xindwebdav.ddnsto.com/sata1-18040367200/视频/电视剧/老友记全10季/"
# files = [file for file in path.rglob("*.*")]
# for file in files:
#     print(file.name + os.path.join(file.parents))
#
for filename in os.listdir(path):
    # print(filename)
    # 构建完整的文件路径（注意：使用 os.path.join 可以跨平台构建路径）
    old_filepath = os.path.join(path, filename)
    # 构建新的文件名（这里以 "new_" 为前缀）
    # new_filename = ((filename.replace("[1994]", ".1997")
    #                  .replace("]", "."))
    #                 .replace("..", "."))

    new_filename = filename.replace("E.", "S01E")
    new_filepath = os.path.join(path, new_filename)
    if old_filepath == new_filepath:
        continue

    print(new_filepath)
    os.rename(old_filepath, new_filepath)

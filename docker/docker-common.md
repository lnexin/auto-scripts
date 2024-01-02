
### docker build
使用 docker build 命令来构建 Docker 镜像并指定自定义命名的 Dockerfile 文件
```bash
docker build -t my-image:latest -f /path/to/Dockerfile.myname .
```

`-t` my-image:latest: 为构建的镜像指定名称和标签  

`-f` /path/to/Dockerfile.myname: 指定要使用的 Dockerfile 文件路径和文件名。注意，这里需要包含文件扩展名

`.` 表示当前目录，即 Docker 上下文的根目录。Docker 在构建镜像时会将此目录中的所有内容打包发送给 Docker 引擎进行处理。

通过这种方式，您就可以指定不同于默认的 Dockerfile 文件名，并运行相应的构建过程。
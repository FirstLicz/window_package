## 构建容器
docker build -t packaging:webterminal .
## 启动容器
docker run -itd --name package -p 1022:22 --privileged=true packaging:webterminal /usr/sbin/init




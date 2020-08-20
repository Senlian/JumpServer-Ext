# JumpServer扩展计划
## 环境搭建
### 开发环境
- 安装CentOs7虚拟机
- 安装python3，配置pip源，修改yum相关文件头
    > /usr/bin/yum文件头修改为python2.7,/usr/libexec/urlgrabber-ext-down件头修改为python2.7
- 配置Python虚拟环境，安装开发模块（此处注意django版本和tree版本要与requirements.txt一致）
- 配置pycharm远程开发环境
- 安装docker
- docker安装mysql
```text
export MYSQL_ROOT_PASSWORD=123=abc
docker run -d --name=mysql --ip=172.17.0.2 -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /home/data/mysql:/var/lib/mysql -p 3306:3306 mariadb
# 数据库创建
mysql -h127.0.0.1 -uroot -p123=abc
create database jumpserver default charset 'utf8';
grant all on jumpserver.* to 'jumpserver'@'%' identified by 'weakPassword';
flush privileges;

```
- docker安装redis
```text
docker run -d --name=redis --ip=172.17.0.3 -v /home/data/redis:/data -p 6379:6379 redis
```
- docker安装guacamole
```text
# 注意容器8080端口与JUMPSERVER_SERVER服务端口冲突，将jumpserver端口改为8088
docker pull jumpserver/jms_guacamole:latest

docker run --name guacamole -d \
  --ip 172.17.0.5 \
  -p 8080:8080 \
  -e JUMPSERVER_SERVER=http://172.17.0.1:8088 \
  -e BOOTSTRAP_TOKEN=aJHFjuGPG1V9fIib \
  -e GUACAMOLE_LOG_LEVEL=ERROR \
  jumpserver/jms_guacamole
```
- docker安装jms_koko
```text
docker pull jumpserver/jms_koko:latest

docker run --name koko -d \
  --ip 172.17.0.4 \
  -p 2222:2222 \
  -p 5000:5000 \
  -e CORE_HOST=http://172.17.0.1:8088 \
  -e BOOTSTRAP_TOKEN=aJHFjuGPG1V9fIib \
  -e LOG_LEVEL=ERROR \
  -e REDIS_HOST=172.17.0.3 \
  -e REDIS_PORT=6379 \
  --link redis:172.17.0.3 \
  jumpserver/jms_koko 
```
- docker安装nginx
docker pull nginx
```text
docker run -d --name=nginx --ip 172.17.0.6 \
--volume=/home/data/nginx/logs/:/var/log/nginx \
--volume=/home/data/nginx/conf/nginx.conf:/etc/nginx/nginx.conf \
--volume=/home/data/nginx/www/:/usr/share/nginx/html \
--volume=/home/data/nginx/conf/conf.d/:/etc/nginx/conf.d -p 80:80 \
--link guacamole:172.17.0.5 \
--link koko:172.17.0.4 \
nginx
```
- 安装luna
```bash
 # 下载luna组件
 wget https://github.com/jumpserver/luna/releases/download/2.0.1/luna.tar.gz
 # 解压并拷贝到nginx的html目录下，容器拷贝到对应的映射目录
 # 授予nginx用户和组权限
 chown -R nginx:nginx luna
```


### 调试运行
- 调试运行
> 注意media目录不能用本地软连接作为容器卷目录，否则录像无法正确找到

## 源码解读
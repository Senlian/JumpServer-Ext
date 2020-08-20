# JumpServer 开发环境搭建
## 安装Python3
```bash
# 下载安装包
wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
# 安装依赖
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel libffi-devel
yum install gcc -y
tar -zxvf Python-3.8.2.tgz
cd Python-3.8.2

export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./configure --prefix=/usr/local/python3/ --with-ssl
make & makeinstall
ln -s /usr/local/python3/bin/python3.8 /usr/local/bin/python
ln -s /usr/local/python3/bin/python3.8 /usr/local/bin/python3
ln -s /usr/local/python3/bin/python3.8 /usr//bin/python
ln -s /usr/local/python3/bin/python3.8 /usr//bin/python3
# /usr/bin/yum文件头修改为python2.7
# /usr/libexec/urlgrabber-ext-down件头修改为python2.7
# pip 安装

python -m pip install wheel
python -m pip install --upgrade pip setuptools
python -m pip install virtualenv
# 创建python虚拟环境
python -m venv venv/jumpserver/
#安装git
yum install -y git
```
 
## 搭建JumpServer开发环境
```bash
git clone https://github.com/jumpserver/jumpserver.git -o git/jumpserver
cd venv/jumpserver/bin
source active
cd git/jumpserver/requirements
yum install -y $(cat rpm_requirements.txt)
# 去掉版本号防止安装失败
awk -F ==  '{print $1}' requirements.txt > requirements_new.txt
# pip安装
pip install -r requirements_new.txt
```
```text
国内源：#
清华：https://pypi.tuna.tsinghua.edu.cn/simple

阿里云：http://mirrors.aliyun.com/pypi/simple/

中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/

华中理工大学：http://pypi.hustunique.com/

山东理工大学：http://pypi.sdutlinux.org/ 

豆瓣：http://pypi.douban.com/simple/

note：新版ubuntu要求使用https源，要注意。

例如：pip3 install -i https://pypi.doubanio.com/simple/ 包名

临时使用：#
可以在使用pip的时候加参数-i https://pypi.tuna.tsinghua.edu.cn/simple
例如：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyspider，这样就会从清华这边的镜像去安装pyspider库。

永久修改，一劳永逸：#
Linux下，修改 ~/.pip/pip.conf (没有就创建一个文件夹及文件。文件夹要加“.”，表示是隐藏文件夹)

内容如下：

[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
windows下，直接在user目录中创建一个pip目录，再新建文件pip.ini。（例如：C:\Users\WQP\pip\pip.ini）内容同上。
```

## docker环境安装
```text
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
yum-config-manager --add-repo https://mirrors.ustc.edu.cn/docker-ce/linux/centos/docker-ce.repo
sed -i 's/$releasever/7/g' Centos-Base.repo
yum clean all
yum makecache
```
```bash
yum install -y yum-utils device-mapper-persistent-data lvm2
yum -y install libseccomp
yum install --installroot=/usr/local/docker docker-ce docker-ce-cli containerd.io
配置docker服务/usr/lib/systemd/system/docker.service
systemctl start docker

docker pull mariadb
docker pull redis
docker pull jumpserver/jms_koko
docker pull jumpserver/jms_guacamole

关闭selinux
sed -i 's/enforcing/disabled/g' /etc/selinux/config
reboot

export MYSQL_ROOT_PASSWORD=123=abc
docker run -itd --name=mysql --ip=172.17.0.2 -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /home/data/mysql:/var/lib/mysql -p 3306:3306 mariadb
docker run -itd --name=redis --ip=172.17.0.3 -v /home/data/redis:/data -p 6379:6379 redis
# 数据库创建
mysql -h127.0.0.1 -uroot -p123=abc
create database jumpserver default charset 'utf8';
grant all on jumpserver.* to 'jumpserver'@'%' identified by 'weakPassword';

# koko 和 guacamole是远程连接相关的，开发阶段可以暂时不启动
./jms start all 启动项目
```
```text
启动koko
docker run --name jms_koko -d \
  -p 2222:2222 \
  -p 127.0.0.1:5000:5000 \
  -e CORE_HOST=http://192.168.159.10:8080 \
  -e BOOTSTRAP_TOKEN=aJHFjuGPG1V9fIib \
  -e LOG_LEVEL=ERROR \
  --restart=always \
  jumpserver/jms_koko
```
```text
启动jms_guacamole
docker run --name jms_guacamole -d \
  -p 8081:8080 \
  -e JUMPSERVER_SERVER=http://192.168.159.10:8080 \
  -e BOOTSTRAP_TOKEN=aJHFjuGPG1V9fIib \
  -e GUACAMOLE_LOG_LEVEL=ERROR \
  jumpserver/jms_guacamole
```
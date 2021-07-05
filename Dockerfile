FROM centos:7
LABEL maintainer licunzhen@bwda.net
ENV LANG C.UTF-8

USER root

WORKDIR /app

# install python3 # 安装常用软件
RUN yum install make wget pcre pcre-devel zlib zlib-devel git gcc-c++ bzip2-devel openssl  openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel gcc libffi-devel -y \
    && yum install kde-l10n-Chinese glibc-common dos2unix -y && localedef -c -f UTF-8 -i zh_CN zh_CN.utf8 \
    && wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tar.xz \
    && tar -xvf Python-3.6.9.tar.xz \
    && cd Python-3.6.9/ && ./configure --prefix=/app/python3 --enable-shared && make && make install \
    && ln -s /app/python3/bin/python3 /usr/bin/python3 && ln -s /app/python3/bin/pip3 /usr/bin/pip3 \
    && cd .. && rm -rf Python-3.6.9 Python-3.6.9.tar.xz && cp /app/python3/lib/libpython3.* /usr/lib64 \
    && pip3 install --upgrade pip && pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple/ \
    && pip3 config set install.trusted-host mirrors.aliyun.com \
    && yum install -y passwd openssl openssh-server vim curl rsync bzip2 tcpdump less telnet net-tools lsof \
    && yum clean all
ENV LC_ALL zh_CN.UTF-8

# 初始化ssh登陆
RUN ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N '' \
    && ssh-keygen -q -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N '' \
    && ssh-keygen -t dsa -f /etc/ssh/ssh_host_ed25519_key -N '' \
    && sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config \
    && echo "Lcz123456" | passwd --stdin root

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

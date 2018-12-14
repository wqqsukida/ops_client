#!/bin/bash
 
#这里可替换为你自己的执行程序，其他代码无需更改
 
APP_NAME=/opt/dera_ops_client/bin/run.py
#使用说明，用来提示输入参数
usage() {
    echo "Usage: sh run_client.sh [start|stop|restart|status|enable|disable]"
    exit 1
}
 
#检查程序是否在运行
is_exist(){
  pid=`ps -ef|grep $APP_NAME|grep -v grep|awk '{print $2}'`
  #如果不存在返回1，存在返回0     
  if [ -z "${pid}" ]; then
   return 1
  else
    return 0
  fi
}
 
#启动方法
start(){
  is_exist
  if [ $? -eq 0 ]; then
    echo "${APP_NAME} is already running. pid=${pid}"
  else
    nohup python ${APP_NAME}  >run_client.out 2>&1 &
  fi
}
 
#停止方法
stop(){
  is_exist
  if [ $? -eq "0" ]; then
    kill -9 $pid
  else
    echo "${APP_NAME} is not running"
  fi  
}
 
#输出运行状态
status(){
  is_exist
  if [ $? -eq "0" ]; then
    echo "${APP_NAME} is running. Pid is ${pid}"
  else
    echo "${APP_NAME} is NOT running."
  fi
}
 
#重启
restart(){
  stop
  sleep 5
  start
}

#添加开机启动
enable(){
  grep 'sh /opt/dera_ops_client/run_client.sh start' /etc/rc.d/rc.local > /dev/null
  if [ $? -eq "0" ];then
    echo "${APP_NAME} in already in rc.local."
  else
    sed -i '$a\sh /opt/dera_ops_client/run_client.sh start' /etc/rc.d/rc.local
    chmod +x /etc/rc.d/rc.local
  fi
}

#禁用开机启动
disable(){
  sed -i '/run_client.sh start/d' /etc/rc.d/rc.local
  chmod -x /etc/rc.d/rc.local
}
 
#根据输入参数，选择执行对应方法，不输入则执行使用说明
case "$1" in
  "start")
    start
    ;;
  "stop")
    stop
    ;;
  "status")
    status
    ;;
  "restart")
    restart
    ;;
  "enable")
    enable
    ;;
  "disable")
    disable
    ;;
  *)
    usage
    ;;
esac

ps aux|grep jd.ini|awk {'print $2'}|xargs kill -9

nohup uwsgi --ini /root/jd_tools/jd.ini &>/var/log/jd_web.log &


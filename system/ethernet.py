'''
    1. /etc/network/interfaces 中 eth0 默认为 dhcp 模式
    2. 启动后读取配置文件。mode为dhcp或static模式
    3. dhcp --> static
        ifconfig eth0 192.168.0.1 netmask 255.255.255.0
        /etc/init.d/dhcpd-server restart
    4. static --> dhcp
        /etc/init.d/dhcpd-server stop
        ifconfig eth0 down
        ifconfig eth0 up
'''
* ### ethernet
* -i \<device> [--command \<command>] [--args]

--command init:    read ini file & init device

--command get:     get device status

--command set:     set device mode

    ` 
      --mode:    dhcp or static
      --addr:    inet address. e.g. 127.0.0.1
      --netmask: netmask. e.g. 255.255.255.0
    `

* ### wifi
* -i \<device> [--command \<command>] [--args]

--command init:    read ini file & init device

--command get:     get device status

--command set:     set device mode or params

    `
      --ssid:    ap ssid
      --psk:     ap psk
    `
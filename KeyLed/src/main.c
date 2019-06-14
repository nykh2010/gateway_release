/*
 * main.c
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */
#include <stdio.h>
#include <stdlib.h>
#include "sysmonitor.h"


int main(int argc, char *argv[]) {
	int ret;
    printf("sysmonitor start\n");

    ret = create_monitor();
    if (ret != 0) {
    	printf("create monitor failed\n");
    	exit(1);
    }
    monitor_loop_forever();
    close_monitor();
    exit(0);
}

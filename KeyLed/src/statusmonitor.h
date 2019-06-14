/*
 * statusmonitor.h
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#ifndef SRC_STATUSMONITOR_H_
#define SRC_STATUSMONITOR_H_
#include "mylist.h"

typedef enum {
	NET_MONITOR,
	CPU_USAGE_MONITOR,
	MEM_USAGE_MONITOR,
	FLASH_USAGE_MONITOR,
	PROCESS_MONITOR,
	MAX_STATUS_MONITOR
} MONITOR_NAME;

typedef struct {
	MONITOR_NAME monitor_name;
	int (*monitor_handler)();
	struct list_head list;
} StatusMonitor;

extern StatusMonitor *status_monitor_register();

#endif /* SRC_STATUSMONITOR_H_ */

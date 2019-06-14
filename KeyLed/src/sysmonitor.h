/*
 * sysmonitor.h
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#ifndef SRC_SYSMONITOR_H_
#define SRC_SYSMONITOR_H_

#include <key.h>
#include <led.h>
#include "statusmonitor.h"
#include <pthread.h>
#include <semaphore.h>
#include "mylist.h"

typedef enum {
	REBOOT,
	ENTER_CONFIG,
	EXIT_CONFIG,
	RESTORE,
	SHUT_DOWN,
	DISCONNECT,
	CONNECT,
	ERROR,
	CLR_ERROR,
	FATAL_ERROR,
	CLR_FATAL_ERROR,
	SLEEP,
	NONE
} EVENTS ;

typedef void*(*PRESS_HANDLER)(void *);
typedef struct {
	EVENTS event_num;
	struct list_head list;
}EVENT_LIST;

typedef struct {
	PRESS_HANDLER *handlers;
	KEY *key_list;
	LED *led_list;
	StatusMonitor *stmonitor_list;
	EVENT_LIST *event_list;
	pthread_t handler_thread;
	sem_t event_sem;
} Monitor;

extern int create_monitor();
extern int monitor_loop_forever();
extern int close_monitor();


#endif /* SRC_SYSMONITOR_H_ */

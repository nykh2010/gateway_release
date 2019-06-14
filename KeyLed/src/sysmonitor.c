/*
 * sysmonitor.c
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */
#include "sysmonitor.h"
#include <stdlib.h>
#include <sys/time.h>
#include <signal.h>
#include <errno.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>

void *reboot_handler(void *arg);
void *enter_config_handler(void *arg);
void *exit_config_handler(void *arg);
void *restore_handler(void *arg);
void *shut_down_handler(void *arg);
void *disconnect_handler(void *arg);
void *connect_handler(void *arg);
void *error_handler(void *arg);
void *clear_error_handler(void *arg);
void *fatal_error_handler(void *arg);
void *clear_fatal_error_handler(void *arg);
void *sleep_handler(void *arg);
void *none_handler(void *arg);

static Monitor *monitor = NULL;
const PRESS_HANDLER handlers[] = {
	    reboot_handler,
	    enter_config_handler,
	    exit_config_handler,
	    restore_handler,
	    shut_down_handler,
	    disconnect_handler,
	    connect_handler,
	    error_handler,
	    clear_error_handler,
	    fatal_error_handler,
	    clear_fatal_error_handler,
	    sleep_handler,
	    none_handler
};

int create_monitor() {
	printf("create_monitor start\n");
	monitor = (Monitor *)malloc(sizeof(Monitor));
	if (monitor == NULL) {
		printf("monitor malloc failed\n");
		return 1;
	}
	monitor->handlers = handlers;
	monitor->key_list = key_register();
	if (monitor->key_list == NULL) {
		printf("get key_list failed\n");
		return 1;
	}
	monitor->led_list = led_register();
	if (monitor->led_list == NULL) {
		printf("get led_list failed\n");
		return 1;
	}
	monitor->stmonitor_list = status_monitor_register();
	if (monitor->stmonitor_list == NULL) {
		printf("get stmonitor_list failed\n");
		return 1;
	}
	monitor->event_list = malloc(sizeof(EVENT_LIST));
	INIT_LIST_HEAD(&monitor->event_list->list);
	sem_init(&monitor->event_sem, 0, 0);
	printf("create_monitor end\n");
	return 0;
}

int close_monitor() {
	sem_destroy(&monitor->event_sem);
	free(monitor);
	return 0;
}

void *monitor_handler(void *param) {
	Monitor *parent = (Monitor *)param;
	int sem_ret;
	void *(*func)(void *) = NULL;
	int i;
	struct list_head *pos;
	struct list_head *n;
	StatusMonitor *tmp;
	while(1) {
		struct timespec now;
		clock_gettime(CLOCK_REALTIME, &now);
		now.tv_sec += 10;
		sem_ret = sem_timedwait(&parent->event_sem, &now);
		if (sem_ret != 0) {
			// 超时，扫描监控程序
			printf("scan status\n");
			list_for_each_safe(pos, n, &parent->stmonitor_list->list) {
				tmp = list_entry(pos, StatusMonitor, list);
				EVENTS event_num = tmp->monitor_handler();
				if (event_num != NONE) {
					EVENT_LIST *event = (EVENT_LIST *)malloc(sizeof(EVENT_LIST));
					event->event_num = event_num;
					list_add_tail(&event->list, &parent->event_list->list);
					sem_post(&parent->event_sem);
				}
			}
		}
		else {
			// 处理事件
			printf("event handler\n");
			EVENT_LIST *event_tmp;
			event_tmp = list_entry(parent->event_list->list.next, EVENT_LIST, list);
			printf("get event: %d\n", event_tmp->event_num);
			func = parent->handlers[event_tmp->event_num];
			list_del(&event_tmp->list);
			func(NULL);
		}
	}
}

void monitor_interval_handler(int signum) {
	int (*func)() = NULL;
	int i;
	struct list_head *pos;
	struct list_head *n;
	KEY *key_tmp;
	LED *led_tmp;

	if (signum == SIGALRM) {
		// 四分之一秒中断
		//检测按键
		//printf("key detect\n");
		list_for_each_safe(pos, n, &monitor->key_list->list) {
			key_tmp = list_entry(pos, KEY, list);
			func = get_key_event(key_tmp);
			if (func != NULL) {
				EVENTS event_num = func();
				if (event_num != NONE) {
					printf("new event: %d\n", event_num);
					EVENT_LIST *new_event = malloc(sizeof(EVENT_LIST));
					new_event->event_num = event_num;
					list_add_tail(&new_event->list, &monitor->event_list->list);
					sem_post(&monitor->event_sem);
				}
			}
		}
		//检测led
		list_for_each_safe(pos, n, &monitor->led_list->list) {
			led_tmp = list_entry(pos, LED, list);
			led_blink(led_tmp);
		}
	}
}

int monitor_loop_forever() {
	printf("monitor_loop_forever start\n");
	int ret;
    struct timeval interval_time;
    struct itimerval expiration_time;
    interval_time.tv_sec = 0;
    interval_time.tv_usec = 250000;		// 250ms
    expiration_time.it_interval = interval_time;
    expiration_time.it_value = interval_time;
    ret = setitimer(ITIMER_REAL, &expiration_time, NULL);
    if (ret != 0) {
        return ret;
    }
    signal(SIGALRM, monitor_interval_handler);
    pthread_create(&monitor->handler_thread, NULL, monitor_handler, monitor);
    pthread_join(monitor->handler_thread, NULL);
    return 0;
}


/*
 execute a system command
*/
static int cmd_system(const char *command, char *buf, int bufSize)
{
    printf("cmd_system : %s\n", command);

    char buf_ps[1024*10] = { 0 };
    int rc = -1;
    FILE *fpRead = 0;

    fpRead = popen(command, "r");

    if (!fpRead) {
        printf("popen NULL\n");
        return rc;
    }

    memset(buf_ps, 0, sizeof(buf_ps));
    memset(buf, 0, bufSize);

    while(fgets(buf_ps, sizeof(buf_ps), fpRead) != NULL) {
        if(strlen(buf) + strlen(buf_ps) > bufSize - 1) {
            break;
        }
        strcat(buf, buf_ps);
    }

    if(fpRead != NULL) {
        rc = pclose(fpRead);
    }

    int len = strlen(buf);

    if(len > 0 && '\n' == buf[len - 1]) {
        buf[len - 1] = 0;
    }

    if (rc < 0) {
        return rc;
    }

    return WEXITSTATUS(rc);
}

void * reboot_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
    system("reboot");
    return NULL;
}

void *enter_config_handler(void *arg) {
    /* 进入配置状态 */
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(CONFIGLED);
	led->blink_type = ON;
	char command_buf[32] = {0};
	cmd_system("cat /etc/gateway/system.ini | sed -n -r 's/inet4_addr\\s+=\\s+([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})/\\1/p'", \
			command_buf, sizeof(command_buf));
	char command[256] = {0};
	sprintf(command, "/home/root/connect -i ethernet --command set --mode static --addr %s --netmask 255.255.255.0", command_buf);
	cmd_system(command, command_buf, sizeof(command_buf));
    return NULL;
}

void * exit_config_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(CONFIGLED);
	led->blink_type = OFF;
	char command_buf[32] = {0};
	cmd_system("/home/root/connect -i ethernet --command set --mode dhcp", command_buf, sizeof(command_buf));
    return NULL;
}

void * restore_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	int ret;
    DIR *bin_dir = opendir('/media/bin');
    DIR *config_dir = opendir('/media/gateway');
    if (bin_dir && config_dir) {
    	system("/home/root/restore &");
    }
    if (bin_dir)
    	closedir(bin_dir);
    if (config_dir)
    	closedir(config_dir);
    return NULL;
}

void * shut_down_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	system("shutdown");
    return NULL;
}

void * disconnect_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(CONNECTLED);
    led->blink_type = OFF;
	return NULL;
}

void * connect_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(CONNECTLED);
	led->blink_type = ON;
	return NULL;
}

void * error_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(SYSLED);
	led->blink_type = TWINKLE;
    return NULL;
}

void * clear_error_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(SYSLED);
	led->blink_type = OFF;
    return NULL;
}

void * fatal_error_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(SYSLED);
	led->blink_type = ON;
    return NULL;
}

void * clear_fatal_error_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
	LED *led = get_led(SYSLED);
	led->blink_type = OFF;
    return NULL;
}

void * sleep_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
    return NULL;
}

void * none_handler(void *arg) {
	printf("%s start\n", __FUNCTION__);
    return NULL;
}

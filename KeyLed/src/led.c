/*
 * led.c
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#include "led.h"
#include <stdlib.h>
#include <fcntl.h>

static LED *led_list;

#define LED_MAP_INIT	{\
							{SYSLED, "led_y"},\
							{CONNECTLED, "led1_g"},\
							{CONFIGLED, "led2_g"}\
						}

const struct LED_MAP{
	LED_NAME led_name;
	char name[20];
} led_map[] = LED_MAP_INIT;

#define LED_PATH	"/sys/class/leds/%s/brightness"
char * gpio_led_pin_value_path(char *name) {
	static char s_pinvalue[128];
	sprintf(s_pinvalue, LED_PATH, name);
	return s_pinvalue;
}

int gpio_led_init(LED *led) {
	int status, ret = 0;
	char *led_value_path = NULL;
	char *pin_name = NULL, *direction_path = NULL;
	int export_fd, direction_fd, success_fd[4], success_fd_index=0;
	int i;

	led_value_path = gpio_led_pin_value_path(led->name);
	status = access(led_value_path, F_OK);
	if (status != 0) {
		// 不存在对应端口
		return 1;
	}
	ret = 0;
	led->led_fd = open(led_value_path, O_WRONLY);
	if (led->led_fd < 0) {
		printf("%s open failed\n", led->name);
		ret = led->led_fd;
		goto led_file_close;
	}

led_file_close:
	for (i = 0; i < 4; i++) {
		if (success_fd[i] != 0) {
			close(success_fd[i]);
		}
	}
	return ret;
}

LED *led_register() {
	int i, status;

	led_list = malloc(sizeof(LED));
	if (led_list == NULL) {
		return NULL;
	}
	
	LED *led = NULL;
	
	INIT_LIST_HEAD(&led_list->list);
	int array_size = sizeof(led_map)/sizeof(struct LED_MAP);
	for (i = 0; i < array_size; i ++) {
		led = malloc(sizeof(LED));
		list_add_tail(&led->list, &led_list->list);
		led->led_name = led_map[i].led_name;
		led->name = led_map[i].name;
		led->blink_type = 0x00;
		status = gpio_led_init(led);
		if (status != 0) {
			printf("%s led init failed\n", led->name);
			return NULL;
		}
	}
	return led_list;
}

LED *get_led(LED_NAME led_name) {
	struct list_head *pos;
	struct list_head *n;

	LED *led_tmp = NULL;

	list_for_each_safe(pos, n, &led_list->list) {
		led_tmp = list_entry(pos, LED, list);
		if (led_tmp->led_name == led_name) {
			return led_tmp;
		}
	}
	return led_tmp;
}

#define led_on(led)		write(led->led_fd, "1", strlen("1"))
#define led_off(led)	write(led->led_fd, "0", strlen("0"))

void led_blink(LED *led) {
	if (led->blink_type & 0x80) {
		led_on(led);
	}
	else {
		led_off(led);
	}
	led->blink_type = (led->blink_type >> 7) | (led->blink_type << 1);
}

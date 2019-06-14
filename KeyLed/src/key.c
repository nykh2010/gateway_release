/*
 * Key.c
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <key.h>
#include <string.h>
#include "sysmonitor.h"

static KEY *key_list;

int reset_key_long_press_handler() {
    // TODO: restore
    return NONE;
}

int reset_key_short_press_handler() {
    return REBOOT;
}

int config_key_long_press_handler() {
    return ENTER_CONFIG;
}

int config_key_short_press_handler() {
    return EXIT_CONFIG;
}

int power_key_long_press_handler() {
    return SLEEP;
}

int power_key_short_press_handler() {
    return SHUT_DOWN;
}

#define KEY_MAP_INIT	{\
							{CONFIG_KEY, 132, config_key_long_press_handler, config_key_short_press_handler}\
						};

const struct KEY_MAP{
	KEY_NAME key_name;
	int pin;
	int (*long_press_handler)();
	int (*short_press_handler)();
} key_map[] = KEY_MAP_INIT;

KEY *key_register() {
	printf("key_register start\n");
	int i, status;
	KEY *key = NULL;
	key_list = (KEY *)malloc(sizeof(KEY));
	if (key_list == NULL) {
		return NULL;
	}
	INIT_LIST_HEAD(&key_list->list);
	int array_size = sizeof(key_map)/sizeof(struct KEY_MAP);
	for (i = 0; i < array_size; i ++) {
		key = malloc(sizeof(KEY));
		list_add_tail(&key->list, &key_list->list);
		key->key_name = key_map[i].key_name;
		key->pin = key_map[i].pin;
		key->short_press_handler = key_map[i].short_press_handler;
		key->long_press_handler = key_map[i].long_press_handler;
		status = gpio_key_init(key);
		if (status < 0) {
			printf("%d init failed\n", key->pin);
			return NULL;
		}
	}
	printf("key_register end\n");
	return key_list;
}

int get_status(KEY *key) {
	int ret, value_fd;
	char s[3] = {0};
	value_fd = open(key->value_path, O_RDONLY);
	ret = read(value_fd, s, 3);
	if (ret < 0) {
		printf("%d pin read failed\n", key->key_name);
	}
	close(value_fd);
	return atoi(&s[0]);
}

void *get_key_event(KEY *key) {
	// 每检测一次250ms
	int new_flag;
	new_flag = get_status(key);
	if (new_flag == PRESS) {
		key->press_time_count ++;
		if (key->press_time_count > 40) {
			key->press_time_count = 0;
			printf("%d pin press invalid\n", key->key_name);
		}
	}
	else {

		if (key->press_time_count > 20) {
			key->press_time_count = 0;
			return key->long_press_handler;
		}
		else if (key->press_time_count > 0) {
			key->press_time_count = 0;
			return key->short_press_handler;
		}
	}
	return NULL;		//没有处理任务
}

char * gpio_key_pin_direction_path(int pin) {
	static char s_pinpath[35];
	sprintf(s_pinpath, "/sys/class/gpio/gpio%d/direction", pin);
	return s_pinpath;
}

//
char * gpio_key_pin_name(int pin) {
	static char s_pinname[5];
	sprintf(s_pinname, "%d", pin);
	return s_pinname;
}

char * gpio_key_pin_value_path(int pin) {
	static char s_pinvalue[35];
	sprintf(s_pinvalue, "/sys/class/gpio/gpio%d/value", pin);
	return s_pinvalue;
}

int gpio_key_init(KEY *key) {
	printf("gpio_key_init start\n");
	int export_fd = 0, unexport_fd = 0, value_fd = 0, direction_fd = 0;
	int ret = 0;
	char *direction_file_path;
	char gpio_dir[35] = {0};
	char *pin_name;
	char *value_path;
	int success_fd[4] = {0};
	int success_fd_index = 0;
	int i;

	if (key == NULL) {
		printf("key is NULL\n");
		return -1;
	}

	export_fd = open("/sys/class/gpio/export", O_WRONLY);
	if (export_fd < 0) {
		printf("open /sys/class/gpio/export failed\n");
		ret = export_fd;
		goto file_close;
	}
	printf("export open success\n");
	success_fd[success_fd_index++] = export_fd;
	unexport_fd = open("/sys/class/gpio/unexport", O_WRONLY);
	if (unexport_fd < 0) {
		printf("open /sys/class/gpio/unexport failed\n");
		ret = unexport_fd;
		goto file_close;
	}
	printf("unexport open success\n");
	success_fd[success_fd_index++] = unexport_fd;

	sprintf(gpio_dir, "/sys/class/gpio/gpio%d", key->pin);
	if (access(gpio_dir, F_OK) != 0) {
		pin_name = gpio_key_pin_name(key->pin);
		ret = write(export_fd, pin_name, strlen(pin_name));		// export
		if (ret < 0) {
			printf("write export failed\n");
			goto file_close;
		}
		printf("write export %s success\n");
	}
	direction_file_path = gpio_key_pin_direction_path(key->pin);
	direction_fd = open(direction_file_path, O_WRONLY);
	if (direction_fd < 0) {
		printf("open %s failed.\n", direction_file_path);
		perror("open direction:");
		ret = direction_fd;
		goto file_close;
	}
	printf("%s open success\n", direction_file_path);
	success_fd[success_fd_index++] = direction_fd;

	ret = write(direction_fd, "in", strlen("in"));
	if (ret < 0) {
		printf("write direction failed\n");
		goto file_close;
	}
	printf("write direction success\n");
	value_path = gpio_key_pin_value_path(key->pin);
	value_fd = open(value_path, O_RDWR);
	if (value_fd < 0) {
		printf("open %s failed\n", value_path);
		ret = value_fd;
		goto file_close;
	}
	success_fd[success_fd_index++] = value_fd;
	printf("open %s success\n", value_path);
	strcpy(key->value_path, value_path);

file_close:
	for (i = 0; i < 4; i++) {
		if (success_fd[i] != 0) {
			close(success_fd[i]);
		}
	}
	printf("gpio_key_init end\n");
	return ret;
}

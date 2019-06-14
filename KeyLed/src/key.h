/*
 * Key.h
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#ifndef SRC_KEY_H_
#define SRC_KEY_H_

#include "mylist.h"

typedef enum {
	RESET_KEY = 0x00,	/* 复位按键 */
	CONFIG_KEY,			/* 配置按键 */
	POWER_KEY,			/* 电源按键 */
	MAX_KEY				/* 最大按键 */
} KEY_NAME;

#define PRESS		0
#define UNPRESS		1

typedef struct{
	int (*long_press_handler)();
	int (*short_press_handler)();

	int (*check_press)();		// 按键检测
	int (*get_status)();		// 获取按键状态

	void *(*get_event)();		// 获取按键处理函数

	int (*gpio_key_init)();	//
	int (*set_pin)(int pin);	//
	char *(*gpio_key_pin_name)();		// 获取按键名称
	char *(*gpio_key_pin_direction_path)();	//方向文件路径
	char *(*gpio_key_pin_value_path)();		//值文件路径

	int pin;
	int status;
	char value_path[35];		// 按键值路径

	int press_time_count;
	int old_flag;

	KEY_NAME key_name;
	struct list_head list;
} KEY;

extern KEY *key_register();
extern void *get_key_event(KEY *key);

#endif /* SRC_KEY_H_ */

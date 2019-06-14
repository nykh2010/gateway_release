/*
 * Led.h
 *
 *  Created on: Jun 11, 2019
 *      Author: xulingfeng
 */

#ifndef SRC_LED_H_
#define SRC_LED_H_
#include "mylist.h"

typedef enum {
	SYSLED,		// 黄色灯，系统运行
	CONNECTLED,	// 绿色灯，服务器连接
	CONFIGLED,	// 绿色灯，配置指示
} LED_NAME;

enum {
	ON = 0xff,
	OFF = 0x00,
	TWINKLE = 0x55
};

typedef struct {
	char blink_type;
	LED_NAME led_name;
	struct list_head list;
	char *name;
	int led_fd;
} LED;

extern void led_blink(LED *led);
extern LED *led_register();
extern LED *get_led(LED_NAME led_name);

#endif /* SRC_LED_H_ */

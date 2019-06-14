/*
 * statusmonitor.c
 *
 *  Created on: Jun 12, 2019
 *      Author: xulingfeng
 */

#include "statusmonitor.h"
#include <stdlib.h>
#include <stdio.h>
#include "sysmonitor.h"

static StatusMonitor *monitor_list;

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

#if 0
/*
 split string with delimiter
*/
static int string_split (const char *str, char *parts[], const char *delimiter) {
  char *pch;
  int i = 0;
  char *copy = NULL, *tmp = NULL;

  copy = strdup(str);
  if (! copy)
    goto bad;

  pch = strtok(copy, delimiter);

  tmp = strdup(pch);
  if (! tmp)
    goto bad;

  parts[i++] = tmp;

  while (pch) {
    pch = strtok(NULL, delimiter);
    if (NULL == pch) break;

    tmp = strdup(pch);
    if (! tmp)
      goto bad;

    parts[i++] = tmp;
  }

  free(copy);
  return i;

 bad:
  free(copy);
  int j = 0;
  for (; j < i; j++)
    free(parts[j]);
  return -1;
}
#endif

static int connect_flag;
static int net_monitor_handler() {
	char command_buf[1024] = {0};
	int connect_flag_tmp = connect_flag;
	// 获取服务器连接端口与IP
	int ret = cmd_system("cat /etc/gateway/dma.ini | cut -f2 -d\"=\"", command_buf, sizeof(command_buf));
	if (ret < 0) {
		return -1;
	}
	// 获取连接状态
	char command[128] = {0};
	sprintf(command, "netstat -ant | grep -E \"(%s)\\s+ESTABLISHED\" | wc -l", command_buf);
	ret = cmd_system(command, command_buf, sizeof(command_buf));
	if (ret < 0) {
		return -1;
	}
	int connect_count = atoi(command_buf);		// 获取连接数
	printf("connect_count:%d\n", connect_count);
	if (connect_count == 0 || connect_count > 1) {
		// 连接数异常
		connect_flag = 0;
	}
	else
		connect_flag = 1;
	if (connect_flag_tmp != connect_flag) {
		if (connect_flag)
			return CONNECT;
		else
			return DISCONNECT;
	}
	return NONE;
}

typedef struct CPU_PACKED {		// CPU状态
	char name[20];
	unsigned int user;			//
	unsigned int nice;
	unsigned int system;
	unsigned int idle;
} CPU_OCCUPY;

static int cal_cpuoccupy(CPU_OCCUPY *o, CPU_OCCUPY *n) {
	unsigned long od, nd;
	unsigned long id, sd;
	int cpu_use = 0;

	od = (unsigned long) (o->user + o->nice + o->system + o->idle);	// 第一次采集
	nd = (unsigned long) (n->user + n->nice + n->system + n->idle);	// 第二次采集

	id = (unsigned long) (n->user - o->user);
	sd = (unsigned long) (n->system - o->system);

	if ((nd-od) != 0)
		cpu_use = (int) ((sd+id)*100)/(nd-od);
	else
		cpu_use = 0;
	return cpu_use;
}

static void get_cpuoccupy(CPU_OCCUPY *cpust) {
	FILE *fd;
	int n;
	char buff[256];
	CPU_OCCUPY *cpu_occupy;
	cpu_occupy = cpust;

	fd = fopen("/proc/stat", "r");
	fgets(buff, sizeof(buff), fd);
	sscanf(buff, "%s %u %u %u %u", cpu_occupy->name, &cpu_occupy->user, &cpu_occupy->nice, &cpu_occupy->system, &cpu_occupy->idle);
	fclose(fd);
}

static int sys_error_flag;

static int cpu_usage_monitor_handler() {
	CPU_OCCUPY cpu_stat1;
	CPU_OCCUPY cpu_stat2;
	int cpu;
#if 0
	get_cpuoccupy((CPU_OCCUPY *)&cpu_stat1);
	get_cpuoccupy((CPU_OCCUPY *)&cpu_stat2);
	cpu = cal_cpuoccupy(&cpu_stat1, &cpu_stat2);
#endif
	int ret;
	char command_buf[32] = {0};
	ret = cmd_system("top -n 1 | awk \"NR==2\" | awk '{print $2}' | cut -f1 -d\"\%\"", command_buf, sizeof(command_buf));
	cpu = atoi(command_buf);
	printf("cpu usage: %d. \n", cpu);
	int old_error_flag = sys_error_flag;

	if (cpu > 80) {
		sys_error_flag |= 0x01;
	}
	else {
		sys_error_flag &= ~0x01;
	}
	if (sys_error_flag != old_error_flag) {
		if (sys_error_flag) 
			return ERROR;
		else 
			return CLR_ERROR;
	}
	return NONE;
}

static int mem_usage_monitor_handler() {
	char command_buf[1024] = {0};
	int ret = 0;
	long total_mem, mem_used;
	long mem;

	memset(command_buf, 0, sizeof(command_buf));
	ret = cmd_system("free | grep Mem | awk '{print $2,$3}'", command_buf, sizeof(command_buf));
	if (ret < 0) {
		return -1;
	}
	sscanf(command_buf, "%ld %ld", &total_mem, &mem_used);
	mem = mem_used * 100 / total_mem;
	printf("mem usage: %d\n", mem);
	int old_error_flag = sys_error_flag;

	if (mem > 90) {
		sys_error_flag |= 0x02;
	}
	else {
		sys_error_flag &= ~0x02;
	}
	if (sys_error_flag != old_error_flag) {
		if (sys_error_flag) 
			return ERROR;
		else 
			return CLR_ERROR;
	}
	return NONE;
}

static int flash_usage_monitor() {
	return NONE;
}

static int fatal_error_flag;
static int process_monitor_handler() {
	char command_buf[128] = {0};
	int process_count;
	int fatal_error_flag_tmp = fatal_error_flag;
	cmd_system("ps | grep dma.monitor | grep -v grep | wc -l", command_buf, sizeof(command_buf));
	process_count = atoi(command_buf);
	if (process_count == 0 || process_count > 1)
		fatal_error_flag = 1;
	else
		fatal_error_flag = 0;
	if (fatal_error_flag_tmp != fatal_error_flag) {
		if (fatal_error_flag)
			return FATAL_ERROR;
		else
			return CLR_FATAL_ERROR;
	}
	return NONE;
}

#define MONITOR_MAP_INIT	{\
								{NET_MONITOR, net_monitor_handler},\
								{CPU_USAGE_MONITOR, cpu_usage_monitor_handler},\
								{MEM_USAGE_MONITOR, mem_usage_monitor_handler},\
								{FLASH_USAGE_MONITOR, flash_usage_monitor},\
								{PROCESS_MONITOR, process_monitor_handler}\
							}

const struct MONITOR_MAP{
	MONITOR_NAME monitor_name;
	int (*monitor_handler)();
} monitor_map[] = MONITOR_MAP_INIT;

StatusMonitor *status_monitor_register() {
	int i;

	monitor_list = malloc(sizeof(StatusMonitor));
	if (monitor_list == NULL) {
		return NULL;
	}

	INIT_LIST_HEAD(&monitor_list->list);
	int array_size = sizeof(monitor_map)/sizeof(struct MONITOR_MAP);
	StatusMonitor *monitor = NULL;

	for (i = 0; i < array_size; i++) {
		monitor = malloc(sizeof(StatusMonitor));
		list_add_tail(&monitor->list, &monitor_list->list);
		monitor->monitor_name = monitor_map[i].monitor_name;
		monitor->monitor_handler = monitor_map[i].monitor_handler;
	}

	return monitor_list;
}


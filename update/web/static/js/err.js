//====================================err==========================================
if (!igd) var igd = new Object();

igd.err = {
    _default: "参数设置失败!",
	"-1":"不能拉黑当前使用设备到黑名单！",
    0: "设置成功",
    1: "数据发生错误",
    2: "数据输入不完整",
    3: "IP地址有错",
    4: "掩码地址有错",
    5: "网关地址有错",
    6: "IP地址与掩码不匹配",
    7: "起始IP大于结束IP",
    8: "设置时分配内存失败",
    9: "MAC地址有错",
    10: "端口范围应设为1-65535",
    11: "设置失败",
    12: "输入的数据超过最大值",
    13: "数字错误",
    14: "条目已添加满",
    15: "两次输入的密码不匹配",
    16: "输入的数据长度过长",
    17: "DNS地址有错",
    18: "时间设置有错",
    19: "条目不存在",
    20: "服务器IP地址有错",
    21: "邮箱地址有误",
    22: "条目已存在",
    23: "IP不在地址池内",
    24: "WAN MTU 值错误",
    25: "名称已存在",
    26: "端口范围在已存在列表内",
    27: "该条目在黑名单中已存在",
    28: "该条目在白名单中已存在",
    29: "key错误",
    30: "PIN码有错",
    31: "密码长度超出限制",
    32: "WEP和WPA,WPA2不能共存",
    33: "WEP current key index大于等于4, 合法值为0-3 ",
    34: "无法找到SSID",
    35: "账户到期",
    36: "用户名或密码错误",
    37: "地址池错误",
    38: "文件不存在",
    39: "用户名包含无效字符",
    40: "密码包含无效字符",
    41: "接口已经绑定",
    42: "操作被禁止",
    43: "该用户组的规则已经设置",
    44: "无权限",
    45: "文件类型错误",
    46: "新密码不能与旧密码相同，请重新输入",
    47: "原密码输入错误",
    48: "创建会话失败",
    49: "已到最大会话数",
    50: "生成token失败",
    51: "登录用户过多数",
    52: "登录次数过多",
    53: "接口不存在",
    54: "操作太频繁",
    55: "文件太大",
    56: "程序已经在运行",
    57: "操作失败",
    58: "action错误",
    59: "数据错误",
    60: "未知错误",
    61: "path为空",
    62: "参数为空",
    63: "空间不足",
    64: "文件不存在",
    65: "目录不存在",
    66: "目标不存在",
    67: "目标已存在",
    68: "samba未支持",
    69: "上传文件大小为空",
    70: "文件类型错误",
    71: "文件创建时间为空"	,
    72: "外设不存在",
    73: "外设不可用",
    74: "获取用户对应路径失败"	,
    75: "获取云盘备份路径失败",
    76: "未绑定手机",
    77: "用户未认证",
    78: "用户认证中",
    79: "用户认证失败",
	100: "规则冲突",
	101: "黑名单条目数超出限制",
	102: "不能拉黑当前使用设备到黑名单",
	103: "设备不存在",
	256: "磁盘空间不足",
	257: "安装失败，请稍后重试",
	258: "安装失败，请稍后重试",
	259: "安装失败，请稍后重试",
	260: "安装失败，请稍后重试",
	271: "USB移动磁盘不可用，请检查",
	291: "安装失败，请稍后重试",
	292: "安装失败，请稍后重试",
	295: "安装失败，请稍后重试",
	296: "安装失败，请稍后重试",
	297: "安装失败，请稍后重试"
};

igd.make_err_msg = function (key) {
    var key_code = key.err_no;
    if (!igd.err[key_code]) {
        return igd.err._default;
    }
    var str = igd.err[key_code];
    return str;
}
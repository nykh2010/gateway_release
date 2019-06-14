#ifndef _MY_LIST_H_
#define _MY_LIST_H_

struct list_head {
    struct list_head *next, *prev;
};

#define list_entry(ptr, type, member) container_of(ptr, type, member)

#define offsetof(TYPE, MEMBER) ((size_t)& ((TYPE *)0)->MEMBER)  

#define container_of(ptr, type, member) (type*)((char *)ptr - offsetof(type,member))

#define list_for_each(pos, head) \
    for (pos = (head)->next; pos != (head); \
        pos = pos->next)

#define list_for_each_safe(pos, n, head)  \
	for (pos = (head)->next, n = pos->next; pos != (head); \
		pos = n, n = pos->next)

#define LIST_HEAD_INIT(name) { &(name), &(name) }                 //prev和next都指向自己

//prev和next都指向自己
void INIT_LIST_HEAD(struct list_head *list);

//new在编译器里被认作关键字   原代码是new 被改为l_new
//l_new 是要被插入的节点
//prev 是插入点前面的一个节点
//next 是插入点后面的一个节点
void __list_add(struct list_head *l_new,\
                  struct list_head *prev,\
                  struct list_head *next);

//这个函数对上面简化 新加入的节点在head和head->next之间  也就是head之后
void list_add(struct list_head *l_new, struct list_head *head);

//这个函数对上面简化 新加入的节点在head->prev和head之间  也就是head之前
void list_add_tail(struct list_head *l_new, struct list_head *head);
//删除一个双向列表中的一个节点 删除节点在prev和next之间
void __list_del(struct list_head *prev, struct list_head *next);

//从列表中删除entry节点，这个函数是对上面函数的简化
//entry->next = LIST_POISON1;
//entry->prev = LIST_POISON2;
void list_del(struct list_head *entry);

//跟上面函数功能一样，将entry中队列里删除后，初始化entry为队列头
void list_del_init(struct list_head *entry);
//判断list是不是最后一个节点
//head节点是队列的第一个节点
//return list->next == head  或者 return head->prev == list一样
int list_is_last(const struct list_head *list,\
                const struct list_head *head);
//列表是不是为空
//head节点 是队列的头节点
int list_empty(const struct list_head *head);
#endif


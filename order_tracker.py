import random

# In-memory variable to track days with no orders
days_without_orders = 0

# Messages
MSG_LESS_THAN_WEEK = "يلا يا شباب أبدأو ضيفو طلابتكم"
MSG_OTHERWISE_EVERY_FEW_DAYS = "فينكم يا شباب... اشتقنا لطلباتكم الحلوه"

# Internal toggle for randomized message sending
_last_msg_sent_day = -1


def get_order_message():
    global _last_msg_sent_day

    if days_without_orders < 7:
        return MSG_LESS_THAN_WEEK
    elif days_without_orders >= 7:
        if _last_msg_sent_day == -1 or (days_without_orders - _last_msg_sent_day) >= random.randint(3, 5):
            _last_msg_sent_day = days_without_orders
            return MSG_OTHERWISE_EVERY_FEW_DAYS
    return None


def reset_days_without_orders():
    global days_without_orders, _last_msg_sent_day
    days_without_orders = 0
    _last_msg_sent_day = -1


# Optionally: simulate day passing (for testing purposes)
def increment_day():
    global days_without_orders
    days_without_orders += 1

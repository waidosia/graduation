import time

import network
import ujson
import machine

import const
from simple import MQTTClient

motor = machine.Pin(23, machine.Pin.OUT)


client = MQTTClient(client_id=const.CLIENT_ID,
                    server=const.SERVER, port=const.PORT)



def Readlight():
    # 获取光照强度
    adc=machine.ADC(0)
    value=adc.read()
    # 积分滤波
    value=0.3*value + 0.7*adc.read() ;
    # 0-1024 等比划分为百分比
    return round(value*100/1024)
    


def do_connect():
    # 持续连接wifi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while True:
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(const.SSID, const.PASSWORD)
            time.sleep(5)
        if wlan.isconnected():
            print('network config:', wlan.ifconfig())
            break


def sub_cb(topic, msg):
    # 控制电机转动
    if topic == b'motor':
        if msg[0] == 49:
            motor.value(1)
        else:
            motor.value(0)


def qqt(l):
    # 发布主题为Light的消息
    data = {"Light": {"light": l}}
    d = ujson.dumps(data)
    client.publish('Light', d)


def main():
    # 主函数
    do_connect()
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(b"motor")
    start_time = time.time()
    while True:
        try:
            if time.time() - start_time == 15:
                l = Readlight()
                qqt(l)
                start_time = time.time()
        except Exception as e:
            print('exception', e)
        client.check_msg()
    client.disconnect()


if __name__ == '__main__':
    main()

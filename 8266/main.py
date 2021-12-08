import time

import dht
import network
import ujson
from machine import Pin

import const
from simple import MQTTClient

Green = Pin(13, Pin.OUT)
Blue = Pin(12, Pin.OUT)
Red = Pin(15, Pin.OUT)
client = MQTTClient(client_id=const.CLIENT_ID,
                    server=const.SERVER, port=const.PORT)



def ReadTemHum():
    # 获取温湿度的值,并返回温湿度
    d = dht.DHT11(Pin(14))
    d.measure()
    tem = d.temperature()
    hum = d.humidity()
    return tem, hum


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
    # 获取灯光信号
    if topic == b'led':
        if msg[0] == 49:
            Red.on()
        else:
            Red.off()

        if msg[1] == 49:
            Green.on()
        else:
            Green.off()

        if msg[2] == 49:
            Blue.on()
        else:
            Blue.off()


def qqt(tem, hum):
    # 发布主题为DHT的消息
    data = {"DHT11": {"tem": tem, "hum": hum}}
    d = ujson.dumps(data)
    client.publish('DHT', d)


def main():
    # 主函数
    do_connect()
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(b"led")
    start_time = time.time()
    while True:
        try:
            if time.time() - start_time == 30:
                tem,hum = ReadTemHum()
                qqt(tem,hum)
                start_time = time.time()
        except Exception as e:
            print('exception', e)
        client.check_msg()
    client.disconnect()


if __name__ == '__main__':
    main()

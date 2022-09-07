import json
import time

import base58
import requests
from openpyxl import Workbook


def current_time_millis() -> int:
    """返回当前时间的毫秒值

    波场的时间戳以毫秒为单位
    """
    return int(time.time()) * 1000


def format_time_millis(timestamp) -> str:
    """格式化时间戳

    时间戳以 ms 为单位
    """
    localtime = time.localtime(timestamp / 1000)
    return time.strftime("%Y-%m-%d %H:%M:%S", localtime)


def decode_hex_address(hex_address: str) -> str:
    """
    decode hex address to tron address
    :param hex_address: hex address eg: 0x22b5aabbf024e83a57d5854e2b51540ce20354ea
    :type hex_address: str
    :return: tron address eg: TD8jc2AKymtkbPwdkJUURbhztPjmbrTaXd
    :rtype: str
    """
    check_address = hex_address.replace('0x', '41', 1)
    return base58.b58encode_check(bytearray.fromhex(check_address)).decode(encoding="UTF-8")


class NDexEvidenceDumper:
    def __init__(self):
        # NDex 1.0
        self.contract_address = "TJztzjR5t7e9BrWTaCfQWGiyxMw1U5ZUaq"
        # NDex 2.0
        # self.contract_address = "TCvkvQUDfb1UzPHzTzCbjBHTUrEX6Cvaw5"
        print("NDex Contract: {}".format(self.contract_address))
        self.event_url = "https://api.trongrid.io/v1/contracts/{}/events".format(self.contract_address)
        print("Event Url: {}".format(self.event_url))
        self.wb = Workbook()

    def start(self):
        ws = self.wb.active
        ws.append(["区块高度", "交易哈希", "用户地址", "上线地址", "交易时间"])

        query_count = 0
        event_count = 0
        last_block_timestamp_ms = 0
        # NDex 1.0
        params = {"event_name": "Upline", "only_unconfirmed": "false", "only_confirmed": "true",
                  "min_block_timestamp": "{}".format(last_block_timestamp_ms),
                  "max_block_timestamp": "{}".format(current_time_millis()),
                  "order_by": "block_timestamp,asc", "limit": "200"}
        # NDex 2.0
        # params = {"event_name": "StakeLP", "only_unconfirmed": "false", "only_confirmed": "true",
        #           "min_block_timestamp": "{}".format(last_block_timestamp_ms),
        #           "max_block_timestamp": "{}".format(current_time_millis()),
        #           "order_by": "block_timestamp,asc", "limit": "200"}

        retry_count = 0
        while True:
            result = self.request(self.event_url, params=params)
            events = result.get("data", None)
            if events is None or len(events) == 0:
                if result['error'] == "Exceeds the maximum limit, please change your query time range":
                    # 修改查询时间范围（默认查询 1w 条数据后就需要修改一次）
                    params["min_block_timestamp"] = "{}".format(last_block_timestamp_ms + 1)
                    params["max_block_timestamp"] = "{}".format(current_time_millis())
                    # 清除翻页参数
                    params["fingerprint"] = ""
                    continue

                # 重试 3 次
                retry_count += 1
                if retry_count > 3:
                    print("result no data {}".format(result))
                    break
                continue

            retry_count = 0
            query_count += 1
            event_count += len(events)
            print("查询次数：{}".format(query_count))
            print("事件总数：{}".format(event_count))

            # 分析注册事件
            for event in events:
                block_number = event['block_number']
                transaction_id = event['transaction_id']
                event_params = event['result']

                # NDex 1.0
                addr = decode_hex_address(event_params['addr'])
                upline = decode_hex_address(event_params['upline'])

                # NDex 2.0
                # addr = decode_hex_address(event_params['sender'])
                # upline = decode_hex_address(event_params['upline'])

                last_block_timestamp_ms = event['block_timestamp']
                block_time = format_time_millis(last_block_timestamp_ms)
                line = [block_number, transaction_id, addr, upline, block_time]
                ws.append(line)
                print(line)
                print(event)

            # 添加翻页参数
            meta = result['meta']
            fingerprint = meta.get("fingerprint", None)
            if fingerprint is not None:
                params["fingerprint"] = fingerprint
                continue
            break

        print("分析完成！")

    @staticmethod
    def request(url, params) -> dict:
        seconds = 3
        while True:
            try:
                response = requests.get(url, params=params)
            except Exception as e:
                print(e)
                print("捕获异常，等待 {} 秒后继续尝试请求！".format(seconds))
                time.sleep(seconds)
                continue
            try:
                result = json.loads(response.text)
                return result
            except Exception as e:
                print(e)
                print("response.text: {}".format(response.text))
                continue


def main():
    dumper = NDexEvidenceDumper()
    try:
        dumper.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt...")
    dumper.wb.save("ndex.xlsx")
    # dumper.wb.save("ndex.xlsx")


if __name__ == '__main__':
    main()

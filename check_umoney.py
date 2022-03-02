import requests
from config import Config

cfg = Config()

from yoomoney.exceptions import (
    IllegalParamType,
    IllegalParamStartRecord,
    IllegalParamRecords,
    IllegalParamLabel,
    IllegalParamFromDate,
    IllegalParamTillDate,
    TechnicalError
    )

class Check_transaction_umoney:
    def __init__(self):
        self.base_url = "https://yoomoney.ru/api/"
        self.method = "operation-history"
        self.token = cfg.umoney_token

    async def request(self, label: str):
        access_token = str(self.token)
        url = self.base_url + self.method
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {}
        payload["label"] = label
        response = requests.request("POST", url, headers=headers, data=payload)
        answer = await self.return_status(response.json())
        return answer

    async def return_status(self, data):
        if "error" in data:
            if data["error"] == "illegal_param_type":
                raise IllegalParamType()
            elif data["error"] == "illegal_param_start_record":
                raise IllegalParamStartRecord()
            elif data["error"] == "illegal_param_records":
                raise IllegalParamRecords()
            elif data["error"] == "illegal_param_label":
                raise IllegalParamLabel()
            elif data["error"] == "illegal_param_from":
                raise IllegalParamFromDate()
            elif data["error"] == "illegal_param_till":
                raise IllegalParamTillDate()
            else:
                raise TechnicalError()

        operation_data = data["operations"]
        status = None
        if not operation_data:
            return None
        if "status" in operation_data[0]:
            status = operation_data[0]["status"]
        return status

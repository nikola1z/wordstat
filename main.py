import asyncio
import json
from typing import List

import aiohttp

from enums import WordstatMethod, FieldName
from helpers import build_body
from settings import WORDSTAT_SANDBOX_URL, LOCALE, TIMEOUT, WORDSTAT_QUEUE_LIMIT

words_list = [["сноуборд"],
              ["аптека"], ]

reports_to_process = []
ready_reports = []


class WordstatClient:
    def __init__(self, session):
        self.session = session

    async def _fetch(self, body):
        async with self.session.post(WORDSTAT_SANDBOX_URL,
                                     data=json.dumps(body, ensure_ascii=False).encode('utf8')) as response:
            return await response.json()

    async def get_reports_list(self):
        body = build_body(WordstatMethod.GetWordstatReportList.value)
        return await self._fetch(body)

    async def create_new_report(self, words: List[str]):
        param = {
            "Phrases": words,
            "GeoID": []
        }
        body = build_body(WordstatMethod.CreateNewWordstatReport.value, param, locale=LOCALE)
        return await self._fetch(body)

    async def get_report(self, number):
        body = build_body(WordstatMethod.GetWordstatReport.value, number)
        return await self._fetch(body)

    async def delete_report(self, number):
        body = build_body(WordstatMethod.DeleteWordstatReport.value, number)
        return await self._fetch(body)


async def check_reports(client: WordstatClient):
    while True:
        await asyncio.sleep(TIMEOUT)
        result = await client.get_reports_list()

        if result.get('data'):
            reports = result['data']
            for report in reports:
                if report[FieldName.StatusReport.value] == 'Done':
                    await get_report(client, report[FieldName.ReportID.value])

        elif words_list:
            for _ in range(WORDSTAT_QUEUE_LIMIT):
                try:
                    words = words_list.pop(0)
                    await asyncio.ensure_future(client.create_new_report(words))
                except IndexError:
                    pass
        else:
            if not (words_list and reports_to_process):
                break


async def get_report(client: WordstatClient, report_number: int):
    result = await client.get_report(report_number)
    if result.get('data'):
        ready_reports.append(result)
        delete_result = await client.delete_report(report_number)
        if delete_result.get('data') and delete_result['data'] == 1:
            try:
                reports_to_process.remove(report_number)
            except ValueError:
                pass


async def main():
    async with aiohttp.ClientSession() as session:
        client = WordstatClient(session)
        for _ in range(WORDSTAT_QUEUE_LIMIT):
            result = await client.create_new_report(words=words_list.pop(0))
            if result.get('data'):
                reports_to_process.append(result['data'])
        await asyncio.ensure_future(check_reports(client))

        with open('results.json', 'w') as fp:
            json.dump(ready_reports, fp)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

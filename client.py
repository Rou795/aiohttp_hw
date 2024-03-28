import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        # Тесты для модели User

        # async with session.post("http://127.0.0.1:8080/user",
        #                         json={'name': 'user_1', 'second_name': 'second_name_1', 'mail': 'jon.79555@gmail.com', 'password': 'password_1'}
        #                         ) as response:
        #
        #     print(response.status)
        #     print(await response.text())

        async with session.post("http://127.0.0.1:8080/user",
                                json={'name': 'user_1', 'second_name': 'second_name_1',
                                      'mail': 'jon.79555@gmail.com', 'password': 'password_1'}
                                ) as response:
            print(response.status)
            print(await response.text())

        # async with session.patch("http://127.0.0.1:8080/user/2",
        #
        #                          json={'name': 'new_user_name'}) as response:
        #     print(response.status)
        #     print(await response.text())
        #
        # async with session.patch("http://127.0.0.1:8080/user/2",
        #
        #                          json={'name': 'new_user_name'},
        #                          headers={'user_id': '1', 'password': 'password_1'}) as response:
        #     print(response.status)
        #     print(await response.text())
        #
        # async with session.get("http://127.0.0.1:8080/user/1") as response:
        #     print(response.status)
        #     print(await response.text())
        #
        # async with session.delete("http://127.0.0.1:8080/user/1") as response:
        #     print(response.status)
        #     print(await response.text())
        #
        # async with session.delete("http://127.0.0.1:8080/user/1",
        #                           headers={'user_id': '1', 'password': 'password_1'}) as response:
        #     print(response.status)
        #     print(await response.text())
        #

        # Тесты для модели Ad

        async with session.post("http://127.0.0.1:8080/ad",
                                json={"title": "title_1", "description": "description ad_1"}
                                ) as response:
            print(response.status)
            print(await response.text())

        async with session.post("http://127.0.0.1:8080/ad",
                                json={"title": "title_1", "description": "description ad_1", 'user_id': '1'},
                                headers={'user_id': '1', 'password': 'password_1'},
                                ) as response:
            print(response.status)
            print(await response.text())

        async with session.patch("http://127.0.0.1:8080/ad/2",

                                 json={"title": "new_title_1"}) as response:
            print(response.status)
            print(await response.text())

        async with session.patch("http://127.0.0.1:8080/ad/2",

                                 json={"title": "new_title_1"},
                                 headers={'user_id': '1', 'password': 'password_1'}) as response:
            print(response.status)
            print(await response.text())

        async with session.get("http://127.0.0.1:8080/ad/1") as response:
            print(response.status)
            print(await response.text())

        async with session.get("http://127.0.0.1:8080/ad/1",
                               headers={'user_id': '1', 'password': 'password_1'}) as response:
            print(response.status)
            print(await response.text())

        async with session.delete("http://127.0.0.1:8080/ad/1",
                                  ) as response:
            print(response.status)
            print(await response.text())

        async with session.delete("http://127.0.0.1:8080/ad/1",
                                  headers={'user_id': '1', 'password': 'password_1'}) as response:
            print(response.status)
            print(await response.text())


asyncio.run(main())

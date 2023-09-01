from asyncio import run
from aiohttp import ClientSession


async def main():
## Post user
#     async with ClientSession() as session:
#         response = await session.post('http://0.0.0.0:8080/user/', json={
#             'name': 'user_3',
#             'email': 'user_3@yandex.ru',
#             'password': '1234587'
#         })
#         print(response.status)
#         print(await response.json())

# # Get user
#     async with ClientSession() as session:
#         response = await session.get('http://0.0.0.0:8080/user/5')
#         print(response.status)
#         print(await response.json())

# # Patch user
#     async with ClientSession() as session:
#         response = await session.patch('http://0.0.0.0:8080/user/4', json={
#                 'name': 're_user_2',
#                 'email': 're_user_2@yandex.ru'
#             })
#         print(response.status)
#         print(await response.json())

# Delete user
#     async with ClientSession() as session:
#         response = await session.delete('http://0.0.0.0:8080/user/99')
#         print(response.status)
#         print(await response.json())

# # Post article
#     async with ClientSession() as session:
#         response = await session.post('http://0.0.0.0:8080/article/', json={
#             'topic': 'topic_2',
#             'description': 'new_topic2',
#             'user_id': 5
#         })
#         print(response.status)
#         print(await response.json())

# # Get article
#         async with ClientSession() as session:
#             response = await session.get('http://0.0.0.0:8080/article/8')
#             print(response.status)
#             print(await response.json())
#
# # Delete article
#         async with ClientSession() as session:
#             response = await session.delete('http://0.0.0.0:8080/article/8')
#             print(response.status)
#             print(await response.json())


run(main())
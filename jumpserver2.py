import os
import asyncio
import aioconsole
import websockets
import requests
import json
 
url = "/api/v1/authentication/connection-token/?user-only=1"
 
 
def get_celery_task_log_path(task_id):
    task_id = str(task_id)
    rel_path = os.path.join(task_id[0], task_id[1], task_id + ".log")
    path = os.path.join("/opt/jumpserver/", rel_path)
    return path
 
 
async def send_msg(websocket, _text):
    if _text == "exit":
        print(f'you have enter "exit", goodbye')
        await websocket.close(reason="user exit")
        return False
    await websocket.send(_text)
 
 
async def send_loop(ws, session_id):
    while True:
        cmdline = await aioconsole.ainput()
        await send_msg(
            ws,
            json.dumps(
                {"id": session_id, "type": "TERMINAL_DATA", "data": cmdline + "\n"}
            ),
        )
 
 
async def recv_loop(ws):
    while True:
        recv_text = await ws.recv()
        ret = json.loads(recv_text)
        if ret.get("type", "TERMINAL_DATA"):
            await aioconsole.aprint(ret["data"], end="")
 
 
# 客户端主逻辑
async def main_logic():
    print("#######start ws")
    async with websockets.connect(target) as client:
        recv_text = await client.recv()
        print(f"{recv_text}")
        session_id = json.loads(recv_text)["id"]
        print("get ws id:" + session_id)
        print("###############")
        print("init ws")
        print("###############")
        inittext = json.dumps(
            {
                "id": session_id,
                "type": "TERMINAL_INIT",
                "data": '{"cols":164,"rows":17}',
            }
        )
        await send_msg(client, inittext)
        await asyncio.gather(recv_loop(client), send_loop(client, session_id))
 
 
if __name__ == "__main__":
    host = "http://192.168.111.162:8080"
    cmd = "whoami"
    if host[-1] == "/":
        host = host[:-1]
    print(host)
    data = {"user": "aff77afe-820c-45c4-b1de-bcbcd320fbeb", "asset": "ae2fd918-ec9b-4900-b864-36d60b46f51a",
            "system_user": "715e93c0-8a50-4318-8310-4ffd5ae88abc"}
    print("##################")
    print("get token url:%s" % (host + url,))
    print("##################")
    res = requests.post(host + url, json=data)
    token = res.json()["token"]
    print("token:%s", (token,))
    print("##################")
    target = (
        "ws://" + host.replace("http://", "") + "/koko/ws/token/?target_id=" + token
    )
    print("target ws:%s" % (target,))
    asyncio.get_event_loop().run_until_complete(main_logic())
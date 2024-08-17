import logging
from urllib.parse import parse_qs
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import jwt
import httpx
import os
import json


DT_CLIENT_ID = os.environ.get('DT_CLIENT_ID')
DT_CLIENT_SECRET = os.environ.get('DT_CLIENT_SECRET')
GRAFFA_ORGANIZATIONS = os.environ.get('GRAFFA_ORGANIZATIONS')


app = FastAPI()


logging.basicConfig(level=logging.INFO, format='%(levelname)s: \t%(message)s', encoding='utf-8')


@app.get("/dingtalk/oauth")
async def dingtalk_oauth(redirect_uri, response_type, client_id, scope, state):
    return RedirectResponse(
        url=f"https://login.dingtalk.com/oauth2/auth?"
            f"redirect_uri={redirect_uri}"
            f"&response_type={response_type}"
            f"&client_id={client_id}"
            f"&scope={scope}"
            f"&state={state}"
            f"&prompt=consent",
        status_code=302)


@app.post("/dingtalk/token")
async def dingtalk_token(request: Request):
    body: bytes = await request.body()
    params: dict = parse_qs(body.decode('utf-8'))
    code = params.get('code', [None])[0]
    client_id = params.get('client_id', [DT_CLIENT_ID])[0]
    client_secret = params.get('client_secret', [DT_CLIENT_SECRET])[0]
    grant_type = params.get('grant_type', [None])[0]

    if grant_type == 'refresh_token':
        logging.info(F"用户退出登陆。")
        return

    user_access = httpx.post(
        "https://api.dingtalk.com/v1.0/oauth2/userAccessToken",
        json={"clientId": client_id, "clientSecret": client_secret, "code": code, "grantType": grant_type}
    ).json()

    user_access_token = user_access.get('accessToken')
    user_token_expirein = user_access.get('expireIn')
    user_refresh_token = user_access.get('refreshToken')

    unionid = httpx.get(
        "https://api.dingtalk.com/v1.0/contact/users/me",
        headers={"x-acs-dingtalk-access-token": user_access_token}
    ).json().get('unionId')

    user_name, user_token = UserToken(unionid).get()

    if user_token is None:
        app_access_token = httpx.post(
            "https://api.dingtalk.com/v1.0/oauth2/accessToken",
            json={"appKey": client_id, "appSecret": client_secret}
        ).json().get('accessToken')
        userid = httpx.post(
            f"https://oapi.dingtalk.com/topapi/user/getbyunionid",
            params={"access_token": app_access_token},
            json={"unionid": unionid}
        ).json().get('result', {}).get('userid')
        userinfo = httpx.post(
            f"https://oapi.dingtalk.com/topapi/v2/user/get",
            params={"access_token": app_access_token},
            json={"userid": userid}
        ).json().get('result', {})
        user_name = userinfo.get('name')
        user_token: str = jwt.encode(
            {
                'sub': user_name,
                'uid': user_name,
                'name': user_name,
                'login': user_name,
                'email': user_name,
                'organizations': [GRAFFA_ORGANIZATIONS],
                'groups': [GRAFFA_ORGANIZATIONS],
                'role': 'Viewer'
            },
            'secret',
            'HS256'
        )
        UserToken(unionid).set(user_name, user_token)

    logging.info(F"用户 {user_name} 正在登陆。")

    return {
        'access_token': user_token,
        'id_token': user_token,
        'token_type': 'Bearer',
        'expiry_in': user_token_expirein,
        'refresh_token': user_refresh_token
    }


@app.get("/dingtalk/userinfo")
async def dingtalk_userinfo(request: Request):
    token = request.headers.get('Authorization').split(' ')[1]
    payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    return payload


class UserToken:
    def __init__(self, unionid, file_path='user/userinfo.json'):
        self.file_path = file_path
        self.unionid = unionid

    def read_json(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    # 写入 JSON 文件
    def write_json(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    # 插入或更新键值对
    def set(self, name, token):
        data = self.read_json()
        data[self.unionid] = {"name": name, "token": token}
        self.write_json(data)

    # 获取值
    def get(self):
        data = self.read_json().get(self.unionid, {})
        return data.get('name'), data.get('token')

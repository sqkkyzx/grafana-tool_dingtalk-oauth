# grafana-tool_dingtalk-oauth

用于钉钉登录 Grafana ，解决Grafna的OAuth与钉钉不兼容的问题。
Grafana 内的昵称、用户名、邮箱等都将被设置为钉钉组织通讯录中的姓名而非昵称、邮箱。

## 使用

1. 在[钉钉开放平台](https://open-dev.dingtalk.com/fe/app)中创建应用
2. 在应用的**凭证与基础信息**页面取得拿到应用的 `client_id` 和 `client_secret`
3. 在**权限管理**页面，对 `个人权限` `通讯录管理` `身份验证` `获取凭证` 进行授权
4. 使用 docker-compose 或者 docker 部署，需要确保能够公网访问
5. 更改 Grafana 配置

### docker-compose.yaml 参考

需要正确填写环境变量。

```yaml
  grafana-tool_dingtalk-oauth:
    image: sqkkyzx/grafana-tool_dingtalk-oauth:latest
    restart: always
    ports:
      - '8080:8080'
    environment:
      - TZ=Asia/Shanghai
      - DT_CLIENT_ID=              # 应用的 client_id
      - DT_CLIENT_SECRET=          # 应用的 client_secret
      - GRAFFA_ORGANIZATIONS=      # 组织名，但其实没有实质性作用
```

### grafana 配置参考

这里给出的是容器部署 grafana 时，传入的环境变量

```yaml
GF_AUTH_GENERIC_OAUTH_ENABLED: true             # 启用
GF_AUTH_GENERIC_OAUTH_NAME: DingTalk            # 显示的登录身份源名称
GF_AUTH_GENERIC_OAUTH_CLIENT_ID:                # 应用的 client_id
GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET:            # 应用的 client_secret

# 以下三行需要替换{your-domain}为你自己的域名
GF_AUTH_GENERIC_OAUTH_AUTH_URL: https://{your-domain}/dingtalk/oauth
GF_AUTH_GENERIC_OAUTH_TOKEN_URL: https://{your-domain}/dingtalk/token
GF_AUTH_GENERIC_OAUTH_API_URL: https://{your-domain}/dingtalk/userinfo

GF_AUTH_GENERIC_OAUTH_SCOPES: openid
GF_AUTH_GENERIC_OAUTH_ALLOW_SIGN_UP: true       # 允许自动注册
GF_AUTH_GENERIC_OAUTH_SKIP_ORG_ROLE_SYNC: true  # 跳过组织角色同步
GF_AUTH_GENERIC_OAUTH_USE_PKCE: false
```
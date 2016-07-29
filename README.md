# auth_oauth_extended

for qq/weixin/weibo authorization and login into Odoo

provider | authorize url | validation url | user detail url | scope
--------|-------------|-----------|---------|-----
qq | https://graph.qq.com/oauth2.0/authorize | https://graph.qq.com/oauth2.0/me | https://graph.qq.com/oauth2.0/get_user_info | userinfo
dingtalk | https://oapi.dingtalk.com/connect/oauth2/sns_authorize |  https://oapi.dingtalk.com/sns/get_sns_token  | https://oapi.dingtalk.com/sns/getuserinfo | snsapi_login



**comment**

 for qq oauth provider, need to fix controller to remove '+' from the returned json like this.

 ```
/auth_oauth/signin?access_token=CC75562316165BAC74675C1853121E85&expires_in=7776000&state=%7B%22p%22%3A%2B12%2C%2B%22r%22%3A%2B%22http%253A%252F%252Fo.odoo123.com%252Fweb%253F%22%2C%2B%22d%22%3A%2B%22odoo123%22%7D
```


 decode as 

```
/auth_oauth/signin?access_token=CC75562316165BAC74675C1853121E85&expires_in=7776000&state={"p":+12,+"r":+"http%3A%2F%2Fo.odoo123.com%2Fweb%3F",+"d":+"odoo123"}
```

 
so need replace '+' with comma(,)

```
kw = simplejson.loads(simplejson.dumps(kw).replace('+',''))
```

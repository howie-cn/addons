# auth_oauth_extended

for qq/weixin/weibo authorization and login into Odoo

provider | authorize url | validation url | user detail url | scope
--------|-------------|-----------|---------|-----
qq | https://graph.qq.com/oauth2.0/authorize | https://graph.qq.com/oauth2.0/me | https://graph.qq.com/oauth2.0/get_user_info | userinfo
dingtalk | https://oapi.dingtalk.com/connect/oauth2/sns_authorize |  https://oapi.dingtalk.com/sns/get_sns_token  | https://oapi.dingtalk.com/sns/getuserinfo | snsapi_login


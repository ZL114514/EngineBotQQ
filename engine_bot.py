# This file contains almost everything of Engine-bot except the web server and QQ-specific content
import base64

from qq_adapter import *

styles = ['超马1', '超马3', '超马世界', '新超马U']


async def command_help(data):
    retval = '''📑 可用的命令 (输入命令以查看用法):
e!help : 查看此帮助。
e!register : 注册帐号或修改密码。
e!query : 查询关卡信息。
e!report : 举报关卡。
e!stats : 查看上传记录。
e!random : 来个随机关卡。'''
    if data['sender']['user_id'] in BOT_ADMIN:
        retval += '''
📑 可用的管理命令:
e!permission : 更新用户权限。'''
    if data['sender']['user_id'] in GAME_ADMIN:
        retval += '''
📑 可用的游戏管理命令:
e!ban : 封禁用户。
e!unban : 解封用户。'''
    send_group_msg(group_id=data['group_id'], message=retval)
    return


async def command_register(data):
    if data['message'].strip() == 'e!register':
        send_group_msg(data['group_id'], '🔗 打开 https://web.enginetribe.gq/register.html 以注册。\n   打开 '
                                         'https://web.enginetribe.gq/change_password.html 以修改密码。')
        return
    else:
        try:
            raw_register_code = data['message'].split(' ')[1]
            register_code = base64.b64decode(raw_register_code.strip().encode()).decode().split("\n")
            operation = register_code[0]
            username = register_code[1]
            password_hash = register_code[2]
            if operation == 'r':  # register
                response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/register',
                                              json={'username': username, 'password_hash': password_hash,
                                                    'user_id': str(data['sender']['user_id']),
                                                    'api_key': ENGINE_TRIBE_API_KEY}).json()
                if 'success' in response_json:
                    send_group_msg(data['group_id'],
                                   '🎉 注册成功，现在可以使用 ' + str(response_json['username']) + ' 在游戏中登录了。')
                else:
                    if response_json['error_type'] == '035':
                        send_group_msg(data['group_id'], '❌ 注册失败。\n' + '一个 QQ 号只能注册一个帐号，' + '\n' +
                                       str(response_json['user_id']) + ' 不能再注册账号了。')
                    elif response_json['error_type'] == '036':
                        send_group_msg(data['group_id'], '❌ 注册失败。\n' + response_json['username'] +
                                       ' 用户名已经存在，请回到注册网页换一个用户名。')
                    else:
                        send_group_msg(data['group_id'],
                                       '❌ 注册失败，发生未知错误。\n' + response_json['error_type'] + '\n' +
                                       response_json['message'])
            elif operation == 'c':  # change password
                response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_password',
                                              json={'username': username, 'password_hash': password_hash,
                                                    'api_key': ENGINE_TRIBE_API_KEY}).json()
                if 'success' in response_json:
                    send_group_msg(data['group_id'],
                                   '🎉 ' + str(response_json['username']) + ' 的密码修改成功。')
                else:
                    send_group_msg(data['group_id'], '❌ 修改密码失败，用户不存在。')
        except Exception as e:
            send_group_msg(data['group_id'], '❌ 无效的注册码，请检查是否复制完全。\n错误信息: ' + str(e))
            return


async def command_ban(data):
    if not data['sender']['user_id'] in GAME_ADMIN:
        send_group_msg(data['group_id'], '❌ 无权使用该命令。')
        return
    if data['message'].strip() == 'e!ban':
        send_group_msg(data['group_id'],
                       '使用方法: e!ban 用户名')
        return
    else:
        try:
            username = data['message'].split(' ')[1]
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': 'banned',
                                                'value': True, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                send_group_msg(data['group_id'],
                               '✅ 成功封禁 ' + username + '。')
            else:
                send_group_msg(data['group_id'], '❌ 权限更新失败。\n' + str(response_json))
                return
        except Exception as e:
            send_group_msg(data['group_id'], '❌ 命令出现错误。\n' + str(e))
            return


async def command_unban(data):
    if not data['sender']['user_id'] in GAME_ADMIN:
        send_group_msg(data['group_id'], '❌ 无权使用该命令。')
        return
    if data['message'].strip() == 'e!unban':
        send_group_msg(data['group_id'],
                       '使用方法: e!unban 用户名')
        return
    else:
        try:
            username = data['message'].split(' ')[1]
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': 'banned',
                                                'value': False, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                send_group_msg(data['group_id'],
                               '✅ 成功解除封禁 ' + username + '。')
            else:
                send_group_msg(data['group_id'], '❌ 权限更新失败。\n' + str(response_json))
                return
        except Exception as e:
            send_group_msg(data['group_id'], '❌ 命令出现错误。\n' + str(e))
            return


async def command_permission(data):
    if not data['sender']['user_id'] in BOT_ADMIN:
        send_group_msg(data['group_id'], '❌ 无权使用该命令。')
        return
    if data['message'].strip() == 'e!permission':
        send_group_msg(data['group_id'],
                       '使用方法: e!permission 用户名 权限名 true或false\n权限: mod, admin, booster, valid, banned')
        return
    else:
        try:
            args = data['message'].replace(data['message'].split(' ')[0], '').strip().split(' ')
            username = args[0]
            permission = args[1]
            if str(args[2]).lower() == 'true':
                value = True
            else:
                value = False
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/update_permission',
                                          json={'username': username, 'permission': permission,
                                                'value': value, 'api_key': ENGINE_TRIBE_API_KEY}).json()
            if 'success' in response_json:
                send_group_msg(data['group_id'],
                               '✅ 成功将 ' + username + ' 的 ' + permission + ' 权限更新为 ' + str(value) + '。')
            else:
                send_group_msg(data['group_id'], '❌ 权限更新失败。\n' + str(response_json))
                return
        except Exception as e:
            send_group_msg(data['group_id'], '❌ 命令出现错误。\n' + str(e))
            return


async def command_report(data):
    if data['message'].strip() == 'e!report':
        send_group_msg(data['group_id'], '''❌ 使用方法: e!report 关卡ID''')
        return
    else:
        level_id = data['message'].split(' ')[1]
        if '-' not in level_id:
            level_id = prettify_level_id(level_id)
        if len(level_id) != 19:
            send_group_msg(data['group_id'], '''❌ 无效的关卡 ID。''')
            return
    try:
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/stage/' + level_id,
                                      data='auth_code=' + BOT_AUTH_CODE,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded',
                                               'User-Agent': 'EngineBot/1'}).json()
        if 'error_type' in response_json:
            send_group_msg(data['group_id'], '''❌ 关卡未找到。''')
            return
        else:
            level_data = response_json['result']
            response_json_user = requests.post(url=ENGINE_TRIBE_HOST + '/user/info',
                                               json={'username': level_data['author']}).json()
            message = '⚠ 接到举报: ' + level_id + ' ' + level_data['name'] + '\n'
            message += '作者: ' + level_data['author'] + '\n'
            message += '作者 QQ: ' + str(response_json_user['result']['user_id']) + '\n'
            message += '上传于 ' + level_data['date']
            message += '  ' + str(level_data['likes']) + '❤ ' + str(level_data['dislikes']) + '💙\n'
            clears = level_data['victorias']
            plays = level_data['intentos']
            deaths = level_data['muertes']
            if int(plays) == 0:
                message += str(clears) + '次通关/' + str(plays) + '次游玩\n'
            else:
                message += str(clears) + '次通关/' + str(plays) + '次游玩 ' + str(
                    round((int(clears) / int(deaths)) * 100, 2)) + '%\n'
            message += '标签: ' + level_data['etiquetas'] + ', 游戏风格: ' + styles[int(level_data['apariencia'])]
            send_group_msg(group_id=ADMIN_GROUP, message=message)
            return
    except Exception as e:
        send_group_msg(data['group_id'],
                       level_id + '''\n❌ 获得被举报的关卡信息时出现错误，连接到引擎部落后端时出错。\n''' + str(e))
        return


async def command_query(data):
    if data['message'].strip() == 'e!query':
        send_group_msg(data['group_id'], '''❌ 使用方法: e!query 关卡ID''')
        return
    else:
        level_id = data['message'].split(' ')[1].upper()
        if '-' not in level_id:
            level_id = prettify_level_id(level_id)
        if len(level_id) != 19:
            send_group_msg(data['group_id'], '''❌ 无效的关卡 ID。''')
            return
        try:
            response_json = requests.post(url=ENGINE_TRIBE_HOST + '/stage/' + level_id,
                                          data='auth_code=' + BOT_AUTH_CODE,
                                          headers={'Content-Type': 'application/x-www-form-urlencoded',
                                                   'User-Agent': 'EngineBot/1'}).json()
            if 'error_type' in response_json:
                send_group_msg(data['group_id'], '''❌ 关卡未找到。''')
                return
            else:
                level_data = response_json['result']
                message = '🔍 查询关卡: ' + level_data['name'] + '\n'
                message += '作者: ' + level_data['author']
                if int(level_data['featured']) == 1:
                    message += ' (管理推荐关卡)'
                message += '\n'
                message += '上传于 ' + level_data['date']
                message += '  ' + str(level_data['likes']) + '❤ ' + str(level_data['dislikes']) + '💙\n'
                clears = level_data['victorias']
                plays = level_data['intentos']
                deaths = level_data['muertes']
                if int(plays) == 0:
                    message += str(clears) + '次通关/' + str(plays) + '次游玩\n'
                else:
                    message += str(clears) + '次通关/' + str(plays) + '次游玩 ' + str(
                        round((int(clears) / int(deaths)) * 100, 2)) + '%\n'
                message += '标签: ' + level_data['etiquetas'] + ', 游戏风格: ' + styles[int(level_data['apariencia'])]
                send_group_msg(group_id=data['group_id'], message=message)
                return
        except Exception as e:
            send_group_msg(data['group_id'], '''❌ 命令出现错误，连接到引擎部落后端时出错。''' + str(e))
            return


async def command_random(data):
    try:
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/stage/random',
                                      data='auth_code=' + BOT_AUTH_CODE,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded',
                                               'User-Agent': 'EngineBot/1'}).json()
        level_data = response_json['result']
        message = '💫 随机关卡: ' + level_data['name'] + '\n'
        message += 'ID: ' + level_data['id'] + '\n'
        message += '作者: ' + level_data['author']
        if int(level_data['featured']) == 1:
            message += ' (管理推荐关卡)'
        message += '\n'
        message += '上传于 ' + level_data['date']
        message += '  ' + str(level_data['likes']) + '❤ ' + str(level_data['dislikes']) + '💙\n'
        clears = level_data['victorias']
        plays = level_data['intentos']
        deaths = level_data['muertes']
        if int(plays) == 0:
            message += str(clears) + '次通关/' + str(plays) + '次游玩\n'
        else:
            message += str(clears) + '次通关/' + str(plays) + '次游玩 ' + str(
                round((int(clears) / int(deaths)) * 100, 2)) + '%\n'
        message += '标签: ' + level_data['etiquetas'] + ', 游戏风格: ' + styles[int(level_data['apariencia'])]
        send_group_msg(group_id=data['group_id'], message=message)
        return
    except Exception as e:
        send_group_msg(data['group_id'], '''❌ 命令出现错误，连接到引擎部落后端时出错。''' + str(e))
        return


async def command_stats(data):
    if data['message'].strip() == 'e!stats':
        request_body = {'user_id': data['sender']['user_id']}
    else:
        request_body = {'username': data['message'].replace('e!stats', '').strip()}
    try:
        response_json = requests.post(url=ENGINE_TRIBE_HOST + '/user/info',
                                      json=request_body).json()
        if 'error_type' in response_json:
            send_group_msg(data['group_id'], '''❌ 数据不存在。''')
            return
        else:
            user_data = response_json['result']
            message = '📜 玩家 ' + user_data['username'] + ' 的上传记录\n'
            message += '共上传了 ' + str(user_data['uploads']) + ' 个关卡。'
            if str(user_data['uploads']) == '0':
                send_group_msg(group_id=data['group_id'], message=message)
            else:
                all_likes = 0
                all_dislikes = 0
                all_plays = 0
                message += '\n'
                levels_data = requests.post(url=ENGINE_TRIBE_HOST + '/stages/detailed_search',
                                            data={'auth_code': BOT_AUTH_CODE, 'author': user_data['username']},
                                            headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
                for level_data in levels_data['result']:
                    message += '- ' + level_data['name'] + ' ' + str(level_data['likes']) + '❤ ' + str(
                        level_data['dislikes']) + '💙\n  ' + level_data['id']
                    if int(level_data['featured']) == 1:
                        message += ' (推荐)'
                    message += '\n'
                    all_likes += int(level_data['likes'])
                    all_dislikes += int(level_data['dislikes'])
                    all_plays += int(level_data['intentos'])
                    message += '  标签: ' + level_data['etiquetas'] + '\n'
                message += '总获赞: ' + str(all_likes) + ' 总获孬: ' + str(all_dislikes) + ' 总游玩: ' + str(all_plays)
                send_group_msg(group_id=data['group_id'], message=message)
            return
    except Exception as e:
        send_group_msg(data['group_id'], '''❌ 命令出现错误，连接到引擎部落后端时出错。''' + str(e))
        return


def prettify_level_id(level_id: str):
    return level_id[0:4] + '-' + level_id[4:8] + '-' + level_id[8:12] + '-' + level_id[12:16]

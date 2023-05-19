import discord
import database as db

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def is_admin(name):
    admins = db.get("admins")
    if admins == None:
        return 0
    if str(name) not in admins:
        return 0
    return 1

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "help":
        with open("help.txt", "r", encoding="utf-8") as file:
            await message.channel.send(file.read())
        return
    if message.type == discord.MessageType.new_member:
        await message.channel.send(
            "Отправьте \"help\", чтобы ознакомиться со списком команд")
        return

    cmd = ""
    param = ""
    try:
        a = message.content.split(" ")
        cmd = a[0]
        del a[0]
        if not len(a):
            return
        param = " ".join(a)
    except:
        return
    ans = ""

    if cmd == "join":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            members = db.get("queues", param, "members")
            if members == None:
                members = []
            if str(message.author.mention) in members:
                ans = f"Вы уже находитесь в очереди {param}"
            else:
                db.put(str(message.author.mention), "queues", param, "members", str(len(members)))
                ans = f"Вы были добавлены в конец очереди {param}"
    elif cmd == "leave":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            members = db.get("queues", param, "members")
            if members == None:
                members = []
            if str(message.author.mention) not in members:
                ans = f"Вы не находитесь в очереди {param}"
            else:
                del members[members.index(str(message.author.mention))]
                db.put(members, "queues", param, "members")
                ans = f"Вы были удалены из очереди {param}"
    elif cmd == "info":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            members = db.get("queues", param, "members")
            if members == None:
                members = []
            ans = f"В очереди {param} сейчас {len(members)} человек(а)"
            if len(members):
                ans += ":"
            for i in members:
                ans += f"\n{i}"
    elif cmd == "q" and param == "list":
        ans = "Список доступных очередей:"
        queues = db.get("queues")
        if queues == None:
            queues = []
        for i in queues:
            ans += f"\n{i}"
    elif cmd == "skip":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            members = db.get("queues", param, "members")
            if members == None:
                members = []
            if str(message.author.mention) not in members:
                ans = f"Вы не находитесь в очереди {param}"
            elif members.index(str(message.author.mention)) == len(members)-1:
                ans = "За вами никого нет"
            else:
                i = members.index(str(message.author.mention))
                members[i], members[i+1] = members[i+1], members[i]
                db.put(members, "queues", param, "members")
                ans = f"Вы успешно поменялись с {members[i]}"
    elif cmd == "url":
        urls = db.get("urls")
        if urls == None:
            urls = {}
        for i in urls.keys():
            if urls[i]["author"] == str(message.author.mention):
                del urls[i]
                break
        db.put(urls, "urls")
        if param == "del":
            ans = "Ссылка удалена успешно"
        else:
            db.post({"author":str(message.author.mention), "url":param}, "urls")
            ans = "Ссылка установлена успешно"

    if ans != "":
        await message.channel.send(ans)
        return

    if not is_admin(message.author):
        return
    print(param)
    if cmd == "admin":
        admins = db.get("admins")
        if param in admins:
            ans = f"{param} уже является администратором"
        else:
            admins.append(param)
            db.put(admins, "admins")
            ans = f"{param} назначен администратором"
    elif cmd == "unadmin":
        admins = db.get("admins")
        if param not in admins:
            ans = f"{param} не является администратором"
        else:
            del admins[admins.index(param)]
            db.put(admins, "admins")
            ans = f"{param} больше не администратор"
    elif cmd == "create":
        if db.get("queues", param) != None:
            ans = "Очередь с таким именем уже существует"
        else:
            db.put({"creator":str(message.author)}, "queues", param)
            ans = f"Очередь {param} создана успешно"
    elif cmd == "delete":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            db.put({}, "queues", param)
            ans = f"Очередь {param} удалена"
    elif cmd == "next":
        if db.get("queues", param) == None:
            ans = "Такой очереди не существует"
        else:
            f = 1
            while f:
                members = db.get("queues", param, "members")
                if members == None:
                    ans = "Очередь пуста"
                    f = 0
                else:
                    user = members[0]
                    del members[0]
                    db.put(members, "queues", param, "members")
                    msg = await message.channel.send(f"{user}, настала ваша очередь! Отреагируйте под сообщением")
                    await msg.add_reaction('\N{THUMBS UP SIGN}')
                    time = int(db.get("time"))
                    try:
                        while 1:
                            reaction, u = await client.wait_for('reaction_add', timeout=time)
                            if u.mention == user:
                                ans = "Успешно!"
                                f = 0
                                break
                    except:
                        await message.channel.send("Вы прозевали свою очередь")
                    ch = None
                    chwait = None
                    for channel in client.guilds[0].channels:
                        if str(channel.type) == 'voice' and channel.user_limit == 2:
                            if len(channel.members) == 0:
                                ch = channel
                            elif len(channel.members) == 1 and str(channel.members[0].name) + "#" + str(channel.members[0].discriminator) == str(message.author):
                                ch = channel
                                break
                    for channel in client.guilds[0].channels:
                        if str(channel.name) == "ожидание":
                            chwait = channel
                            continue
                    try:
                        await message.author.move_to(ch)
                    except:
                        pass
                    if chwait:
                        for i in chwait.members:
                            if str(i.mention) == str(user):
                                await i.move_to(ch)
                                break
                    urls = db.get("urls")
                    if not urls:
                        urls = {}
                    for i in urls.keys():
                        if urls[i]["author"] == str(user):
                            await message.author.send(f"Ссылка от {user}: " + urls[i]["url"])

    elif cmd == "time":
        if not param.isnumeric() or int(param) < 10:
            ans = "Время должно быть числом секунд большим или равным 10"
        else:
            db.put(int(param), "time")
            ans = "Время установлено успешно"
    if ans != "":
        await message.channel.send(ans)

client.run(db.get("token"))

import discord
import discord.utils
from discord.ext import commands
from webserver import keep_alive
import os
import json
import random



client = commands.Bot(command_prefix = '-')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('記錄中。。。'))
    print('Bot is ready.')



@client.command(aliases = ['direct'])
async def directory(ctx):
  myEmbed = discord.Embed(title = "指令列表 '-'",
                          description = "所有 @秘書ちゃん 的银行系统指令列表\nList of all @秘書ちゃん commands",
                          color = 0xe74c3c)
  myEmbed.add_field(name = "work",
                    value = "每小時工作一次\nWork once every hour",
                    inline = False)
  myEmbed.add_field(name = "clean",
                    value = "每半小時幫助賭場進行清潔一次\nhelp cleaning the casino once every half an hour",
                    inline = False)
  myEmbed.add_field(name = "bal",
                    value = "查看自己的餘額\nCheck your balance",
                    inline = False)
  myEmbed.add_field(name = "dep [amount]",
                    value = "存放金錢在自己的戶口\nDeposit money into your bank",
                    inline = False)
  myEmbed.add_field(name = "draw [amount]",
                    value = "從自己的戶口提取金銭\nWithdraw money from your bank",
                    inline = False)
  myEmbed.add_field(name = "send @[user] [amount]",
                    value = "轉帳給其他用戶\nTransfer your money to others",
                    inline = False)
  myEmbed.add_field(name = "slot [amount]",
                    value = "遊玩老虎機 (錢包裏至少￥500)\nPlay slot machine (at least ￥500 in wallet)",
                    inline = False)
  myEmbed.add_field(name = "guess [amount]",
                    value = "猜數字遊戲 (錢包裏至少￥500)\nPlay number game (at least ￥500 in wallet)",
                    inline = False)
  myEmbed.add_field(name = "roulette [amount]",
                    value = "扣動板機 (錢包裏至少￥500)\nPlay roulette (at least ￥500 in wallet)",
                    inline = False)
  myEmbed.add_field(name = "dice [amount]",
                    value = "擲骰子 (錢包裏至少￥500)\nPlay dice game (at least ￥500 in wallet)",
                    inline = False)
  myEmbed.add_field(name = "fortune [amount]",
                    value = "命運之輪 (錢包裏至少￥100000)\nPlay wheel of fortune (at least ￥100000 in wallet)",
                    inline = False)
  myEmbed.set_footer(text = "如有任何提問/意見，歡迎私訊四宮!!")
  await ctx.send(embed = myEmbed)



##Curency system

@client.command(aliases = ["bal"])
async def balance(ctx, member: discord.Member = None):
  if not member:
    member = ctx.author
  await open_account(member)

  users = await get_bank_data()
  user = member

  wallet_amount = users[str(user.id)]["wallet"]
  bank_amount = users[str(user.id)]["bank"]
  total = wallet_amount + bank_amount

  balEmbed = discord.Embed(title = f"{member.name}的餘額\n{member.name}'s balance", colour = discord.Color.red())
  balEmbed.add_field(name = "錢包\nWallet", value = wallet_amount)
  balEmbed.add_field(name = "戶口\nBank", value = bank_amount)
  balEmbed.add_field(name = "總共\nTotal", value = total)
  await ctx.send(embed = balEmbed)



@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    if round(error.retry_after) < 60:
      timeLeft = round(error.retry_after)
      await ctx.send(f"請在{timeLeft}秒后再使用此指令。\nPlease try again after {timeLeft} seconds.")

    if round(error.retry_after) > 60 and round(error.retry_after) < 3600:
      timeLeft = round(error.retry_after)
      minutesLeft = timeLeft / 60
      minutesLeft = round(minutesLeft)
      await ctx.send(f"請在{minutesLeft}分鐘后再使用此指令。\nPlease try again after {minutesLeft} minutes.")
    
    elif round(error.retry_after) < 86400 and round(error.retry_after) > 3600:
      timeLeft = round(error.retry_after)
      minutesLeft = timeLeft / 60
      minutesLeft = round(minutesLeft)
      hoursLeft = minutesLeft / 60
      hoursLeft = round(hoursLeft)
      await ctx.send(f"請在{hoursLeft}小時后再使用此指令。\nPlease try again after {hoursLeft} hours.")
    
    elif round(error.retry_after) > 86400:
      timeLeft = round(error.retry_after)
      minutesLeft = timeLeft / 60
      minutesLeft = round(minutesLeft)
      hoursLeft = minutesLeft / 60
      hoursLeft = round(hoursLeft)
      daysLeft = hoursLeft / 24
      daysLeft = round(daysLeft)
      await ctx.send(f"請在{daysLeft}天后再使用此指令。\nPlease try again after {daysLeft} days.")



@client.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def work(ctx):
    await open_account(ctx.author)
    earnings = random.randrange(500, 1000)
    await update_bank(ctx.author, earnings, "wallet")
    await ctx.send(f"你賺了￥**{earnings}**。\nYou have earned ￥**{earnings}**.")



@client.command()
@commands.cooldown(1, 1800, commands.BucketType.user)
async def clean(ctx):
    await open_account(ctx.author)
    earnings = random.randrange(500, 1000)
    await update_bank(ctx.author, earnings, "wallet")
    await ctx.send(f"你幫賭場進行清理，賺了￥**{earnings}**。\nYou helped cleaning the casino and earned ￥**{earnings}**.")



@client.command(aliases = ["draw"])
async def withdraw(ctx, amount = None):
  await open_account(ctx.author)

  if amount == None:
    await ctx.send('請打出你要從戶口取出的數目。\nPlease include the amount of money you want to withdraw.')
    return
  
  users = await get_bank_data()
  user = ctx.author

  bank_amount = users[str(user.id)]["bank"]
  
  if amount == "all":
    amount = bank_amount
  elif amount == "max":
    amount = bank_amount
  
  amount = int(amount)

  if amount < 0:
    await ctx.send('數目必需大於0。\nThe amount needs to be more than 0.')
    return
  if amount > bank_amount:
    await ctx.send('你並没有足夠的餘額進行轉帳。\nYou do not have suffucient amount for the transaction to take place.')
    return
  
  await update_bank(ctx.author, amount, "wallet")
  await update_bank(ctx.author, -1 * amount, "bank")

  await ctx.send(f"你取出了￥**{amount}**。\nYou have withdrawn ￥**{amount}**.")



@client.command(aliases = ["dep"])
async def deposit(ctx, amount = None):
  await open_account(ctx.author)

  if amount == None:
    await ctx.send('請打出你要放進戶口的數目。\nPlease include the amount of money you want to deposit.')
    return
  
  users = await get_bank_data()
  user = ctx.author

  wallet_amount = users[str(user.id)]["wallet"]
  
  if amount == "all":
    amount = wallet_amount
  elif amount == "max":
    amount = wallet_amount
  
  amount = int(amount)

  if amount < 0:
    await ctx.send('數目必需大於0。\nThe amount needs to be more than 0.')
    return
  if amount > wallet_amount:
    await ctx.send('你並没有足夠的餘額進行轉帳。\nYou do not have suffucient amount for the transaction to take place.')
    return

  
  await update_bank(ctx.author, -1 * amount, "wallet")
  await update_bank(ctx.author, amount, "bank")

  await ctx.send(f"你存放了￥**{amount}**。\nYou have deposited ￥**{amount}**.")



@client.command(aliases = ["send"])
async def give(ctx, member:discord.Member, amount = None):
  await open_account(ctx.author)
  await open_account(member)

  if amount == None:
    await ctx.send('請打出你要轉帳的數目。\nPlease include the amount of money you want to transfer.')
    return
  
  users = await get_bank_data()
  user = ctx.author

  wallet_amount = users[str(user.id)]["wallet"]
  
  if amount == "all":
    amount = wallet_amount
  elif amount == "max":
    amount = wallet_amount
  
  amount = int(amount)

  if amount < 0:
    await ctx.send('數目必需大於0。\nThe amount needs to be more than 0.')
    return
  if amount > wallet_amount:
    await ctx.send('你並没有足夠的餘額進行轉帳。\nYou do not have suffucient amount for the transaction to take place.')
    return
  
  await update_bank(ctx.author, -1 * amount, "wallet")
  await update_bank(member, amount, "wallet")

  await ctx.send(f"你轉帳了￥**{amount}** 給**{member}**。\nYou have transferred ￥**{amount}** to **{member}**.")



@client.command()
async def spawn(ctx, member:discord.Member, amount = None):
  if ctx.author.id == 509989355792629767:
    await open_account(member)

    if amount == None:
      await ctx.send('請打出你要轉帳的數目。')
      return

    amount = int(amount)

    if amount < 0:
      await ctx.send('數目必需大於0。')
      return
    
    await update_bank(member, amount, "wallet")

    await ctx.send(f"你轉帳了￥**{amount}** 給**{member}**。")
  else:
    await ctx.send("不好意思，你並沒有權限使用此指令。\nSorry, you do not have permission to use this command.")



@client.command()
async def remove(ctx, member:discord.Member, amount = None):
  if ctx.author.id == 509989355792629767:
    await open_account(member)

    if amount == None:
      await ctx.send('請打出你要收取的數目。')
      return

    amount = int(amount)

    if amount < 0:
      await ctx.send('數目必需大於0。')
      return
    
    await update_bank(member, -1 * amount, "wallet")

    await ctx.send(f"你從 {member} 收取了￥**{amount}**。")
  else:
    await ctx.send("不好意思，你並沒有權限使用此指令。\nSorry, you do not have permission to use this command.")



@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def slot(ctx, amount=None):
  if amount == None:
    return await ctx.send('請打出你要賭注的數目。\nPlease include the amount of money you want to bet.')

  await open_account(ctx.author)
  bal = await update_bank(ctx.author)

  amount = int(amount)

  if amount < 10:
    return await ctx.send('你必需賭注至少￥**10**。\nYou need to bet at least ￥**10**.')
  elif amount > 500:
    return await ctx.send('你最多只能賭注￥**500**。\nYou can bet at most ￥**500**.')
  else:
      if amount > bal[0]:
        return await ctx.send("你並没有足夠的餘額進行賭注。\nYou do not have suffucient amount to bet.")
      if amount < 0:
        return await ctx.send("數目必需大於0。\nThe amount needs to be more than 0.")
      if bal[0] < 500:
        return await ctx.send("如果輸的話，你的錢包並没有足夠的餘額賠款。\nYou do not have suffucient amount in your wallet to pay if you lose.")

  final = []
  for i in range(3):
      a = random.choice(["7️⃣", "❌", "🔄", "💎", "✨","🔥", "🌟", "🌙", "☀", "🛎", "🛑", "🍻"])

      final.append(a)

  slotsEmbed = discord.Embed(Title = f"{ctx.author.name}的老虎機遊戲\n{ctx.author.name}'s slot machine")
  slotsEmbed.add_field(name = '你的老虎機遊戲\nYour slot machine', value = str(final))
  await ctx.send(embed=slotsEmbed)

  if final[0] == final[1] == final[2]:
      await update_bank(ctx.author, 7*amount)
      await ctx.send(f"你中了三個相同的圖案啊！！你獲得了￥**{7*amount}**。\nYou have gotten three identical emojis!! You received ￥**{7*amount}**.")

  if final[0] == final[1] or final[0] == final[2] or final[1] == final[2]:
      await update_bank(ctx.author, 1.5*amount, "wallet")
      await ctx.send(f"你中了兩個相同的圖案啊！！你獲得了￥**{1.5*amount}**。\nYou have gotten two identical emojis!! You received ￥**{1.5*amount}**.")
  
  else:
    await update_bank(ctx.author, -1 * amount, "wallet")
    await ctx.send(f"你並没有中任何相同的圖案。你損失了￥**{amount}**。\nYou did not get any pair of adentical emojis. You lost ￥**{amount}**.")



@client.command(aliases = ["guess"])
@commands.cooldown(1, 30, commands.BucketType.user)
async def number(ctx, amount=None):
  if amount == None:
    return await ctx.send('請打出你要賭注的數目。\nPlease include the amount of money you want to bet.')

  await open_account(ctx.author)
  bal = await update_bank(ctx.author)

  amount = int(amount)

  if amount < 10:
    return await ctx.send('你必需賭注至少￥**10**。\nYou need to bet at least ￥**10**.')
  elif amount > 500:
    return await ctx.send('你最多只能賭注￥**500**。\nYou can bet at most ￥**500**.')
  else:
      if amount > bal[0]:
        return await ctx.send("你並没有足夠的餘額進行賭注。\nYou do not have suffucient amount to bet.")
      if amount < 0:
        return await ctx.send("數目必需大於0。\nThe amount needs to be more than 0.")
      if bal[0] < 500:
        return await ctx.send("如果輸的話，你的錢包並没有足夠的餘額賠款。\nYou do not have suffucient amount in your wallet to pay if you lose.")
  
  correct = False
  await ctx.send('數字介於 1 - 100 之間，猜猜看吧！你有**5**次機會。\nThe number is between 1 and 100. Make a guess! You have **5** chances.')
  number = random.randint(1, 100)
  tryTimes = 0
  while (tryTimes < 5):
    res = await client.wait_for('message')
    if res.content.isdigit():
      tryTimes+= 1
      guess = int(res.content)
      if guess == number:
        correct = True
        await update_bank(ctx.author, 1.5*amount, "wallet")
        await ctx.send(f"你终於猜對了！你獲得了￥**{1.5*amount}**。\nYou got the number right! You received ￥**{1.5*amount}**")
        break
      elif tryTimes == 5:
        break
      elif guess > number:
        await ctx.send(f"你猜的數字太大了，再猜猜看吧。你剩下**{5 - tryTimes}**次。\nYou guess is too big. Guess again! You are left with **{5 - tryTimes}** chances.")
      elif guess < number:
        await ctx.send(f"你猜的數字太小了，再猜猜看吧。你剩下**{5 - tryTimes}**次。\nYou guess is too small. Guess again! You are left with **{5 - tryTimes}** chances.")
  if correct == False:
    await update_bank(ctx.author, -1 * amount, "wallet")
    await ctx.send(f"你已經使用了5次機會了！答案是**{number}**。你損失了￥**{amount}**。\nYou have used all 5 chances. The answer is **{number}**. You lost ￥**{amount}**.")



@client.command(aliases = ["f"])
@commands.cooldown(1, 900, commands.BucketType.user)
async def fortune(ctx, amount=None):
  if amount == None:
    return await ctx.send('請打出你要賭注的數目。\nPlease include the amount of money you want to bet.')

  await open_account(ctx.author)
  bal = await update_bank(ctx.author)

  amount = int(amount)

  if amount < 1:
    return await ctx.send('你必需賭注至少￥**1**。\nYou need to bet at least ￥**1**.')
  elif amount > 10000:
    return await ctx.send('你最多只能賭注￥**10000**。\nYou can bet at most ￥**10000**.')
  else:
      if amount > bal[0]:
        return await ctx.send("你並没有足夠的餘額進行賭注。\nYou do not have suffucient amount to bet.")
      if amount < 0:
        return await ctx.send("數目必需大於0。\nThe amount needs to be more than 0.")
      if bal[0] < 100000:
        return await ctx.send("如果輸的話，你的錢包並没有足夠的餘額賠款。\nYou do not have suffucient amount in your wallet to pay if you lose.")
  
  b = "大凶"
  c = "末凶"
  d = "半凶"
  e = "小凶"
  f = "凶"
  g = "末小吉"
  h = "末吉"
  j = "半吉"
  k = "吉"
  l = "小吉"
  m = "中吉"
  n = "大吉"
  answer = random.choice([b, c, d, e, f, g, h, j, k, l, m, n])

  if answer == b:
    await update_bank(ctx.author, -10 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！損失了￥**{10*amount}**\nYou've got {answer}! And lost ￥**{10*amount}**.")
  
  elif answer == c:
    await update_bank(ctx.author, -8 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！損失了￥**{8*amount}**\nYou've got {answer}! And lost ￥**{8*amount}**.")
  
  elif answer == d:
    await update_bank(ctx.author, -6 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！損失了￥**{6*amount}**\nYou've got {answer}! And lost ￥**{6*amount}**.")

  elif answer == e:
    await update_bank(ctx.author, -4 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！損失了￥**{4*amount}**\nYou've got {answer}! And lost ￥**{4*amount}**.")

  elif answer == f:
    await update_bank(ctx.author, -2 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！損失了￥**{2*amount}**\nYou've got {answer}! And lost ￥**{2*amount}**.")

  elif answer == g:
    await update_bank(ctx.author, 1.5 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{1.5*amount}**\nYou've got {answer}! And won ￥**{1.5*amount}**.")

  elif answer == h:
    await update_bank(ctx.author, 2 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{2*amount}**\nYou've got {answer}! And won ￥**{2*amount}**.")

  elif answer == j:
    await update_bank(ctx.author, 3 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{3*amount}**\nYou've got {answer}! And won ￥**{3*amount}**.")

  elif answer == k:
    await update_bank(ctx.author, 4 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{4*amount}**\nYou've got {answer}! And won ￥**{4*amount}**.")

  elif answer == l:
    await update_bank(ctx.author, 5 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{5*amount}**\nYou've got {answer}! And won ￥**{5*amount}**.")

  elif answer == m:
    await update_bank(ctx.author, 7 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{7*amount}**\nYou've got {answer}! And won ￥**{7*amount}**.")

  elif answer == n:
    await update_bank(ctx.author, 9 * amount, "wallet")
    await ctx.send(f"你抽到了{answer}！獲得了￥**{9*amount}**\nYou've got {answer}! And won ￥**{9*amount}**.")



@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def dice(ctx, amount=None):
  if amount == None:
    return await ctx.send('請打出你要賭注的數目。\nPlease include the amount of money you want to bet.')

  await open_account(ctx.author)
  bal = await update_bank(ctx.author)

  amount = int(amount)

  if amount < 10:
    return await ctx.send('你必需賭注至少￥**10**。\nYou need to bet at least ￥**10**.')
  elif amount > 500:
    return await ctx.send('你最多只能賭注￥**500**。\nYou can bet at most ￥**500**.')
  else:
      if amount > bal[0]:
        return await ctx.send("你並没有足夠的餘額進行賭注。\nYou do not have suffucient amount to bet.")
      if amount < 0:
        return await ctx.send("數目必需大於0。\nThe amount needs to be more than 0.")
      if bal[0] < 500:
        return await ctx.send("如果輸的話，你的錢包並没有足夠的餘額賠款。\nYou do not have suffucient amount in your wallet to pay if you lose.")
  

  await ctx.send(f"🎲你下注￥**{amount}**，並擲骰子...\nYou bet ￥**{amount}**, and threw the dice...")
  number = random.randint(1, 6)
  number2 = random.randint(1, 6)
  total_number = number + number2
  ai_number = random.randint(1, 6)
  ai_number2 = random.randint(1, 6)
  ai_total_number = ai_number + ai_number2
  await ctx.send(f"🎲你骰到**{number}**和**{number2}**...\nYou got **{number}** and **{number2}**...")
  await ctx.send(f"🎲你的對手擲出骰子...並骰到**{ai_number}**和**{ai_number2}**...\nYour opponent threw the dice... and got **{ai_number}** and **{ai_number2}**...")


  if total_number > ai_total_number: 
    await update_bank(ctx.author, 1.5*amount, "wallet")
    await ctx.send(f"🎲你贏了￥**{1.5*amount}。**\nYou won ￥**{1.5*amount}**.")

  elif total_number == ai_total_number:
    await update_bank(ctx.author, amount, "wallet")
    await ctx.send(f"🎲這是平局，你拿回了￥**{amount}**。\nThis is a draw. You took back ￥**{amount}**.")
  
  elif total_number < ai_total_number:
    await update_bank(ctx.author, -1*amount, "wallet")
    await ctx.send(f"🎲你輸了￥**{amount}。**\nYou lost ￥**{amount}**.")



@client.command(aliases = ["ro"])
@commands.cooldown(1, 30, commands.BucketType.user)
async def roulette(ctx, amount=None):
  if amount == None:
    return await ctx.send('請打出你要賭注的數目。\nPlease include the amount of money you want to bet.')

  await open_account(ctx.author)
  bal = await update_bank(ctx.author)

  amount = int(amount)

  if amount < 10:
    return await ctx.send('你必需賭注至少￥**10**。\nYou need to bet at least ￥**10**.')
  elif amount > 500:
    return await ctx.send('你最多只能賭注￥**500**。\nYou can bet at most ￥**500**.')
  else:
      if amount > bal[0]:
        return await ctx.send("你並没有足夠的餘額進行賭注。\nYou do not have suffucient amount to bet.")
      if amount < 0:
        return await ctx.send("數目必需大於0。\nThe amount needs to be more than 0.")
      if bal[0] < 500:
        return await ctx.send("如果輸的話，你的錢包並没有足夠的餘額賠款。\nYou do not have suffucient amount in your wallet to pay if you lose.")
  
  await ctx.send(f"🔫你下注了**{amount}**並扣動扳機...\nYou bet ￥**{amount}** and pulled the trigger...")
  
  a = "win"
  b = "lose"
  result = random.choice([a, b])

  if result == a:
    await update_bank(ctx.author, 1.5 * amount, "wallet")
    await ctx.send(f"你贏回了**{1.5*amount}**。\nYou won ￥**{1.5*amount}**.")
  
  elif result == b:
    await update_bank(ctx.author, -1 * amount, "wallet")
    await ctx.send(f"你輸了**{amount}**。\nYou lost ￥**{amount}**.")



async def open_account(user):
  users = await get_bank_data()


  if str(user.id) in users:
    return False
  else:
    users[str(user.id)] = {}
    users[str(user.id)]["wallet"] = 0
    users[str(user.id)]["bank"] = 100

  with open("bank.json", "w") as f:
    json.dump(users, f, indent=3)
  return True


async def get_bank_data():
  with open("bank.json", "r") as f:
    users = json.load(f)

  return users


async def update_bank(user, change=0, mode="wallet"):
  users = await get_bank_data()

  users[str(user.id)][mode] += change

  with open ("bank.json", "w") as f:
    json.dump(users, f, indent=3)

  bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
  return bal



keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run('ODg0MjU3NzE3NjU1NTkzMDEw.YTV3LA.XAh146O2TW_6oE2uEHXo1dZDpEU')

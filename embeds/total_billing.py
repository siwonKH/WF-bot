import discord
from random import randint
from datetime import datetime


def get_total_billing_embed(cost: int, member_cnt: int, date: datetime):
    subtotal = format(cost, ',')
    discount = str(format(round(cost / member_cnt * (member_cnt - 1) * -1, 1), ','))
    total = str(format(round(cost / member_cnt, 1), ','))

    embed = discord.Embed(
        title=f"ChatGPT Plus [{date.month}월]",
        description=f"이번 달 요금: KRW {cost}\n인당 요금: KRW {total}",
        color=0xffffff,
        timestamp=date
    )
    embed.add_field(
        name="",
        value=f"""
`                                  `
` ChatGPT Plus Sub.       US$20.00 `
` Tax                      US$2.00 `
`                                  `
` Subtotal                US$22.00 `
` Subtotal(Won){" " * (15 - len(subtotal))}KRW {subtotal} `
` Discount(Won){" " * (15 - len(discount))}KRW {discount} `
`                                  `
` Total(Won){" " * (18 - len(total))}KRW {total} `
`                                  `
"""
    )
    embed.set_footer(text="Date")
    return embed

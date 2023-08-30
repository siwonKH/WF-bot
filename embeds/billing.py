import discord
from datetime import datetime


def get_billing_embed(cost: int, member_cnt: int):
    now = datetime.now()

    discount = str(round(cost / member_cnt * (member_cnt - 1) * -1, 1))
    total = str(round(cost / member_cnt, 1))

    embed = discord.Embed(title=f"ChatGPT Plus [{now.month}월]",
                          description=f"이번 달 요금: KRW {total}",
                          colour=0x00b0f4,
                          timestamp=now)

    embed.add_field(name="",
                    value=f"""`                                  `
` ChatGPT Plus Sub.       US$20.00 `
` Tax                      US$2.00 `
`                                  `
` Subtotal                US$22.00 `
` Subtotal(Won)         KRW {format(cost, ',')} `
` Discount(Won){" " * (15 - len(discount))}KRW {discount} `
`                                  `
` Total{" " * (23 - len(total))}KRW {total} `
`                                  `""",
                    inline=False)

    embed.set_footer(text="Date")

    return embed

import LilyWebhook as Hook
import asyncio

async def main():
    webhook = "https://discord.com/api/webhooks/1461403375303393380/q56-lczDRUzTXmfdKoOrO584WxGnaeUVmnJCNnRDrLI7mudmis32rzj2IfsKyJ_0JJi2"
    webhook = Hook.Webhook(webhook, "Shree")

    view = Hook.ComponentBuilder()
    view.add(Hook.Content("Hi"))
    view.add(Hook.Content("Hi"))
    view.add(Hook.Container().add(Hook.Content("Hello")).add(Hook.Content("# HELLO")))

    view.add(Hook.ButtonLink(emoji="😳"))

    try:
        response = await webhook.send(component=view)
        await webhook.close()
    except Exception as e:
        print(e)
        await webhook.close()

asyncio.run(main())
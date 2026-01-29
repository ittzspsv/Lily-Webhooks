import LilyWebhook as LDH
import asyncio




async def main():
    webhook = "https://discord.com/api/webhooks/1461403375303393380/q56-lczDRUzTXmfdKoOrO584WxGnaeUVmnJCNnRDrLI7mudmis32rzj2IfsKyJ_0JJi2"
    webhook = LDH.Webhook(webhook, "Shree")

    cv2 = LDH.ComponentBuilder()
    cv2.add(
        LDH.Content("Hello")
    )
    cv2.add(
        LDH.Content("Hii")
    )
    container = LDH.Container()
    container.add(LDH.Content("Hello"))
    container.add(LDH.Separator())
    container.add(LDH.Content("Hello"))

    cv2.add(container)

    try:
        response = await webhook.send(component=cv2)
        await webhook.close()
    except Exception as e:
        print(e)
        await webhook.close()

asyncio.run(main())
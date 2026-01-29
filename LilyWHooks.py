import aiohttp
import asyncio

WEBHOOK_URL = "https://discord.com/api/webhooks/1438049631803150400/sshwdYrWAW_s7GJaF1Im069cr3b0cPbjMXda0m2NGhVB0xlTgqd9WEhZ0GGOiOF8_GtK"

async def main():
    async with aiohttp.ClientSession() as session:
        payload = {
  "flags": 32768,
  "components": [
    {
      "type": 17,
      "components": [
        {
          "type": 10,
          "content": "Hello"
        }
      ]
    }
  ]
}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{WEBHOOK_URL}?wait=true&with_components=true", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("Sent successfully:", data)
                else:
                    text = await resp.text()
                    print(f"Failed ({resp.status}): {text}")

asyncio.run(main())

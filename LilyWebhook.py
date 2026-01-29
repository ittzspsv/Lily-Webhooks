import aiohttp
import datetime
import json
from typing import Union, List, BinaryIO, Optional


class Component:
    def __init__(self, value: dict):
        self.value = value

class Accessory:
    def __init__(self):
        self.type = 2
        self.style = 5

class Content(Component):
    def __init__(self, content: str):
        super().__init__({
            "type": 10,
            "content": content
        })

class Separator(Component):
    def __init__(self, spacing: bool = False, divider: bool = True):
        super().__init__({
            "type": 14,
            "spacing": 2 if spacing else 1,
            "divider": divider
        })

class ButtonLink(Component, Accessory):
    def __init__(self, label: str | None = None, emoji: str | None = None, url: str = "https://google.com"):
        Accessory.__init__(self)

        payload = {
            "type": self.type,   
            "style": self.style, 
            "url": url,
            "disabled": False
        }

        if label is not None:
            payload["label"] = label

        if emoji is not None:
            payload["emoji"] = {
                "name": emoji,
                "id": None
            }

        if label is None and emoji is None:
            raise ValueError("Either an emoji or a label is necessary")

        Component.__init__(self, payload)

class Thumbnail(Component, Accessory):
    def __init__(self, url: str, spoiler: bool = False):
        if not url:
            raise ValueError("Media link not defined")

        Accessory.__init__(self)

        self.type = 11

        payload = {
            "type": self.type,
            "spoiler": spoiler,
            "media": {
                "url": url
            }
        }

        Component.__init__(self, payload)

class Container(Component):
    def __init__(self, accent_color=None, spoiler: bool = False):
        self.components: list[dict] = []

        payload = {
            "type": 17,
            "spoiler": spoiler,
            "components": self.components
        }

        if accent_color is not None:
            payload["accent_color"] = accent_color

        super().__init__(payload)

    def add(self, component: Component):
        if not isinstance(component, Component):
            raise TypeError("Only Component instances can be added")
        self.components.append(component.value)
        return self

class ComponentBuilder:
    def __init__(self):
        self.components: list[Component] = []

    def add(self, component: Component):
        if not isinstance(component, Component):
            raise TypeError("Only Component instances can be added")
        self.components.append(component)
        return self

    def build(self) -> list[dict]:
        return [component.value for component in self.components]
    
    def legacy_compatible(self) -> bool:
        return bool(self.components) and all(isinstance(component, ButtonLink)
            for component in self.components
        )

class File:
    """
    Data class that represents a file that can be sent to discord.

    Parameters
    ----------
    fp : str or :class:`io.BytesIO`
        A file path or a binary stream that is the file. If a file path
        is provided, this class will open and close the file for you.

    name : str, optional
        The name of the file that discord will use, if not provided,
        defaults to the file name or the binary stream's name.

    """
    def __init__(self, fp: Union[BinaryIO, str], name: str = ''):
        if isinstance(fp, str):
            self.fp = open(fp, 'rb')
            self._manual_opened = True
            self.name = name if name else fp
        else:
            self.fp = fp
            self._manual_opened = False
            self.name = name if name else getattr(fp, 'name', 'filename')

        self._close = self.fp.close
        self.fp.close = lambda: None # prevent aiohttp from closing the file

    def seek(self, offset: int = 0, *args, **kwargs):
        """
        A shortcut to ``self.fp.seek``.

        """
        return self.fp.seek(offset, *args, **kwargs)

    def close(self, force=False) -> None:
        """
        Closes the file if the file was opened by :class:`File`,
        if not, this does nothing.

        Parameters
        ----------
        force: bool
            If set to :class:`True`, force close every file.

        """
        self.fp.close = self._close
        if self._manual_opened or force:
            self.fp.close()

class Embed:
    """
    Class that represents a discord embed
    \nCredits : https://github.com/0arm/dhooks/blob/master/dhooks/embed.py\nModified by SHREESPSV

    Parameters
    -----------
    \*\*title: str, optional
        Defaults to :class:`None`.
        The title of the embed.

    \*\*description: str, optional
        Defaults to :class:`None`.
        The description of the embed.

    \*\*url: str, optional
        URL of the embed. It requires :attr:`title` to be set.

    \*\*timestamp: str, optional
        ``ISO 8601`` timestamp of the embed. If set to a "now",
        the current time is set as the timestamp.
        
    \*\*color: int (or hex), optional
        Color of the embed.
        
    \*\*image_url: str, optional
        URL of the image.
        
    \*\*thumbnail_url: str, optional
        URL of the thumbnail.
        
    """  # noqa: W605
    __slots__ = (
        'color', 'title', 'url', 'author',
        'description', 'fields', 'image',
        'thumbnail', 'footer', 'timestamp',
    )

    def __init__(self, **kwargs):
        """
        Initialises an Embed object.
        """
        self.color = kwargs.get('color')
        if isinstance(self.color, str):
            self.color = int(self.color.lstrip("#"), 16)

        self.title = kwargs.get('title')
        self.url = kwargs.get('url')
        self.description = kwargs.get('description')

        ts = kwargs.get('timestamp')
        if ts == "now":
            self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        elif ts:
            self.timestamp = str(ts)
        else:
            self.timestamp = None

        self.author = None
        self.thumbnail = None
        self.image = None
        self.footer = None
        self.fields = []

        if kwargs.get("image_url"):
            self.set_image(kwargs["image_url"])
        if kwargs.get("thumbnail_url"):
            self.set_thumbnail(kwargs["thumbnail_url"])

    def add_field(self, name: str, value: str, inline: bool = True):
        """
        Adds an embed field.

        Parameters
        ----------
        name: str
            Name attribute of the embed field.

        value: str
            Value attribute of the embed field.

        inline: bool
            Defaults to :class:`True`.
            Whether or not the embed should be inline.

        """
        self.fields.append({
            'name': name,
            'value': value,
            'inline': inline
        })

    def set_author(self, name: str, icon_url: str = None, url: str = None):
        """
        Sets the author of the embed.

        Parameters
        ----------
        name: str
            The author's name.

        icon_url: str, optional
            URL for the author's icon.

        url: str, optional
            URL hyperlink for the author.

        """
        self.author = {'name': name, 'icon_url': icon_url, 'url': url}

    def set_thumbnail(self, url: str):
        """
        Sets the thumbnail of the embed.

        Parameters
        ----------
        url: str
            URL of the thumbnail.

        """
        self.thumbnail = {'url': url}

    def set_image(self, url: str):
        """
        Sets the image of the embed.

        Parameters
        ----------
        url: str
            URL of the image.

        """
        self.image = {'url': url}

    def set_footer(self, text: str, icon_url: str = None):
        """
        Sets the footer of the embed.

        Parameters
        ----------
        text: str
            The footer text.

        icon_url: str, optional
            URL for the icon in the footer.

        """
        self.footer = {'text': text, 'icon_url': icon_url}

    def set_timestamp(self, now: bool = False):
        """
        Sets the timestamp of the embed.

        Parameters
        ----------
        time: str or :class:`datetime.datetime`
            The ``ISO 8601`` timestamp from the embed.

        now: bool
            Defaults to :class:`False`.
            If set to :class:`True` the current time is used for the timestamp.

        """
        self.timestamp = (
            datetime.datetime.utcnow().isoformat() + "Z"
            if now else self.timestamp
        )

    @property
    def embed_dict(self) -> dict:
        data = {}
        for key in self.__slots__:
            value = getattr(self, key)
            if value is None:
                continue
            if key == "fields" and not value:
                continue
            data[key] = value
        return data

class Webhook:
    """
    ### Class that represents a Discord webhook client.

    This class allows sending and editing messages through Discord webhooks

    Parameters
    ----------
    webhook_url: str or List[str]
        Single Webhook url or a List of Webhook URL

    username: str or List[str], optional
        Single username or List of Usernames mapped => webhook url

    avatar_url: str or List[str], optional
        Single avatar_url or List of avatar_url mapped => webhook url
    """
    def __init__(self,webhook_url: Union[str, List[str]],username: Union[str, List[str], None] = None,avatar_url: Union[str, List[str], None] = None):
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url
        self.client_session: aiohttp.ClientSession | None = None

    async def _get_session(self):
        if not self.client_session or self.client_session.closed:
            self.client_session = aiohttp.ClientSession()
        return self.client_session

    def set_username(self, name: str | List[str]) -> None:
        """
        Sets the username/usernames of the webhooks

        Parameters
        ----------
        name: str or List[str]
            Maps an individual username or a list of usernames to the webhook

        Raises
        ------
        ValueError
            If ``name`` is ``None``.
        """
        if not name:
            raise ValueError("URL Not Defined")
        self.username = name

    def set_avatar(self, url: str | List[str]) -> None:
        """
        Sets the avatar url of the webhook/webhooks

        Parameters
        ----------
        url: str or List[str]
            Maps an individual url or a list of url's to the webhook

        Raises
        ------
        ValueError
            If ``url`` is ``None``.
        """
        if not url:
            raise ValueError("URL Not Defined")
        self.avatar_url = url


    def _build_payload(self,content,embed,index: int | None = None,component: ComponentBuilder | None = None):
        payload = {}

        if component is not None:
            if content is not None or embed is not None and not component.legacy_compatible():
                raise ValueError("Component V2 messages cannot include content or embeds")

            if isinstance(component, ComponentBuilder):
                if component.legacy_compatible():
                    components = [
                        {
                            "type": 1,
                            "components": component.build()
                        }
                    ]
                else:
                    components = component.build()

            else:
                raise TypeError("component must be ComponentBuilder")
            payload["flags"] = 32768
            payload["components"] = components

        if self.username is not None:
            payload["username"] = (
                self.username[index] if isinstance(self.username, list) else self.username
            )

        if self.avatar_url is not None:
            payload["avatar_url"] = (
                self.avatar_url[index] if isinstance(self.avatar_url, list) else self.avatar_url
            )

        if content is not None:
            payload["content"] = content

        if embed is not None:
            if isinstance(embed, Embed):
                payload["embeds"] = [embed.embed_dict]
            elif isinstance(embed, list):
                payload["embeds"] = [e.embed_dict for e in embed]
            else:
                raise TypeError("embed must be Embed or list[Embed]")

        return payload


    async def send(self, content: str | None = None, embed: Embed | list[Embed] | None = None, component: ComponentBuilder | None = None, file: Optional[File] = None):
        """
        Sends an webhook response

        Parameters
        ----------
        content: str, optional
            The message content to send.
            If set to ``None``, no text content will be sent.

        embed: Embed or List[Embed], optional
            An embed or a list of embeds to attach to the message.
            If set to ``None``, no embeds will be sent.

        Returns
        -------
        dict or List[dict], depends.
            ``dict`` containing ``message id`` and ``channel id`` the webhook is sent to,
            a ``list`` of ``dict`` containing ``message id`` and ``channel id`` the webhook is sent to,

        Raises
        ------
        ValueError
            If both ``content`` and ``embed`` are ``None``.
        """
        if component is not None and not isinstance(component, ComponentBuilder):
            raise TypeError("component must be a Component or ComponentBuilder instance")

        if component is None and content is None and embed is None:
            raise ValueError("Either content, embed, or component must be provided")


        session = await self._get_session()

        async def _post(url, payload):
            if file:
                form = aiohttp.FormData()
                form.add_field("file", file.fp, filename=file.name)
                form.add_field("payload_json", json.dumps(payload))
                async with session.post(f"{url}?wait=true", data=form) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            else:
                if component:
                    async with session.post(f"{url}?wait=true&with_components=true", json=payload) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                else:
                    async with session.post(f"{url}?wait=true", json=payload) as resp:
                        resp.raise_for_status()
                        return await resp.json()

        if isinstance(self.webhook_url, str):
            payload = self._build_payload(content=content,embed=embed,component=component)
            data = await _post(self.webhook_url, payload)
            return {"id": int(data["id"]), "channel_id": int(data["channel_id"])}

        results = []
        for i, url in enumerate(self.webhook_url):
            payload = self._build_payload(content=content,embed=embed,component=component,index=i)
            data = await _post(url, payload)
            results.append({
                "id": int(data["id"]),
                "channel_id": int(data["channel_id"])
            })

        return results


    async def edit(self, message_id: int, content=None, embed=None):
        """
        
        Edits a previously sent webhook message.

        Parameters
        ----------
        message_id: int
            The message id to edit

        content: str can be optional
            Contents to edit
            can be setted to ``None``

        embed: Embed or List[Embed] can be optional
            An embed or list of embeds to attach to the message.
            If set to ``None``, the embeds will remain unchanged.

        Returns
        -------
        dict
            A dictionary containing the new message ID and channel ID.

        Raises
        ------
        ValueError
            If both ``content`` and ``embed`` are ``None``.
            
        TypeError
            If webhooks are collection (only one webhook are supported)
        """
        if content is None and embed is None:
            raise ValueError("Either content or embed must be provided")

        if isinstance(self.webhook_url, list):
            raise TypeError("edit() supports only one webhook")

        session = await self._get_session()
        payload = self._build_payload(content, embed)

        async with session.patch(
            f"{self.webhook_url}/messages/{message_id}?wait=true",
            json=payload
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return {"id": int(data["id"]), "channel_id": int(data["channel_id"])}

    async def close(self):
        """
        Closes the current client session
        """
        if self.client_session and not self.client_session.closed:
            await self.client_session.close()
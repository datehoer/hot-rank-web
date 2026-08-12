import json
import random
import string
import time

from fastapi import APIRouter

from hotrank.cache import redis_cache
from hotrank.schemas import Feedback, SubscriberRequest, UnsubscribeRequest
from sendEmail import send_email


router = APIRouter()


def generate_uuid() -> str:
    timestamp = int(time.time())
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{timestamp}{random_str}"


@router.post("/subscribe")
async def subscribe(subscriber: SubscriberRequest):
    email = subscriber.email
    exist_email = await redis_cache.hget("subscriberEmail", email)
    if exist_email:
        return {"code": 500, "msg": "error, maybe the email in my database", "data": []}

    uuid = generate_uuid()
    await redis_cache.hset("subscriberEmail", email, uuid)
    send_email(
        "Subscribe",
        f"Thank you for subscribing to my website. Below is your UUID. To unsubscribe, please enter your UUID ({uuid}) and your email ({email}) in the unsubscribe form on the website and submit it. Love from: https://www.hotday.uk ",
        [email],
    )
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "uuid": uuid,
            "email": email,
        },
    }


@router.post("/unsubscribe")
async def unsubscribe(unsub: UnsubscribeRequest):
    email = unsub.email
    uuid = await redis_cache.hget("subscriberEmail", email)
    if uuid:
        if uuid != unsub.uuid:
            return {"code": 500, "msg": "error, maybe the uuid is not correct", "data": []}
        await redis_cache.hdel("subscriberEmail", email)
        send_email(
            "Unsubscribe",
            f"Thank you for subscribing to my website. You have successfully unsubscribed from my website. Love from: https://www.hotday.uk ",
            [email],
        )
        return {"code": 200, "msg": "success", "data": []}
    return {"code": 500, "msg": "error, maybe the email not in my database", "data": []}


@router.get("/rankCopyWriting")
async def get_copywriting():
    data = await redis_cache.srandmember("copywriting")
    return {"code": 200, "msg": "success", "data": data}


@router.get("/yellowCalendar")
async def get_yellow_calendar():
    data = await redis_cache.get("yellowCalendar")
    return {"code": 200, "msg": "success", "data": json.loads(data)}


@router.get("/music")
async def get_music():
    data = await redis_cache.get("music")
    return {"code": 200, "msg": "success", "data": json.loads(data)}


@router.get("/avatar")
async def get_avatar():
    data = await redis_cache.srandmember("avatar")
    return {"code": 200, "msg": "success", "data": data}


@router.get("/username")
async def get_username():
    data = await redis_cache.srandmember("username")
    return {"code": 200, "msg": "success", "data": data}


@router.post("/feedback")
async def post_feedback(feedback: Feedback):
    send_email(feedback.subject, feedback.content, ["datehoer@gmail.com"])
    return {"code": 200, "msg": "success"}


@router.get("/get_cards")
async def get_cards():
    data = await redis_cache.get("card_table")
    return {"code": 200, "msg": "success", "data": json.loads(data)}

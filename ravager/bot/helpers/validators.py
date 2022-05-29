from ravager.bot.helpers.constants import *
from functools import wraps
from ravager.celery_tasks.tasks import app
from ravager.database.users import UserData
from ravager.database.helpers.structs import UserStruct
import logging
from ravager.config import HEROKU_APP, HEROKU_API_TOKEN
from ravager.helpers.heroku import get_uptime
import time

logger = logging.getLogger(__file__)


def restricted(handlers):
    wraps(handlers)

    def wrapper(self, update, context, *args, **kwargs):
        user_id = update.effective_user.id
        user = UserData(user=self.user).get_user()
        if not user.is_admin:
            logger.error("Unauthorized access denied for {}.".format(user_id))
            return
        return handlers(self, update, context, *args, **kwargs)

    return wrapper


def check_filters(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            tg_user = UserStruct(user_id=str(update.effective_chat.id))
            chat_id = str(update.effective_chat.id)
            user_id = str(update.effective_user.id)
            personal = False
            user = UserData(tg_user).get_user()
            if not user:
                self.user = tg_user
                return handlers(self, update, context, *args, **kwargs)
            if chat_id == user_id:
                personal = True

            if "is_start" in dkwargs:
                start = bool(dkwargs["is_start"])
            else:
                start = False
            allowlist_status = bool(os.environ.get("ALLOWLIST"))
            blocked = bool(user.blocked)
            if personal:
                if allowlist_status and not start and blocked:

                    update.message.reply_text(quote=True,
                                              text="You are blocked from further usage,for more info contact admin.")
                    logger.error("Unauthorized access denied for {}.".format(user_id))
                    if "is_convo" in dkwargs:
                        return END
                    return
            else:
                if allowlist_status and not start and blocked:
                    update.message.reply_text(quote=True,
                                              text="This group or the particular user has been blacklisted,"
                                                   "for further info contact admin.")
                    logger.error("Unauthorized access denied for {}.".format(user_id))
                    if "is_convo" in dkwargs:
                        return END
                    return
            return handlers(self, update, context, *args, **kwargs)

        return wrapper

    return decorator


def check_celery_queue(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            i = app.control.inspect()
            reserved = i.reserved()
            if reserved is not None:
                worker_name = list(reserved.keys())[0]
                reserved_tasks = len(reserved[worker_name])
                if reserved_tasks >= 4:
                    update.message.reply_text(quote=True, text="Too many tasks in queue,try again later")
                    if "is_convo" in dkwargs:
                        return END
                    return
            return handlers(self, update, context, *args, *kwargs)

        return wrapper

    return decorator


def check_authorized(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            tg_user = UserStruct(user_id=str(update.effective_chat.id))
            user = UserData(user=tg_user).get_user()
            if user is None or not user.authorized:
                update.message.reply_text(quote=True,
                                          text="The bot doesn't have access to your google account,authorize?")
                if "is_convo" in dkwargs:
                    return END
                return

            return handlers(self, update, context, *args, **kwargs)

        return wrapper

    return decorator


def check_drive_selection(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            tg_user = UserStruct(user_id=str(update.effective_chat.id))
            user = UserData(user=tg_user).get_user()
            if user.storage_type is None:
                update.message.reply_text(text="Default drive is not set", quote=True)
                return END

            return handlers(self, update, context, *args, **kwargs)

        return wrapper

    return decorator


def give_uptime(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            if HEROKU_APP and HEROKU_API_TOKEN is not None:
                uptime = get_uptime().total_seconds()
                shutdown_time = time.strftime("%H:%M:%S", time.gmtime(uptime))
                update.message.reply_text(text="Ravager will restart in approx {}".format(shutdown_time), quote=True)

            return handlers(self, update, context, *args, **kwargs)

        return wrapper

    return decorator


def check_group_admin(*dargs, **dkwargs):
    def decorator(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            if chat_id != user_id:
                admins = update.message.bot.get_chat_administrators(chat_id=chat_id)
                for i in admins:
                    if str(user_id) == str(i.user.id):
                        return handlers(self, update, context, *args, **kwargs)
                else:
                    update.message.reply_text(quote=True, text="This command can only be executed by an admin")
                    return END
            return handlers(self, update, context, *args, **kwargs)

        return wrapper

    return decorator

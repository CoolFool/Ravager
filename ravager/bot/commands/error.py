import logging
import traceback

logger = logging.getLogger(__file__)


def error_handler(update, context):
    update.message.reply_text(quote=True, text="Error Occurred while handling request")
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(tb_string)

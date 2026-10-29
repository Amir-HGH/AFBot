import asyncio
import aiohttp
from telegram.ext import (
    CommandHandler , MessageHandler , filters , ContextTypes,
    InlineKeyboardButton , InlineKeyboardMarkup , 
    ConversationHandler,CallbackQueryHandler
)
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class Login : 

    def __init__(self,database):
        
        self.database = database

        self.CHOICE = 1
        self.GET_USERNAME = 2
        self.GET_USER_PROFILE = 3 
        self.GET_USER_PROFILE_2 = 4 
        self.FINISH = 5


    # Level methods _________________________________________________________

    async def start (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        try :

            login_b = InlineKeyboardButton(
                "Yes",
                callback_data = "login"
            )
            build_account_b = InlineKeyboardButton(
                "No",
                callback_data = "build_account"
            )

            keyboard = InlineKeyboardMarkup([[login_b,build_account_b]])

            await update.effective_message.reply_text(
                "آیا حساب کاربری دارید ؟ ",
                reply_markup = keyboard
            )

            return self.CHOICE

        except Exception : 

            logger.exception("start")
            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )

            return ConversationHandler.END


    async def choice (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        try : 

            btn = update.callback_query

            await btn.answer()
            context.user_data["choice"] = btn.data

            return self.GET_USERNAME

        except Exception : 

            logger.exception("choice")
            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )

            return ConversationHandler.END


    async def get_username (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        try : 

            await update.effective_message.reply_text(
                "لطفا یوزر نیم انتخابی خود را وارد کنید "
            )

            return self.GET_USER_PROFILE

        except Exception : 

            logger.exception("get username")
            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )

            return self.GET_USERNAME


    async def get_u_profile (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        username = update.message.text

        exist_username = self.database.exist(
            "users",
            ["1"],
            ["username"],
            [[username]]
        )
        if isinstance(exist_username, dict) and "error" in exist_username : 

            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )
            return self.GET_USER_PROFILE

        try :

            if context.user_data["choice"] == "login" : 

                if exist_username is True : 
                    
                    context.user_data["username"] = username
                    return await self.finish(update,context)
                
                else : 

                    await update.effective_message.reply_text(
                        "یوزر نیم موجود نیست "
                    )
                    return self.GET_USERNAME

            else : 

                if exist_username is False : context.user_data["username"] = username

                else : 

                    await update.effective_message.reply_text(
                        "این یوزر نیم قبلا توسط کاربر دیگری انتخاب شده است "
                    )
                    return self.GET_USERNAME

                await update.effective_message.reply_text(
                    "لطفا یک جمله برای معرفی علایق خود به من بدهید تا شما را بهتر بشناسم "
                )
                
                return self.GET_USER_PROFILE_2

        except Exception : 

            logger.exception("get u profile")
            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )

            return self.GET_USER_PROFILE


    async def get_u_profile_2 (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        try : 

            u_profile = update.message.text

            context.user_data["user_profile"] = u_profile

            return await self.finish(update,context)

        except Exception : 

            logger.exception("get u profile 2 ")
            await update.effective_message.reply_text(
                "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
            )

            return self.GET_USER_PROFILE_2


    async def finish (self,update,context : ContextTypes.DEFAULT_TYPE) : 

        choice = context.user_data["choice"]
        conversation_id = 1

        if choice == "login" : 

            result = self.database.login_process(context.user_data["username"])
            
            if result == False : 
 
                await update.effective_message.reply_text(
                    "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
                )
                return ConversationHandler.END

            conversation_id = result

        elif choice == "build_account" : 

            result = self.database.build_account_process(
                context.user_data["username"],
                context.user_data["user_profile"]
            )
            
            if result == False : 
                
                await update.effective_message.reply_text(
                    "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
                )
                return ConversationHandler.END

        context.user_data["conversation_id"] = conversation_id
        
        await update.effective_message.reply_text(
            "لاگین با موفقیت کامل شد "
        )

        return ConversationHandler.END


    # Main method _________________________________________________________

    def build_ch (self) : 

        try : 

            return ConversationHandler(
                entry_points=[
                    CommandHandler("start",self.start)
                ],
                states={
                    self.CHOICE : [
                        CallbackQueryHandler(self.choice,pattern="^(login|build_account)$")
                    ],
                    self.GET_USERNAME : [
                        MessageHandler(filters.TEXT & ~filters.COMMAND,self.get_username)
                    ],
                    self.GET_USER_PROFILE : [
                        MessageHandler(filters.TEXT & ~filters.COMMAND,self.get_u_profile)
                    ],
                    self.GET_USER_PROFILE_2 :[
                       MessageHandler(filters.TEXT & ~filters.COMMAND,self.get_u_profile_2) 
                    ]
                }
            )

        except Exception : 

            logger.exception("get u profile 2 ")
            return False



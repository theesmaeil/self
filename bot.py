import asyncio
import os
import random
import re
from datetime import datetime
import pytz
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ==================== تنظیمات اولیه ====================
API_ID = #api_id
API_HASH = '#id_hash'
SESSION_NAME = 'noghtchannel'

app = Client(SESSION_NAME, API_ID, API_HASH)
scheduler = AsyncIOScheduler()

# ==================== متغیرهای وضعیت ====================
status_time_bio = 'off'       # 'on' یا 'off'
bio_text = 'bye bye 🤫🧏'
status_time_name = 'off'      # 'on' یا 'off'

# ایجاد پوشه دانلود
os.makedirs("downloads", exist_ok=True)

# ==================== توابع کمکی (به‌روزرسانی زمان) ====================
async def update_bio_with_time():
    if status_time_bio == 'on':
        try:
            tz = pytz.timezone('Asia/Tehran')
            now = datetime.now(tz).strftime("%H:%M")
            await app.update_profile(bio=f'{now} | {bio_text}')
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except RPCError as e:
            print(f"⚠️ خطا در به‌روزرسانی بیو: {e}")

async def update_name_with_time():
    if status_time_name == 'on':
        try:
            tz = pytz.timezone('Asia/Tehran')
            now = datetime.now(tz).strftime("%H:%M")
            await app.update_profile(last_name=now)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except RPCError as e:
            print(f"⚠️ خطا در به‌روزرسانی نام: {e}")

# ==================== ذخیره خودکار عکس/ویدیوی تایم‌دار ====================
@app.on_message(filters.photo & filters.private)
async def save_timed_photo(client, message):
    if message.photo.ttl_seconds:
        rand = random.randint(1000, 9999999)
        path = f"downloads/photo-{rand}.png"
        try:
            await app.download_media(message.photo.file_id, file_name=path)
            await app.send_photo("me", photo=path,
                                 caption=f"🖼 عکس تایم‌دار دریافت شد\n⏳ {message.photo.ttl_seconds}s")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره عکس: {e}")
        finally:
            if os.path.exists(path):
                os.remove(path)

@app.on_message(filters.video & filters.private)
async def save_timed_video(client, message):
    if message.video.ttl_seconds:
        rand = random.randint(1000, 9999999)
        path = f"downloads/video-{rand}.mp4"
        try:
            await app.download_media(message.video.file_id, file_name=path)
            await app.send_video("me", video=path,
                                 caption=f"🎥 ویدیو تایم‌دار دریافت شد\n⏳ {message.video.ttl_seconds}s")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره ویدیو: {e}")
        finally:
            if os.path.exists(path):
                os.remove(path)

# ==================== دستورات اصلی (بدون نقطه) ====================

@app.on_message(filters.me & filters.regex('(?i)^help$'))
async def cmd_help(client, message):
    help_text = (
        "📖 **راهنمای سلف**\n\n"
        "**دستورات بدون نقطه**\n"
        "`bot` – وضعیت آنلاین بودن\n"
        "`status` – وضعیت تنظیمات\n"
        "`timebio on/off` – فعال/غیرفعال زمان در بیو\n"
        "`timename on/off` – فعال/غیرفعال زمان در نام\n"
        "`setbio` (ریپلای روی متن) – تنظیم بیو\n"
        "`save` (ریپلای روی پیام) – ذخیره در Saved Messages\n"
        "`id` (ریپلای روی کاربر) – اطلاعات کاربر\n"
        "`data` (ریپلای روی پیام) – اطلاعات خام پیام\n"
        "`help` – این راهنما\n\n"
        "📌 عکس/ویدیوهای تایم‌دار به‌طور خودکار ذخیره می‌شوند."
    )
    try:
        await app.edit_message_text(message.chat.id, message.id, help_text)
        await asyncio.sleep(60)
        await app.delete_messages(message.chat.id, message.id, revoke=True)
    except Exception as e:
        print(f"⚠️ خطا در help: {e}")

@app.on_message(filters.me & filters.regex('(?i)^bot$'))
async def cmd_bot(client, message):
    try:
        await app.edit_message_text(
            message.chat.id, message.id,
            f"✅ **<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> آنلاین است.**"
        )
        await asyncio.sleep(20)
        await app.delete_messages(message.chat.id, message.id, revoke=True)
    except Exception as e:
        print(f"⚠️ خطا در دستور bot: {e}")

@app.on_message(filters.me & filters.regex('(?i)^status$'))
async def cmd_status(client, message):
    text = (
        "📊 **وضعیت سلف**\n\n"
        f"⏰ نمایش زمان در بیو: `{status_time_bio}`\n"
        f"⏰ نمایش زمان در نام: `{status_time_name}`\n"
        f"📝 بیو فعلی: `{bio_text}`"
    )
    try:
        await app.edit_message_text(message.chat.id, message.id, text)
    except Exception as e:
        print(f"⚠️ خطا در status: {e}")

@app.on_message(filters.me & filters.regex('(?i)^timebio (on|off)$'))
async def cmd_timebio(client, message):
    global status_time_bio
    action = re.search(r'(?i)^timebio (on|off)$', message.text).group(1).lower()
    if action == 'on':
        if status_time_bio == 'on':
            await app.edit_message_text(message.chat.id, message.id, "⏰ قبلاً فعال است.")
            return
        status_time_bio = 'on'
        scheduler.add_job(update_bio_with_time, "interval", minutes=1)
        await app.edit_message_text(message.chat.id, message.id, "✅ نمایش زمان در بیو فعال شد.")
    else:  # off
        if status_time_bio == 'off':
            await app.edit_message_text(message.chat.id, message.id, "⏰ قبلاً غیرفعال است.")
            return
        status_time_bio = 'off'
        for job in scheduler.get_jobs():
            if job.func == update_bio_with_time:
                job.remove()
        await app.update_profile(bio=f'--:-- | {bio_text}')
        if status_time_name == 'on' and not any(j.func == update_name_with_time for j in scheduler.get_jobs()):
            scheduler.add_job(update_name_with_time, "interval", minutes=1)
        await app.edit_message_text(message.chat.id, message.id, "❌ نمایش زمان در بیو غیرفعال شد.")
    await asyncio.sleep(15)
    await app.delete_messages(message.chat.id, message.id, revoke=True)

@app.on_message(filters.me & filters.regex('(?i)^timename (on|off)$'))
async def cmd_timename(client, message):
    global status_time_name
    action = re.search(r'(?i)^timename (on|off)$', message.text).group(1).lower()
    if action == 'on':
        if status_time_name == 'on':
            await app.edit_message_text(message.chat.id, message.id, "⏰ قبلاً فعال است.")
            return
        status_time_name = 'on'
        scheduler.add_job(update_name_with_time, "interval", minutes=1)
        await app.edit_message_text(message.chat.id, message.id, "✅ نمایش زمان در نام فعال شد.")
    else:  # off
        if status_time_name == 'off':
            await app.edit_message_text(message.chat.id, message.id, "⏰ قبلاً غیرفعال است.")
            return
        status_time_name = 'off'
        for job in scheduler.get_jobs():
            if job.func == update_name_with_time:
                job.remove()
        await app.update_profile(last_name='--:--')
        if status_time_bio == 'on' and not any(j.func == update_bio_with_time for j in scheduler.get_jobs()):
            scheduler.add_job(update_bio_with_time, "interval", minutes=1)
        await app.edit_message_text(message.chat.id, message.id, "❌ نمایش زمان در نام غیرفعال شد.")
    await asyncio.sleep(15)
    await app.delete_messages(message.chat.id, message.id, revoke=True)

@app.on_message(filters.me & filters.reply & filters.regex('(?i)^setbio$'))
async def cmd_setbio(client, message):
    global bio_text
    if not message.reply_to_message or not message.reply_to_message.text:
        await app.edit_message_text(message.chat.id, message.id, "⚠️ لطفاً روی یک پیام متنی ریپلای کنید.")
        return
    new_bio = message.reply_to_message.text
    bio_text = new_bio
    try:
        if status_time_bio == 'on':
            tz = pytz.timezone('Asia/Tehran')
            now = datetime.now(tz).strftime("%H:%M")
            await app.update_profile(bio=f'{now} | {new_bio}')
        else:
            await app.update_profile(bio=f'--:-- | {new_bio}')
        await app.edit_message_text(message.chat.id, message.id, "✅ بیو با موفقیت تنظیم شد.")
    except Exception as e:
        await app.edit_message_text(message.chat.id, message.id, f"⚠️ خطا در تنظیم بیو: {e}")
    await asyncio.sleep(15)
    await app.delete_messages(message.chat.id, message.id, revoke=True)

@app.on_message(filters.me & filters.reply & filters.regex('(?i)^save$'))
async def cmd_save(client, message):
    try:
        await app.copy_message("me", message.chat.id, message.reply_to_message_id)
        await app.delete_messages(message.chat.id, message.id, revoke=True)
    except Exception as e:
        await app.edit_message_text(message.chat.id, message.id, f"⚠️ خطا: {e}")
        await asyncio.sleep(5)
        await app.delete_messages(message.chat.id, message.id, revoke=True)

@app.on_message(filters.me & filters.reply & filters.regex('(?i)^id$'))
async def cmd_id(client, message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await app.edit_message_text(message.chat.id, message.id, "⚠️ روی پیام یک کاربر ریپلای کنید.")
        return
    user = message.reply_to_message.from_user
    text = (
        f"👤 **{user.first_name}**\n"
        f"🆔 `{user.id}`\n"
        f"📛 @{user.username or 'ندارد'}\n"
        f"🔹 خودمان: `{user.is_self}`\n"
        f"🔹 مخاطب: `{user.is_contact}`\n"
        f"🔹 حذف‌شده: `{user.is_deleted}`\n"
        f"🔹 ربات: `{user.is_bot}`\n"
        f"🔹 اسکم: `{user.is_scam}`\n"
        f"🔹 فیک: `{user.is_fake}`\n"
        f"🔹 پریمیوم: `{user.is_premium}`\n"
        f"📌 آخرین بازدید: `{user.status}`"
    )
    try:
        await app.edit_message_text(message.chat.id, message.id, text)
    except Exception as e:
        print(f"⚠️ خطا در id: {e}")

@app.on_message(filters.me & filters.reply & filters.regex('(?i)^data$'))
async def cmd_data(client, message):
    if not message.reply_to_message:
        await app.edit_message_text(message.chat.id, message.id, "⚠️ روی یک پیام ریپلای کنید.")
        return
    try:
        await app.edit_message_text(
            message.chat.id, message.id,
            f"```\n{message.reply_to_message}\n```"
        )
    except Exception as e:
        print(f"⚠️ خطا در data: {e}")

# ==================== تابع اصلی ====================
async def main_async():
    scheduler.start()
    await app.start()
    print("✅ ربات با موفقیت راه‌اندازی شد.")
    print("📌 برای تست، دستور 'help' را در Saved Messages ارسال کنید.")
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        app.run(main_async())
    except KeyboardInterrupt:
        print("\n⏹ در حال توقف...")
    finally:
        scheduler.shutdown()
        print("⏹ ربات متوقف شد.")
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8704940063:AAEhMgGQmHmVkdFQL15QnSf3AXrh2IPj_s0"
ADMIN_ID = 5435228160

os.makedirs("pdfs", exist_ok=True)

if os.path.exists("lessons.json"):
    with open("lessons.json", "r") as f:
        lessons = json.load(f)
else:
    lessons = {
        "التاسع": {"فيزياء": {}, "كيمياء": {}},
        "البكالوريا": {"فيزياء": {}, "كيمياء": {}}
    }

def save_lessons():
    with open("lessons.json", "w") as f:
        json.dump(lessons, f)

# ========== القائمة الرئيسية ==========
async def main_menu(update, context, message=None):
    user_id = update.effective_user.id
    text = "📘 الفيزياء والكيمياء - سوريا\n👨‍🏫 الأستاذ: علي سليمان\n\n🌟 أهلاً بك في البوت التعليمي\n\nاختر صفك:"
    keyboard = [
        [InlineKeyboardButton("🎓 الصف التاسع", callback_data="grade_التاسع")],
        [InlineKeyboardButton("🎓 البكالوريا العلمي", callback_data="grade_البكالوريا")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ إدارة", callback_data="admin")])
    
    if message:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    await main_menu(update, context)

async def callback(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = update.effective_user.id

    # ========== رجوع للرئيسية ==========
    if data == "main_menu":
        await main_menu(update, context, q.message)
        return

    # ========== عرض المواد ==========
    if data.startswith("grade_"):
        grade = data[6:]
        keyboard = [
            [InlineKeyboardButton("📘 فيزياء", callback_data=f"sub_{grade}_فيزياء")],
            [InlineKeyboardButton("🧪 كيمياء", callback_data=f"sub_{grade}_كيمياء")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
        await q.edit_message_text(f"🎓 {grade}\nاختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ========== عرض الدروس ==========
    if data.startswith("sub_"):
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        subject_lessons = lessons.get(grade, {}).get(subject, {})
        
        keyboard = []
        for name in subject_lessons:
            keyboard.append([InlineKeyboardButton(f"📄 {name}", callback_data=f"view_{grade}_{subject}_{name}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"grade_{grade}")])
        
        if not subject_lessons:
            await q.edit_message_text(f"📭 لا يوجد دروس في {subject} - {grade}", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await q.edit_message_text(f"📚 {subject} - {grade}\nاختر الدرس:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ========== عرض الملف ==========
    if data.startswith("view_"):
        parts = data.split("_", 3)
        grade = parts[1]
        subject = parts[2]
        name = parts[3]
        path = lessons.get(grade, {}).get(subject, {}).get(name)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                await q.message.reply_document(f, caption=f"📄 {name}\n📚 {subject} - {grade}\n👨‍🏫 علي سليمان")
        else:
            await q.edit_message_text("❌ الملف غير موجود")
        return

    # ========== لوحة الإدارة ==========
    if data == "admin" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة درس", callback_data="add")],
            [InlineKeyboardButton("🗑 حذف درس", callback_data="del")],
            [InlineKeyboardButton("📊 إحصائيات", callback_data="stats")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
        await q.edit_message_text("⚙️ لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ========== إضافة درس ==========
    if data == "add" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="add_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="add_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء", callback_data="add_البكالوريا_فيزياء")],
            [InlineKeyboardButton("البكالوريا - كيمياء", callback_data="add_البكالوريا_كيمياء")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin")]
        ]
        await q.edit_message_text("📤 اختر مكان حفظ الدرس:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("add_") and user_id == ADMIN_ID:
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        context.user_data["add_grade"] = grade
        context.user_data["add_subject"] = subject
        await q.edit_message_text(f"📤 أرسل ملف PDF لـ:\n{grade} - {subject}")
        context.user_data["waiting_file"] = True
        return

    # ========== حذف درس ==========
    if data == "del" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="del_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="del_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء", callback_data="del_البكالوريا_فيزياء")],
            [InlineKeyboardButton("البكالوريا - كيمياء", callback_data="del_البكالوريا_كيمياء")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin")]
        ]
        await q.edit_message_text("🗑 اختر الصف والمادة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("del_") and user_id == ADMIN_ID:
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        subject_lessons = lessons.get(grade, {}).get(subject, {})
        keyboard = []
        for name in subject_lessons:
            keyboard.append([InlineKeyboardButton(f"🗑 {name}", callback_data=f"delete_{grade}_{subject}_{name}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin")])
        if not subject_lessons:
            await q.edit_message_text(f"📭 لا يوجد دروس في {grade} - {subject}", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await q.edit_message_text(f"🗑 اختر درساً للحذف:\n{grade} - {subject}", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("delete_") and user_id == ADMIN_ID:
        parts = data.split("_", 3)
        grade = parts[1]
        subject = parts[2]
        name = parts[3]
        if name in lessons.get(grade, {}).get(subject, {}):
            path = lessons[grade][subject][name]
            if os.path.exists(path):
                os.remove(path)
            del lessons[grade][subject][name]
            save_lessons()
            await q.edit_message_text(f"✅ تم حذف: {name}")
        return

    # ========== إحصائيات ==========
    if data == "stats" and user_id == ADMIN_ID:
        t1 = len(lessons["التاسع"]["فيزياء"])
        t2 = len(lessons["التاسع"]["كيمياء"])
        b1 = len(lessons["البكالوريا"]["فيزياء"])
        b2 = len(lessons["البكالوريا"]["كيمياء"])
        total = t1 + t2 + b1 + b2
        text = f"📊 الإحصائيات\n\nالتاسع - فيزياء: {t1}\nالتاسع - كيمياء: {t2}\nالبكالوريا - فيزياء: {b1}\nالبكالوريا - كيمياء: {b2}\n\nالمجموع: {total}"
        await q.edit_message_text(text)
        return

async def handle_file(update, context):
    if context.user_data.get("waiting_file"):
        doc = update.message.document
        name = doc.file_name
        if not name.endswith(".pdf"):
            await update.message.reply_text("❌ أرسل ملف PDF فقط")
            return
        file_obj = await doc.get_file()
        path = f"pdfs/{name}"
        await file_obj.download_to_drive(path)
        context.user_data["temp_path"] = path
        await update.message.reply_text("✅ تم استلام PDF\n📝 أرسل الآن اسم الدرس:")
        context.user_data["waiting_name"] = True
        context.user_data["waiting_file"] = False

async def handle_text(update, context):
    if context.user_data.get("waiting_name"):
        name = update.message.text
        path = context.user_data.get("temp_path")
        grade = context.user_data.get("add_grade")
        subject = context.user_data.get("add_subject")
        if path and name and grade and subject:
            lessons[grade][subject][name] = path
            save_lessons()
            await update.message.reply_text(f"✅ تم حفظ الدرس: {name}\n📚 {subject} - {grade}")
            context.user_data.clear()

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("✅ البوت يعمل")
app.run_polling()

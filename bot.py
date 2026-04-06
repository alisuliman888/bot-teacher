import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8704940063:AAEhMgGQmHmVkdFQL15QnSf3AXrh2IPj_s0"
ADMIN_ID = 5435228160

os.makedirs("pdfs", exist_ok=True)
os.makedirs("paid_pdfs", exist_ok=True)

# تحميل الدروس المجانية
if os.path.exists("lessons.json"):
    with open("lessons.json", "r") as f:
        lessons = json.load(f)
else:
    lessons = {
        "التاسع": {"فيزياء": {}, "كيمياء": {}},
        "البكالوريا": {"فيزياء": {}, "كيمياء": {}}
    }

# تحميل الدروس المدفوعة
if os.path.exists("paid_lessons.json"):
    with open("paid_lessons.json", "r") as f:
        paid_lessons = json.load(f)
else:
    paid_lessons = {
        "التاسع": {"فيزياء": {}, "كيمياء": {}},
        "البكالوريا": {"فيزياء": {}, "كيمياء": {}}
    }

# تحميل المستخدمين المدفوعين
if os.path.exists("premium_users.json"):
    with open("premium_users.json", "r") as f:
        premium_users = json.load(f)
else:
    premium_users = []

def save_lessons():
    with open("lessons.json", "w") as f:
        json.dump(lessons, f)

def save_paid_lessons():
    with open("paid_lessons.json", "w") as f:
        json.dump(paid_lessons, f)

def save_premium_users():
    with open("premium_users.json", "w") as f:
        json.dump(premium_users, f)

# ========== القائمة الرئيسية ==========
async def main_menu(update, context, message=None):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    text = "📘 الفيزياء والكيمياء - سوريا\n👨‍🏫 الأستاذ: علي سليمان\n\n🌟 مرحباً بك في المراجعة النهائية 🌟\n\n"
    
    if is_premium:
        text += "✅ أنت مشترك في الباقة الممتازة\nلديك حق الوصول لجميع المحتوى.\n\n"
    else:
        text += "📚 المحتوى المجاني:\n✅ مكثف الوحدة الأولى\n✅ اختبار تجريبي واحد\n\n🔒 المحتوى المدفوع (5000 ليرة):\n🔒 مكثفات الوحدات 2-5\n🔒 5 اختبارات نهائية\n🔒 حلول نموذجية\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🎓 الصف التاسع", callback_data="grade_التاسع")],
        [InlineKeyboardButton("🎓 البكالوريا العلمي", callback_data="grade_البكالوريا")]
    ]
    
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ إدارة", callback_data="admin")])
    
    if not is_premium:
        keyboard.append([InlineKeyboardButton("💰 شراء الحزمة الكاملة", callback_data="buy_package")])
    
    if message:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    await main_menu(update, context)

# ========== شراء الحزمة ==========
async def buy_package(update, context):
    user_id = update.effective_user.id
    text = """
💰 *طريقة الشراء:*

1️⃣ حول مبلغ 5000 ليرة إلى الرقم:
   `09XXXXXXXX` (MTN أو سيريتل كاش)

2️⃣ أرسل صورة الإشعار هنا.

3️⃣ انتظر التفعيل (خلال 24 ساعة).

📞 للاستفسار: @AliSuliman

بعد التفعيل، ستظهر لك جميع الدروس والمكثفات.
"""
    await update.callback_query.edit_message_text(text, parse_mode="Markdown")

# ========== عرض المواد ==========
async def show_subjects(update, context, grade, message):
    keyboard = [
        [InlineKeyboardButton("📘 فيزياء", callback_data=f"sub_{grade}_فيزياء")],
        [InlineKeyboardButton("🧪 كيمياء", callback_data=f"sub_{grade}_كيمياء")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
    ]
    await message.edit_text(f"🎓 {grade}\nاختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض الدروس ==========
async def show_lessons(update, context, grade, subject, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_lessons = lessons.get(grade, {}).get(subject, {})
    paid_lessons_data = paid_lessons.get(grade, {}).get(subject, {})
    
    keyboard = []
    
    # إضافة الدروس المجانية
    for name in free_lessons:
        keyboard.append([InlineKeyboardButton(f"📄 {name} (مجاني)", callback_data=f"view_free_{grade}_{subject}_{name}")])
    
    # إضافة الدروس المدفوعة (للمشتركين فقط)
    if is_premium:
        for name in paid_lessons_data:
            keyboard.append([InlineKeyboardButton(f"🔓 {name} (مدفوع)", callback_data=f"view_paid_{grade}_{subject}_{name}")])
    else:
        for name in paid_lessons_data:
            keyboard.append([InlineKeyboardButton(f"🔒 {name} (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"grade_{grade}")])
    
    if not free_lessons and not paid_lessons_data:
        await message.edit_text(f"📭 لا يوجد دروس في {subject} - {grade}", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        title = f"📚 {subject} - {grade}"
        if not is_premium and paid_lessons_data:
            title += "\n\n🔒 دروس مقفلة. اشترك لفتحها: /start"
        await message.edit_text(title, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض الملف ==========
async def view_file(update, context, file_path, caption):
    q = update.callback_query
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            await q.message.reply_document(f, caption=caption)
    else:
        await q.edit_message_text("❌ الملف غير موجود")

async def callback(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = update.effective_user.id

    if data == "main_menu":
        await main_menu(update, context, q.message)
        return

    if data == "buy_package":
        await buy_package(update, context)
        return

    if data == "not_premium":
        await q.edit_message_text("🔒 هذا الدرس للمشتركين فقط.\n\nلشراء الحزمة اضغط /start ثم اختر 💰 شراء الحزمة الكاملة")
        return

    if data.startswith("grade_"):
        grade = data[6:]
        await show_subjects(update, context, grade, q.message)
        return

    if data.startswith("sub_"):
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        await show_lessons(update, context, grade, subject, q.message)
        return

    if data.startswith("view_free_"):
        parts = data.split("_", 3)
        grade = parts[2]
        subject = parts[3]
        name = "_".join(parts[4:]) if len(parts) > 4 else parts[3]
        path = lessons.get(grade, {}).get(subject, {}).get(name)
        await view_file(update, context, path, f"📄 {name} (مجاني)\n📚 {subject} - {grade}")
        return

    if data.startswith("view_paid_"):
        if user_id not in premium_users:
            await q.edit_message_text("🔒 هذا الدرس للمشتركين فقط.\n\nلشراء الحزمة اضغط /start ثم اختر 💰 شراء الحزمة الكاملة")
            return
        parts = data.split("_", 3)
        grade = parts[2]
        subject = parts[3]
        name = "_".join(parts[4:]) if len(parts) > 4 else parts[3]
        path = paid_lessons.get(grade, {}).get(subject, {}).get(name)
        await view_file(update, context, path, f"📄 {name}\n📚 {subject} - {grade}")
        return

    # ========== لوحة الإدارة ==========
    if data == "admin" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة درس مجاني", callback_data="add_free")],
            [InlineKeyboardButton("💰 إضافة درس مدفوع", callback_data="add_paid")],
            [InlineKeyboardButton("🗑 حذف درس", callback_data="del")],
            [InlineKeyboardButton("👥 تفعيل مستخدم", callback_data="activate_user")],
            [InlineKeyboardButton("📊 إحصائيات", callback_data="stats")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
        await q.edit_message_text("⚙️ لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # إضافة درس مجاني
    if data == "add_free" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="addfree_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="addfree_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء", callback_data="addfree_البكالوريا_فيزياء")],
            [InlineKeyboardButton("البكالوريا - كيمياء", callback_data="addfree_البكالوريا_كيمياء")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin")]
        ]
        await q.edit_message_text("📤 اختر مكان حفظ الدرس المجاني:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("addfree_") and user_id == ADMIN_ID:
        parts = data.split("_")
        context.user_data["add_grade"] = parts[1]
        context.user_data["add_subject"] = parts[2]
        context.user_data["add_type"] = "free"
        await q.edit_message_text(f"📤 أرسل ملف PDF مجاني لـ:\n{parts[1]} - {parts[2]}")
        context.user_data["waiting_file"] = True
        return

    # إضافة درس مدفوع
    if data == "add_paid" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="addpaid_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="addpaid_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء", callback_data="addpaid_البكالوريا_فيزياء")],
            [InlineKeyboardButton("البكالوريا - كيمياء", callback_data="addpaid_البكالوريا_كيمياء")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin")]
        ]
        await q.edit_message_text("💰 اختر مكان حفظ الدرس المدفوع:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("addpaid_") and user_id == ADMIN_ID:
        parts = data.split("_")
        context.user_data["add_grade"] = parts[1]
        context.user_data["add_subject"] = parts[2]
        context.user_data["add_type"] = "paid"
        await q.edit_message_text(f"💰 أرسل ملف PDF مدفوع لـ:\n{parts[1]} - {parts[2]}")
        context.user_data["waiting_file"] = True
        return

    # تفعيل مستخدم
    if data == "activate_user" and user_id == ADMIN_ID:
        await q.edit_message_text("👤 أرسل معرف المستخدم (user_id) لتفعيل اشتراكه.\n\nمثال: 5435228160")
        context.user_data["waiting_activation"] = True
        return

    # حذف درس
    if data == "del" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="dellist_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="dellist_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء", callback_data="dellist_البكالوريا_فيزياء")],
            [InlineKeyboardButton("البكالوريا - كيمياء", callback_data="dellist_البكالوريا_كيمياء")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin")]
        ]
        await q.edit_message_text("🗑 اختر الصف والمادة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("dellist_") and user_id == ADMIN_ID:
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        all_lessons = {**lessons.get(grade, {}).get(subject, {}), **paid_lessons.get(grade, {}).get(subject, {})}
        if not all_lessons:
            await q.edit_message_text(f"📭 لا يوجد دروس في {grade} - {subject}")
        else:
            keyboard = []
            for name in all_lessons:
                keyboard.append([InlineKeyboardButton(f"🗑 {name}", callback_data=f"delete_{grade}_{subject}_{name}")])
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin")])
            await q.edit_message_text(f"🗑 اختر درساً للحذف:\n{grade} - {subject}", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("delete_") and user_id == ADMIN_ID:
        parts = data.split("_", 3)
        grade = parts[1]
        subject = parts[2]
        name = parts[3]
        if name in lessons.get(grade, {}).get(subject, {}):
            del lessons[grade][subject][name]
            save_lessons()
        elif name in paid_lessons.get(grade, {}).get(subject, {}):
            del paid_lessons[grade][subject][name]
            save_paid_lessons()
        await q.edit_message_text(f"✅ تم حذف: {name}")

    # إحصائيات
    if data == "stats" and user_id == ADMIN_ID:
        free_total = sum(len(lessons[g][s]) for g in lessons for s in lessons[g])
        paid_total = sum(len(paid_lessons[g][s]) for g in paid_lessons for s in paid_lessons[g])
        text = f"📊 الإحصائيات\n\n📚 دروس مجانية: {free_total}\n💰 دروس مدفوعة: {paid_total}\n👥 مشتركين ممتازين: {len(premium_users)}"
        await q.edit_message_text(text)

async def handle_file(update, context):
    if context.user_data.get("waiting_file"):
        doc = update.message.document
        name = doc.file_name
        if not name.endswith(".pdf"):
            await update.message.reply_text("❌ أرسل ملف PDF فقط")
            return
        file_obj = await doc.get_file()
        path = f"pdfs/{name}" if context.user_data.get("add_type") == "free" else f"paid_pdfs/{name}"
        await file_obj.download_to_drive(path)
        context.user_data["temp_path"] = path
        await update.message.reply_text("✅ تم استلام PDF\n📝 أرسل الآن اسم الدرس:")
        context.user_data["waiting_name"] = True
        context.user_data["waiting_file"] = False

async def handle_activation(update, context):
    if context.user_data.get("waiting_activation"):
        try:
            user_id = int(update.message.text)
            if user_id not in premium_users:
                premium_users.append(user_id)
                save_premium_users()
                await update.message.reply_text(f"✅ تم تفعيل المستخدم {user_id} بنجاح")
            else:
                await update.message.reply_text(f"⚠️ المستخدم {user_id} مفعل مسبقاً")
        except:
            await update.message.reply_text("❌ أرسل معرف مستخدم صحيح (أرقام فقط)")
        context.user_data["waiting_activation"] = False

async def handle_text(update, context):
    if context.user_data.get("waiting_name"):
        name = update.message.text
        path = context.user_data.get("temp_path")
        grade = context.user_data.get("add_grade")
        subject = context.user_data.get("add_subject")
        add_type = context.user_data.get("add_type")
        if path and name and grade and subject:
            if add_type == "free":
                lessons[grade][subject][name] = path
                save_lessons()
            else:
                paid_lessons[grade][subject][name] = path
                save_paid_lessons()
            await update.message.reply_text(f"✅ تم حفظ الدرس: {name}\n📚 {subject} - {grade}")
            context.user_data.clear()
        return
    
    await handle_activation(update, context)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("✅ البوت يعمل بنظام مجاني + مدفوع")
app.run_polling()

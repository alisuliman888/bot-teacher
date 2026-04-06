import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8704940063:AAEhMgGQmHmVkdFQL15QnSf3AXrh2IPj_s0"
ADMIN_ID = 5435228160

os.makedirs("pdfs", exist_ok=True)
os.makedirs("paid_pdfs", exist_ok=True)

# ========== تحميل البيانات ==========
if os.path.exists("lessons.json"):
    with open("lessons.json", "r") as f:
        lessons = json.load(f)
else:
    lessons = {
        "التاسع": {"فيزياء": {}, "كيمياء": {}},
        "البكالوريا": {
            "فيزياء": {
                "الوحدة1": {"نواس مرن": {}, "نواس فتل": {}, "نواس ثقلي": {}},
                "الوحدة2": {"المغناطيسية": {}, "فعل الحقل": {}, "التحريض الكهرطيسي": {}, "الدارات المهتزة": {}, "التيار المتناوب": {}, "المحولات الكهربائية": {}},
                "الوحدة3": {"الامواج": {}},
                "الوحدة4": {"الالكترونيات": {}},
                "الوحدة5": {"الفلكية": {}}
            },
            "كيمياء": {
                "الكيمياء النووية": {},
                "الغازات": {},
                "سرعة التفاعل والتوازن الكيميائي والمعايرة الحجمية": {},
                "الكيمياء العضوية": {}
            }
        }
    }

if os.path.exists("paid_lessons.json"):
    with open("paid_lessons.json", "r") as f:
        paid_lessons = json.load(f)
else:
    paid_lessons = {
        "التاسع": {"فيزياء": {}, "كيمياء": {}},
        "البكالوريا": {
            "فيزياء": {
                "الوحدة1": {"نواس مرن": {}, "نواس فتل": {}, "نواس ثقلي": {}},
                "الوحدة2": {"المغناطيسية": {}, "فعل الحقل": {}, "التحريض الكهرطيسي": {}, "الدارات المهتزة": {}, "التيار المتناوب": {}, "المحولات الكهربائية": {}},
                "الوحدة3": {"الامواج": {}},
                "الوحدة4": {"الالكترونيات": {}},
                "الوحدة5": {"الفلكية": {}}
            },
            "كيمياء": {
                "الكيمياء النووية": {},
                "الغازات": {},
                "سرعة التفاعل والتوازن الكيميائي والمعايرة الحجمية": {},
                "الكيمياء العضوية": {}
            }
        }
    }

if os.path.exists("premium_users.json"):
    with open("premium_users.json", "r") as f:
        premium_users = json.load(f)
else:
    premium_users = []

if os.path.exists("settings.json"):
    with open("settings.json", "r") as f:
        settings = json.load(f)
else:
    settings = {
        "welcome_text": "📘 الفيزياء والكيمياء - سوريا\n👨‍🏫 الأستاذ: علي سليمان\n\n🌟 مرحباً بك في المراجعة النهائية 🌟\n\nاختر صفك:"
    }

def save_lessons():
    with open("lessons.json", "w") as f:
        json.dump(lessons, f)

def save_paid_lessons():
    with open("paid_lessons.json", "w") as f:
        json.dump(paid_lessons, f)

def save_premium_users():
    with open("premium_users.json", "w") as f:
        json.dump(premium_users, f)

def save_settings():
    with open("settings.json", "w") as f:
        json.dump(settings, f)

# ========== القائمة الرئيسية ==========
async def main_menu(update, context, message=None):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    text = settings.get("welcome_text", "📘 الفيزياء والكيمياء - سوريا\n👨‍🏫 الأستاذ: علي سليمان\n\n🌟 مرحباً بك في البوت التعليمي\n\nاختر صفك:")
    
    if not is_premium:
        text += "\n\n💰 اشتراك ممتاز: 5000 ليرة/شهر"
    
    keyboard = [
        [InlineKeyboardButton("🎓 الصف التاسع", callback_data="grade_التاسع")],
        [InlineKeyboardButton("🎓 البكالوريا العلمي", callback_data="grade_البكالوريا")]
    ]
    
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ إدارة", callback_data="admin")])
    
    if not is_premium:
        keyboard.append([InlineKeyboardButton("💰 شراء الحزمة", callback_data="buy_package")])
    
    if message:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    await main_menu(update, context)

# ========== شراء الحزمة ==========
async def buy_package(update, context):
    text = """
💰 *طريقة الشراء:*

1️⃣ حول مبلغ 5000 ليرة إلى الرقم:
   `09XXXXXXXX` (MTN أو سيريتل كاش)

2️⃣ أرسل صورة الإشعار إلى @AliSuliman

3️⃣ سيتم تفعيل اشتراكك خلال 24 ساعة.

📞 للاستفسار: @AliSuliman
"""
    await update.callback_query.edit_message_text(text, parse_mode="Markdown")

# ========== عرض المواد حسب الصف ==========
async def show_subjects(update, context, grade, message):
    if grade == "التاسع":
        keyboard = [
            [InlineKeyboardButton("📘 فيزياء", callback_data=f"subject_{grade}_فيزياء")],
            [InlineKeyboardButton("🧪 كيمياء", callback_data=f"subject_{grade}_كيمياء")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📘 فيزياء", callback_data=f"subject_{grade}_فيزياء")],
            [InlineKeyboardButton("🧪 كيمياء", callback_data=f"subject_{grade}_كيمياء")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
    await message.edit_text(f"🎓 {grade}\nاختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض الوحدات للبكالوريا فيزياء ==========
async def show_physics_units(update, context, grade, message):
    keyboard = [
        [InlineKeyboardButton("📚 الوحدة الأولى", callback_data=f"unit_{grade}_فيزياء_الوحدة1")],
        [InlineKeyboardButton("📚 الوحدة الثانية", callback_data=f"unit_{grade}_فيزياء_الوحدة2")],
        [InlineKeyboardButton("📚 الوحدة الثالثة", callback_data=f"unit_{grade}_فيزياء_الوحدة3")],
        [InlineKeyboardButton("📚 الوحدة الرابعة", callback_data=f"unit_{grade}_فيزياء_الوحدة4")],
        [InlineKeyboardButton("📚 الوحدة الخامسة", callback_data=f"unit_{grade}_فيزياء_الوحدة5")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"grade_{grade}")]
    ]
    await message.edit_text(f"📘 فيزياء - {grade}\nاختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض دروس الوحدة (فيزياء) ==========
async def show_unit_lessons(update, context, grade, unit, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_lessons_data = lessons.get(grade, {}).get("فيزياء", {}).get(unit, {})
    paid_lessons_data = paid_lessons.get(grade, {}).get("فيزياء", {}).get(unit, {})
    
    keyboard = []
    
    for topic in free_lessons_data:
        keyboard.append([InlineKeyboardButton(f"📚 {topic}", callback_data=f"topic_{grade}_فيزياء_{unit}_{topic}_free")])
    
    if is_premium:
        for topic in paid_lessons_data:
            keyboard.append([InlineKeyboardButton(f"🔓 {topic} (مدفوع)", callback_data=f"topic_{grade}_فيزياء_{unit}_{topic}_paid")])
    else:
        for topic in paid_lessons_data:
            keyboard.append([InlineKeyboardButton(f"🔒 {topic} (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"subject_{grade}_فيزياء")])
    
    await message.edit_text(f"📚 {unit.replace('الوحدة', 'الوحدة ')} - فيزياء {grade}\nاختر الموضوع:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض دروس الموضوع (مكثفة + اختبار) ==========
async def show_topic_lessons(update, context, grade, unit, topic, lesson_type, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_data = lessons.get(grade, {}).get("فيزياء", {}).get(unit, {}).get(topic, {})
    paid_data = paid_lessons.get(grade, {}).get("فيزياء", {}).get(unit, {}).get(topic, {})
    
    keyboard = []
    
    if "مكثفة" in free_data:
        keyboard.append([InlineKeyboardButton("📖 مكثفة", callback_data=f"view_free_{grade}_فيزياء_{unit}_{topic}_مكثفة")])
    if "اختبار" in free_data:
        keyboard.append([InlineKeyboardButton("📝 اختبار", callback_data=f"view_free_{grade}_فيزياء_{unit}_{topic}_اختبار")])
    
    if is_premium:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 مكثفة (مدفوع)", callback_data=f"view_paid_{grade}_فيزياء_{unit}_{topic}_مكثفة")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 اختبار (مدفوع)", callback_data=f"view_paid_{grade}_فيزياء_{unit}_{topic}_اختبار")])
    else:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 مكثفة (مدفوع)", callback_data="not_premium")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 اختبار (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"unit_{grade}_فيزياء_{unit}")])
    
    await message.edit_text(f"📚 {topic}\nاختر:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض مواضيع الكيمياء للبكالوريا ==========
async def show_chemistry_topics(update, context, grade, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_data = lessons.get(grade, {}).get("كيمياء", {})
    paid_data = paid_lessons.get(grade, {}).get("كيمياء", {})
    
    keyboard = []
    
    for topic in free_data:
        keyboard.append([InlineKeyboardButton(f"🧪 {topic}", callback_data=f"chem_topic_{grade}_{topic}_free")])
    
    if is_premium:
        for topic in paid_data:
            keyboard.append([InlineKeyboardButton(f"🔓 {topic} (مدفوع)", callback_data=f"chem_topic_{grade}_{topic}_paid")])
    else:
        for topic in paid_data:
            keyboard.append([InlineKeyboardButton(f"🔒 {topic} (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"subject_{grade}_كيمياء")])
    
    await message.edit_text(f"🧪 كيمياء - {grade}\nاختر الموضوع:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض مكثفة واختبار لموضوع الكيمياء ==========
async def show_chem_topic_lessons(update, context, grade, topic, lesson_type, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_data = lessons.get(grade, {}).get("كيمياء", {}).get(topic, {})
    paid_data = paid_lessons.get(grade, {}).get("كيمياء", {}).get(topic, {})
    
    keyboard = []
    
    if "مكثفة" in free_data:
        keyboard.append([InlineKeyboardButton("📖 مكثفة", callback_data=f"view_free_chem_{grade}_{topic}_مكثفة")])
    if "اختبار" in free_data:
        keyboard.append([InlineKeyboardButton("📝 اختبار", callback_data=f"view_free_chem_{grade}_{topic}_اختبار")])
    
    if is_premium:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 مكثفة (مدفوع)", callback_data=f"view_paid_chem_{grade}_{topic}_مكثفة")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 اختبار (مدفوع)", callback_data=f"view_paid_chem_{grade}_{topic}_اختبار")])
    else:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 مكثفة (مدفوع)", callback_data="not_premium")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 اختبار (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"chem_{grade}")])
    
    await message.edit_text(f"🧪 {topic}\nاختر:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض الصف التاسع ==========
async def show_ninth_grade(update, context, grade, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_data = lessons.get(grade, {})
    paid_data = paid_lessons.get(grade, {})
    
    keyboard = []
    
    for subject in free_data:
        keyboard.append([InlineKeyboardButton(f"📚 {subject}", callback_data=f"ninth_subject_{grade}_{subject}_free")])
    
    if is_premium:
        for subject in paid_data:
            keyboard.append([InlineKeyboardButton(f"🔓 {subject} (مدفوع)", callback_data=f"ninth_subject_{grade}_{subject}_paid")])
    else:
        for subject in paid_data:
            keyboard.append([InlineKeyboardButton(f"🔒 {subject} (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"grade_{grade}")])
    
    await message.edit_text(f"🎓 {grade}\nاختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض مكثفة واختبار لمواد التاسع ==========
async def show_ninth_subject_lessons(update, context, grade, subject, lesson_type, message):
    user_id = update.effective_user.id
    is_premium = user_id in premium_users
    
    free_data = lessons.get(grade, {}).get(subject, {})
    paid_data = paid_lessons.get(grade, {}).get(subject, {})
    
    keyboard = []
    
    if "مكثفة" in free_data:
        keyboard.append([InlineKeyboardButton("📖 مكثفة", callback_data=f"view_free_ninth_{grade}_{subject}_مكثفة")])
    if "اختبار" in free_data:
        keyboard.append([InlineKeyboardButton("📝 اختبار", callback_data=f"view_free_ninth_{grade}_{subject}_اختبار")])
    
    if is_premium:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 مكثفة (مدفوع)", callback_data=f"view_paid_ninth_{grade}_{subject}_مكثفة")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔓 اختبار (مدفوع)", callback_data=f"view_paid_ninth_{grade}_{subject}_اختبار")])
    else:
        if "مكثفة" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 مكثفة (مدفوع)", callback_data="not_premium")])
        if "اختبار" in paid_data:
            keyboard.append([InlineKeyboardButton("🔒 اختبار (مدفوع)", callback_data="not_premium")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"ninth_{grade}")])
    
    await message.edit_text(f"📚 {subject} - {grade}\nاختر:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== عرض الملف ==========
async def view_file(update, context, file_path, caption):
    q = update.callback_query
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            await q.message.reply_document(f, caption=caption)
    else:
        await q.edit_message_text("❌ الملف غير موجود")

# ========== معالج الأزرار ==========
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
        await q.edit_message_text("🔒 هذا المحتوى للمشتركين فقط.\n\nلشراء الحزمة اضغط /start ثم اختر 💰 شراء الحزمة")
        return

    # اختيار الصف
    if data.startswith("grade_"):
        grade = data[6:]
        await show_subjects(update, context, grade, q.message)
        return

    # اختيار المادة
    if data.startswith("subject_"):
        parts = data.split("_")
        grade = parts[1]
        subject = parts[2]
        if grade == "التاسع":
            await show_ninth_grade(update, context, grade, q.message)
        elif subject == "فيزياء":
            await show_physics_units(update, context, grade, q.message)
        else:
            await show_chemistry_topics(update, context, grade, q.message)
        return

    # اختيار وحدة فيزياء
    if data.startswith("unit_"):
        parts = data.split("_")
        grade = parts[1]
        unit = parts[3]
        await show_unit_lessons(update, context, grade, unit, q.message)
        return

    # اختيار موضوع فيزياء
    if data.startswith("topic_"):
        parts = data.split("_")
        grade = parts[1]
        unit = parts[3]
        topic = parts[4]
        lesson_type = parts[5]
        await show_topic_lessons(update, context, grade, unit, topic, lesson_type, q.message)
        return

    # اختيار موضوع كيمياء
    if data.startswith("chem_topic_"):
        parts = data.split("_")
        grade = parts[2]
        topic = parts[3]
        lesson_type = parts[4]
        await show_chem_topic_lessons(update, context, grade, topic, lesson_type, q.message)
        return

    if data.startswith("chem_"):
        grade = data[5:]
        await show_chemistry_topics(update, context, grade, q.message)
        return

    # اختيار مادة التاسع
    if data.startswith("ninth_subject_"):
        parts = data.split("_")
        grade = parts[2]
        subject = parts[3]
        lesson_type = parts[4]
        await show_ninth_subject_lessons(update, context, grade, subject, lesson_type, q.message)
        return

    if data.startswith("ninth_"):
        grade = data[6:]
        await show_ninth_grade(update, context, grade, q.message)
        return

    # عرض الملفات المجانية
    if data.startswith("view_free_"):
        if data.startswith("view_free_ninth_"):
            parts = data.split("_")
            grade = parts[3]
            subject = parts[4]
            file_type = parts[5]
            path = lessons.get(grade, {}).get(subject, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n📚 {subject} - {grade}")
        elif data.startswith("view_free_chem_"):
            parts = data.split("_")
            grade = parts[3]
            topic = parts[4]
            file_type = parts[5]
            path = lessons.get(grade, {}).get("كيمياء", {}).get(topic, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n🧪 {topic} - {grade}")
        else:
            parts = data.split("_")
            grade = parts[2]
            unit = parts[3]
            topic = parts[4]
            file_type = parts[5]
            path = lessons.get(grade, {}).get("فيزياء", {}).get(unit, {}).get(topic, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n📚 {topic} - {grade}")
        return

    # عرض الملفات المدفوعة
    if data.startswith("view_paid_"):
        if user_id not in premium_users:
            await q.edit_message_text("🔒 هذا المحتوى للمشتركين فقط")
            return
        if data.startswith("view_paid_ninth_"):
            parts = data.split("_")
            grade = parts[3]
            subject = parts[4]
            file_type = parts[5]
            path = paid_lessons.get(grade, {}).get(subject, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n📚 {subject} - {grade}")
        elif data.startswith("view_paid_chem_"):
            parts = data.split("_")
            grade = parts[3]
            topic = parts[4]
            file_type = parts[5]
            path = paid_lessons.get(grade, {}).get("كيمياء", {}).get(topic, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n🧪 {topic} - {grade}")
        else:
            parts = data.split("_")
            grade = parts[2]
            unit = parts[3]
            topic = parts[4]
            file_type = parts[5]
            path = paid_lessons.get(grade, {}).get("فيزياء", {}).get(unit, {}).get(topic, {}).get(file_type)
            await view_file(update, context, path, f"📄 {file_type}\n📚 {topic} - {grade}")
        return

    # ========== لوحة الإدارة ==========
    if data == "admin" and user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة درس مجاني", callback_data="add_free")],
            [InlineKeyboardButton("💰 إضافة درس مدفوع", callback_data="add_paid")],
            [InlineKeyboardButton("✏️ تعديل رسالة الترحيب", callback_data="edit_welcome")],
            [InlineKeyboardButton("🗑 حذف درس", callback_data="del")],
            [InlineKeyboardButton("👥 تفعيل مستخدم", callback_data="activate_user")],
            [InlineKeyboardButton("📊 إحصائيات", callback_data="stats")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ]
        await q.edit_message_text("⚙️ لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # تعديل رسالة الترحيب
    if data == "edit_welcome" and user_id == ADMIN_ID:
        await q.edit_message_text("📝 أرسل رسالة الترحيب الجديدة:")
        context.user_data["waiting_welcome"] = True
        return

    # إضافة درس مجاني
    if data == "add_free" and user_id == ADMIN_ID:
        await q.edit_message_text("📤 أرسل ملف PDF (سيتم طلب مكان الحفظ بعد استلام الملف)")
        context.user_data["waiting_file"] = True
        context.user_data["add_type"] = "free"
        return

    # إضافة درس مدفوع
    if data == "add_paid" and user_id == ADMIN_ID:
        await q.edit_message_text("💰 أرسل ملف PDF (سيتم طلب مكان الحفظ بعد استلام الملف)")
        context.user_data["waiting_file"] = True
        context.user_data["add_type"] = "paid"
        return

    # تفعيل مستخدم
    if data == "activate_user" and user_id == ADMIN_ID:
        await q.edit_message_text("👤 أرسل معرف المستخدم (user_id) لتفعيل اشتراكه.\n\nمثال: 5435228160\n\nللحصول على معرفك، أرسل /id إلى @userinfobot")
        context.user_data["waiting_activation"] = True
        return

    # حذف درس
    if data == "del" and user_id == ADMIN_ID:
        await q.edit_message_text("🚧 سيتم إضافة واجهة الحذف قريباً\nللحذف حالياً، يمكنك حذف الملفات يدوياً من Render Shell")
        return

    # إحصائيات
    if data == "stats" and user_id == ADMIN_ID:
        free_total = 0
        paid_total = 0
        # حساب إجمالي الدروس المجانية والمدفوعة
        for grade in lessons:
            for subject in lessons[grade]:
                if isinstance(lessons[grade][subject], dict):
                    for item in lessons[grade][subject]:
                        free_total += len(lessons[grade][subject][item]) if isinstance(lessons[grade][subject][item], dict) else 1
        for grade in paid_lessons:
            for subject in paid_lessons[grade]:
                if isinstance(paid_lessons[grade][subject], dict):
                    for item in paid_lessons[grade][subject]:
                        paid_total += len(paid_lessons[grade][subject][item]) if isinstance(paid_lessons[grade][subject][item], dict) else 1
        text = f"📊 الإحصائيات\n\n📚 دروس مجانية: {free_total}\n💰 دروس مدفوعة: {paid_total}\n👥 مشتركين ممتازين: {len(premium_users)}"
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
        temp_path = f"temp_{name}"
        await file_obj.download_to_drive(temp_path)
        context.user_data["temp_path"] = temp_path
        context.user_data["temp_name"] = name
        
        # طلب مكان الحفظ
        keyboard = [
            [InlineKeyboardButton("التاسع - فيزياء", callback_data="savepath_التاسع_فيزياء")],
            [InlineKeyboardButton("التاسع - كيمياء", callback_data="savepath_التاسع_كيمياء")],
            [InlineKeyboardButton("البكالوريا - فيزياء - الوحدة1", callback_data="savepath_البكالوريا_فيزياء_الوحدة1")],
            [InlineKeyboardButton("البكالوريا - فيزياء - الوحدة2", callback_data="savepath_البكالوريا_فيزياء_الوحدة2")],
            [InlineKeyboardButton("البكالوريا - فيزياء - الوحدة3", callback_data="savepath_البكالوريا_فيزياء_الوحدة3")],
            [InlineKeyboardButton("البكالوريا - فيزياء - الوحدة4", callback_data="savepath_البكالوريا_فيزياء_الوحدة4")],
            [InlineKeyboardButton("البكالوريا - فيزياء - الوحدة5", callback_data="savepath_البكالوريا_فيزياء_الوحدة5")],
            [InlineKeyboardButton("البكالوريا - كيمياء - الكيمياء النووية", callback_data="savepath_البكالوريا_كيمياء_الكيمياء النووية")],
            [InlineKeyboardButton("البكالوريا - كيمياء - الغازات", callback_data="savepath_البكالوريا_كيمياء_الغازات")],
            [InlineKeyboardButton("البكالوريا - كيمياء - سرعة التفاعل", callback_data="savepath_البكالوريا_كيمياء_سرعة التفاعل والتوازن الكيميائي والمعايرة الحجمية")],
            [InlineKeyboardButton("البكالوريا - كيمياء - الكيمياء العضوية", callback_data="savepath_البكالوريا_كيمياء_الكيمياء العضوية")],
        ]
        await update.message.reply_text("📂 اختر مكان حفظ الملف:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["waiting_path"] = True
        context.user_data["waiting_file"] = False

async def handle_path_selection(update, context):
    if context.user_data.get("waiting_path"):
        query = update.callback_query
        await query.answer()
        path_data = query.data
        temp_path = context.user_data.get("temp_path")
        temp_name = context.user_data.get("temp_name")
        add_type = context.user_data.get("add_type")
        
        parts = path_data.split("_")
        if len(parts) >= 3:
            grade = parts[1]
            subject = parts[2]
            
            final_path = f"{add_type}_pdfs/{temp_name}"
            os.rename(temp_path, final_path)
            
            if add_type == "free":
                if grade == "التاسع":
                    lessons[grade][subject]["مكثفة"] = final_path
                else:
                    if len(parts) >= 4:
                        unit = parts[3]
                        if unit.startswith("الوحدة"):
                            lessons[grade][subject][unit]["نواس مرن"]["مكثفة"] = final_path
                        else:
                            topic = "_".join(parts[3:])
                            lessons[grade][subject][topic]["مكثفة"] = final_path
                save_lessons()
            else:
                if grade == "التاسع":
                    paid_lessons[grade][subject]["مكثفة"] = final_path
                else:
                    if len(parts) >= 4:
                        unit = parts[3]
                        if unit.startswith("الوحدة"):
                            paid_lessons[grade][subject][unit]["نواس مرن"]["مكثفة"] = final_path
                        else:
                            topic = "_".join(parts[3:])
                            paid_lessons[grade][subject][topic]["مكثفة"] = final_path
                save_paid_lessons()
            
            await query.edit_message_text(f"✅ تم حفظ الملف في:\n{grade} - {subject}")
            context.user_data.clear()

async def handle_text(update, context):
    user_id = update.effective_user.id
    
    # تعديل رسالة الترحيب
    if context.user_data.get("waiting_welcome") and user_id == ADMIN_ID:
        settings["welcome_text"] = update.message.text
        save_settings()
        await update.message.reply_text("✅ تم تعديل رسالة الترحيب بنجاح")
        context.user_data["waiting_welcome"] = False
        return
    
    # تفعيل مستخدم
    if context.user_data.get("waiting_activation") and user_id == ADMIN_ID:
        try:
            target_id = int(update.message.text)
            if target_id not in premium_users:
                premium_users.append(target_id)
                save_premium_users()
                await update.message.reply_text(f"✅ تم تفعيل المستخدم {target_id} بنجاح")
            else:
                await update.message.reply_text(f"⚠️ المستخدم {target_id} مفعل مسبقاً")
        except:
            await update.message.reply_text("❌ أرسل معرف مستخدم صحيح (أرقام فقط)")
        context.user_data["waiting_activation"] = False
        return

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(CallbackQueryHandler(handle_path_selection, pattern="^savepath_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("✅ البوت يعمل مع الهيكل المطلوب بالكامل")
app.run_polling()

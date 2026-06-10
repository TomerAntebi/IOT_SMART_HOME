# 🏠 Smart Room Monitor - IoT System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**מערכת ניטור חכמה לחדרים מבוססת IoT**

מערכת מתקדמת לניטור טמפרטורה ולחות בחדרים, עם שליטה אוטומטית וממשק משתמש אינטואיטיבי

[תכונות](#-תכונות) • [התקנה](#-התקנה) • [שימוש](#-שימוש) • [מבנה הפרויקט](#-מבנה-הפרויקט)

</div>

---

## 📋 תוכן עניינים

- [תיאור הפרויקט](#-תיאור-הפרויקט)
- [תכונות](#-תכונות)
- [דרישות מערכת](#-דרישות-מערכת)
- [התקנה](#-התקנה)
- [שימוש](#-שימוש)
- [מבנה הפרויקט](#-מבנה-הפרויקט)
- [ארכיטקטורה](#-ארכיטקטורה)
- [תצורת MQTT](#-תצורת-mqtt)
- [פתרון בעיות](#-פתרון-בעיות)

---

## 🎯 תיאור הפרויקט

**Smart Room Monitor** היא מערכת IoT מתקדמת המאפשרת ניטור בזמן אמת של תנאי הסביבה בחדרים שונים. המערכת כוללת:

- 📊 **דשבורד אינטראקטיבי** - ממשק משתמש מודרני ונוח
- 🔐 **מערכת התחברות** - אבטחה וניהול משתמשים
- 🏠 **ניהול חדרים מרובה** - תמיכה במספר חדרים
- ⏰ **טיימר אוטומטי** - הפעלה/כיבוי לפי לוח זמנים
- 📈 **גרפים בזמן אמת** - ויזואליזציה של נתוני טמפרטורה ולחות
- 🚨 **התראות חכמות** - התראות אוטומטיות על תנאים חריגים

---

## ✨ תכונות

### 🔹 תכונות עיקריות

- ✅ **ניטור בזמן אמת** - עדכון נתונים כל שנייה
- ✅ **ממשק משתמש מודרני** - בנוי עם Streamlit
- ✅ **ניהול חדרים** - הוספה ובחירת חדרים
- ✅ **שליטה ידנית ואוטומטית** - הפעלה/כיבוי ידני או לפי טיימר
- ✅ **אחסון נתונים** - שמירת היסטוריה ב-SQLite
- ✅ **תמיכה ב-MQTT** - תקשורת מבוססת MQTT עם HiveMQ

### 🔹 תכונות מתקדמות

- 🎛️ **מצבי פעולה** - AUTO/MANUAL
- ⏱️ **טיימר חכם** - תמיכה בטווחי זמן (כולל מעבר חצות)
- 📊 **ויזואליזציה** - גרפים דינמיים של טמפרטורה ולחות
- 🚨 **מערכת התראות** - INFO, WARNING, ALARM
- 🔄 **עדכון אוטומטי** - רענון אוטומטי של הממשק

---

## 💻 דרישות מערכת

### דרישות חומרה
- מחשב עם Windows/Linux/Mac
- חיבור לאינטרנט (לחיבור ל-MQTT broker)

### דרישות תוכנה
- **Python 3.8+** - [הורדה](https://www.python.org/downloads/)
- **pip** - מנהל חבילות Python (מגיע עם Python)

---

## 🚀 התקנה

### שלב 1: שכפול הפרויקט

```bash
# שכפול מהמאגר (אם יש)
git clone <repository-url>
cd Smart_Room_Monitor

# או פשוט עבור לתיקיית הפרויקט
cd Smart_Room_Monitor
```

### שלב 2: יצירת סביבה וירטואלית (מומלץ)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### שלב 3: התקנת התלויות

```bash
pip install -r requirements.txt
```

זה יתקין את החבילות הבאות:
- `paho-mqtt` - לקוח MQTT
- `streamlit` - מסגרת לפיתוח אפליקציות web
- `pandas` - עיבוד נתונים
- `streamlit-autorefresh` - רענון אוטומטי

### שלב 4: אתחול בסיס הנתונים

```bash
python init_db.py
```

---

## 📖 שימוש

### הפעלת המערכת

המערכת מורכבת משלושה רכיבים עיקריים שצריכים לרוץ במקביל:

#### 1️⃣ הפעלת Sensor Emulator (סימולטור חיישנים)

פתח טרמינל/Command Prompt ראשון:

```bash
cd Smart_Room_Monitor
python sensor_emulator.py
```

**פלט צפוי:**
```
[✓] MQTT connected to broker.hivemq.com:1883
[sensor] published: {'temp': 25.3, 'hum': 65.2, 'ts': 1234567890.123}
```

#### 2️⃣ הפעלת App Manager (מנהל המערכת)

פתח טרמינל שני:

```bash
cd Smart_Room_Monitor
python app_manager.py
```

**פלט צפוי:**
```
[manager] connected to broker
[manager] subscribing to telemetry and control mode topics
[manager] running... (DB enabled)
[manager] status: {'level': 'INFO', 'message': 'Temperature is normal...', ...}
```

#### 3️⃣ הפעלת Dashboard (ממשק המשתמש)

פתח טרמינל שלישי:

```bash
cd Smart_Room_Monitor
streamlit run dashboard.py
```

**פלט צפוי:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

הדפדפן יפתח אוטומטית, או פתח ידנית את הכתובת שמוצגת.

---

### 🔐 שימוש בממשק המשתמש

#### מסך התחברות
1. הזן **Username** ו-**Password** (כל ערך תקין)
2. לחץ על **Login** או **Guest Access** לכניסה מהירה

#### מסך בחירת חדר
1. בחר חדר קיים מהרשימה, או
2. לחץ על **Add New Room** להוספת חדר חדש:
   - הזן **Room Name** (למשל: "סלון", "חדר שינה")
   - הזן **Room ID** ייחודי (למשל: "room_001")
   - לחץ **Add Room**

#### מסך הדשבורד
- **מטריקות** - טמפרטורה, לחות, מצב, ריליי
- **גרפים** - ויזואליזציה של נתונים היסטוריים
- **שליטה ידנית** - כפתורי ON/OFF
- **טיימר** - הגדרת זמן הפעלה/כיבוי אוטומטי

---

## 📁 מבנה הפרויקט

```
Smart_Room_Monitor/
│
├── 📄 dashboard.py              # ממשק המשתמש הראשי (Streamlit)
├── 📄 app_manager.py            # מנהל המערכת המרכזי
├── 📄 sensor_emulator.py         # סימולטור חיישנים
├── 📄 relay_emulator.py          # סימולטור ריליי
├── 📄 button_emulator.py         # סימולטור כפתורים
│
├── 📄 mqtt_init.py              # הגדרות MQTT
├── 📄 db.py                      # פונקציות בסיס נתונים
├── 📄 init_db.py                # אתחול בסיס הנתונים
│
├── 📄 requirements.txt           # רשימת תלויות
├── 📄 README.md                  # קובץ זה
│
├── 📄 rooms.json                # רשימת החדרים (נוצר אוטומטית)
└── 📄 smart_room.db             # בסיס נתונים SQLite (נוצר אוטומטית)
```

---

## 🏗️ ארכיטקטורה

### רכיבי המערכת

```
┌─────────────────┐
│  Sensor Emulator│  ──► Publishes telemetry data
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   MQTT Broker   │  (HiveMQ - broker.hivemq.com)
│   (HiveMQ)      │
└─────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ App Manager │  │   Relay     │  │  Dashboard  │
│             │  │  Emulator   │  │  (Streamlit)│
└─────────────┘  └─────────────┘  └─────────────┘
         │
         ▼
┌─────────────┐
│  SQLite DB  │  (smart_room.db)
└─────────────┘
```

### זרימת נתונים

1. **Sensor Emulator** שולח נתוני טמפרטורה ולחות ל-MQTT
2. **App Manager** מקבל את הנתונים, מנתח אותם, ושולח סטטוס
3. **Dashboard** מציג את הנתונים למשתמש בזמן אמת
4. **Relay Emulator** מקבל פקודות שליטה ומדווח על מצב

---

## ⚙️ תצורת MQTT

המערכת משתמשת ב-MQTT broker ציבורי של HiveMQ:

- **Broker**: `broker.hivemq.com`
- **Port**: `1883`
- **Protocol**: MQTT v3.1.1

### Topics

| Topic | Direction | תיאור |
|-------|-----------|-------|
| `amiram/smart-room/telemetry` | Publish | נתוני חיישנים |
| `amiram/smart-room/status` | Subscribe | סטטוס מערכת |
| `amiram/smart-room/control/mode` | Publish | שליטה במצב (auto/manual) |
| `amiram/smart-room/actuator/relay/cmd` | Publish | פקודות ריליי |
| `amiram/smart-room/actuator/relay/state` | Subscribe | מצב ריליי |

---

## 🔧 פתרון בעיות

### הבעיה: הנתונים לא מופיעים בדשבורד

**פתרונות:**
1. ודא שכל שלושת הרכיבים רצים (sensor_emulator, app_manager, dashboard)
2. בדוק חיבור לאינטרנט
3. בדוק את הקונסולה לשגיאות
4. נסה לרענן את הדפדפן

### הבעיה: שגיאת חיבור ל-MQTT

**פתרונות:**
1. בדוק חיבור לאינטרנט
2. ודא שהחומת אש לא חוסמת את הפורט 1883
3. נסה להשתמש ב-VPN אם יש בעיות גישה

### הבעיה: שגיאת התקנת חבילות

**פתרונות:**
```bash
# עדכן pip
python -m pip install --upgrade pip

# נסה התקנה מחדש
pip install -r requirements.txt --force-reinstall
```

### הבעיה: Dashboard לא נפתח

**פתרונות:**
1. ודא ש-Streamlit מותקן: `pip install streamlit`
2. נסה להריץ: `streamlit --version`
3. בדוק שהפורט 8501 פנוי

---

## 📝 הערות חשובות

- ⚠️ **MQTT Broker ציבורי** - המערכת משתמשת ב-HiveMQ הציבורי. לפרודקשן, מומלץ להשתמש ב-broker פרטי.
- 💾 **שמירת נתונים** - הנתונים נשמרים ב-SQLite מקומי (`smart_room.db`)
- 🔐 **אבטחה** - מערכת ההתחברות היא בסיסית. לפרודקשן, הוסף אימות חזק יותר.
- 📊 **ביצועים** - המערכת מיועדת לניטור מספר מוגבל של חדרים. לקנה מידה גדול, שקול שיפורים.

---

## 👨‍💻 פיתוח

### הוספת תכונות חדשות

1. שמור את הקוד נקי ומתועד
2. השתמש ב-PEP 8 לסגנון קוד
3. בדוק את הקוד לפני commit

### תרומה לפרויקט

תרומות מתקבלות בברכה! אנא:
1. Fork את הפרויקט
2. צור branch חדש (`git checkout -b feature/AmazingFeature`)
3. Commit את השינויים (`git commit -m 'Add some AmazingFeature'`)
4. Push ל-branch (`git push origin feature/AmazingFeature`)
5. פתח Pull Request

---

## 📄 רישיון

פרויקט זה מופץ תחת רישיון MIT. ראה קובץ `LICENSE` לפרטים.

---

## 👤 מחבר

**Amiram** - פרויקט IoT לקורס

---

## 🙏 תודות

- [Streamlit](https://streamlit.io/) - למסגרת הנהדרת
- [HiveMQ](https://www.hivemq.com/) - ל-MQTT broker הציבורי
- [Paho MQTT](https://www.eclipse.org/paho/) - לספריית MQTT

---

<div align="center">

**נבנה עם ❤️ עבור פרויקט IoT**

⭐ אם הפרויקט עזר לך, שקול לתת Star!

</div>


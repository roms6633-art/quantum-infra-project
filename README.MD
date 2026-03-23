# 🛡️ Quantum-Safe Infrastructure Dashboard

פרויקט אישי שבו הקמתי תשתית ענן מלאה (AWS) שמריצה סימולציה של הצפנה קוונטית (פרוטוקול BB84).
המטרה הייתה לקחת קונספט תיאורטי מורכב ולהפוך אותו למוצר עובד, מנוהל וקריא בתוך Docker.

## 🛠️ מה עשיתי בפרויקט?
* **Infrastructure as Code:** השתמשתי ב-**Terraform** כדי להקים אוטומטית שרת EC2 ב-AWS, כולל ניהול Security Groups ומפתחות גישה.
* **Containerization:** ארזתי את כל האפליקציה (Flask + Qiskit) בתוך **Docker**. זה איפשר לי להתגבר על ספריות מדעיות כבדות ולהבטיח שהסביבה תרוץ בצורה זהה בכל מקום.
* **Backend & Logic:** כתבתי ב-**Python** סימולטור שמדמה העברת מפתחות קוונטיים, כולל זיהוי האזנות (Eavesdropping) בזמן אמת.
* **Visualization:** יצרתי Dashboard ב-Dark Mode שמנתח את המצב הקוונטי (Bloch Sphere) ומציג את אחוז השגיאות במערכת.

## 🚀 איך מריצים?
1. בונים את ה-Image:
   `docker build -t quantum-api .`
2. מריצים את הקונטיינר:
   `docker run -p 5000:5000 quantum-api`
3. ניגשים לדשבורד (בדפדפן):
   `http://localhost:5000/qkd/visualize?bits=24&eve=true`

## 🧠 אתגרים שהתמודדתי איתם
היה לי חשוב שה-Dockerfile יהיה יעיל, לכן השתמשתי בגרסת `slim` של Python וביצעתי אופטימיזציה להתקנת ספריות המערכת (כמו `libpng` ו-`freetype`) שנדרשות עבור הגרפיקה, תוך שמירה על נפח Image מינימלי.
# 🛡️ Quantum-Safe Infrastructure & QKD Analyzer

מערכת ענן מתקדמת לניתוח והדמיה של פרוטוקולי אבטחה קוונטיים (BB84). הפרויקט משלב תשתית ענן אוטומטית (IaC) עם מנוע חישוב קוונטי מבוסס Qiskit, ומספק Dashboard לניתוח פגיעויות בזמן אמת.

## ⚙️ יכולות המערכת
* **Automated Provisioning:** פריסה מלאה של תשתית AWS (EC2, Networking, Security) תוך שניות באמצעות **Terraform**.
* **Real-time QKD Simulation:** הרצת פרוטוקול BB84 להחלפת מפתחות מוצפנים על גבי סימולטור קוונטי.
* **Vulnerability Detection:** זיהוי אוטומטי של "האזנה" (Eavesdropping) בערוץ הקוונטי על ידי ניתוח קריסת פונקציית הגל.
* **Advanced Analytics Dashboard:** תצוגה ויזואלית של מצבים קוונטיים על גבי כדור בלוך (Bloch Sphere) וחישוב אחוז שגיאות (QBER) להערכת רמת האבטחה.
* **Containerized Deployment:** המערכת ארוזה ב-**Docker** להבטחת ביצועים אחידים ופריסה מהירה (Scalability).

## 🏗️ ארכיטקטורה טכנית
המערכת בנויה בארכיטקטורת **Microservices** מודרנית:
1. **Infrastructure Layer:** ניהול משאבי ענן ב-AWS באמצעות קוד (IaC).
2. **Logic Layer:** מנוע Python המריץ לוגיקה קוונטית וממשק API מבוסס Flask.
3. **Visualization Layer:** רינדור Dashboard דינמי המציג את תקינות המפתח והשוואה בין בסיסי השידור.


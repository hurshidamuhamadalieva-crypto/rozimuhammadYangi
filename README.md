# Telegram taksi boti

Toshkent va vodiy orasida haydovchi e’lonlari va yo‘lovchi buyurtmalarini boshqaradi.

## Ishga tushirish
Python 3.10 yoki 3.11. `pip install -r requirements.txt`, so‘ng `python main.py`.
`.env` fayliga `BOT_TOKEN=...` yozing. Adminlar, guruh IDlari va tariflar `config.py` da.
Serverda `DATA_DIR` ni doimiy diskka ulang. Botning guruhlarga xabar yuborish huquqi bo‘lsin.
Bir vaqtda faqat bitta bot nusxasini ishlating (JSON saqlash).

## Imkoniyatlar
- Yo‘lovchi: telefon, ikki ustunli yo‘nalish, matn, ixtiyoriy lokatsiya; buyurtmani bekor qilish.
- Telefon Telegramning kontakt tugmasi bilan yoki qo‘lda yozib yuboriladi.
- Lokatsiya Telegramning odatiy lokatsiya tugmasi bilan yuboriladi; lokatsiyasiz davom etish inline tugma orqali.
- Haydovchi arizasi birlashtirilgan: telefon va profil ma’lumotlari → tarif → to‘lov → adminning yagona qarori.
- Guruhdan haydovchi qidirish: https://t.me/bogdod_taxi16
- Telefon va lokatsiyani faqat tasdiqlangan, faol obunali haydovchi ko‘radi.
- Buyurtmani birinchi olgan haydovchi bajaradi va safarni yakunlay oladi.
- Haydovchi: rasmli e’lon, 5/10/15/20/30 daqiqa interval; yangi e’lon eskisini to‘xtatadi.
- E’londa profil va buyurtma tugmalari birga yuboriladi. Yuborish xatosi qayd etiladi.
- Obuna yangilansa qolgan kunlar saqlanadi; umrbod obuna qisqarmaydi.
- Admin: ariza tafsilotlari, mavjud username orqali profil, sabab bilan rad etish,
  to‘lovlarni ko‘rish/tasdiqlash, obunani qo‘lda uzaytirish, haydovchini chiqarish.
- Chek va admin orqali to‘lov mavjud. Click/Payme integratsiyasi hali yozilmagan.
- 12 soatda e’lon eslatmasi, 24 soatda avtomatik to‘xtash; obuna tugaganda e’lonlar to‘xtaydi.
- JSON yozish o‘zgarmagan ma’lumotni qayta diskka yozmaydi. Sana Toshkent vaqtida.

## Tekshirish
`python -m unittest test_bot -v` — Telegramga ulanmaydigan tekshiruvlar.
Jonli tekshiruv uchun alohida sinov boti va guruhlar ishlating.
Safar narxini hisoblash va baholash tizimi hozircha mavjud emas.

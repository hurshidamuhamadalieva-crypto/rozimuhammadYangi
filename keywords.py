import re


KEYWORDS_BASE_ODAM_BOR = [
    '1 kishi bor', '1 kishi bor edi', '1 kishi bor ekan', '1 kishi ekan', '1 ta qiz bola bor',
    '1 ta qiz bor', '1 киши бор', '1 та қиз бола бор', '1 та қиз бор',
    '1kishi ayol kishili mashina kerak', '1kishi bor', '1kishi ekan', '1odam bor', '1ta odam bor',
    '1ta qiz bola bor', '1ta qiz bor', '1киши аёл кишили машина керак', '1та одам бор',
    '2 kishi bor edi', '2 kishi bor ekan', '2 kishi ekan', '2 kishimiz', '2 киши бор',
    '2-kishi bor', '2-ta ayolkishi bor', '2-ta kishi bor', '2-ta odam bor', '2kishi bor',
    '2kishi ekan', '2kishimiz', '2ta ayol bor', '2ta odam bor', '2та аёл бор', '2та одам бор',
    '3 kishi bor edi', '3 kishi bor ekan', '3 kishi ekan', '3 kishimiz', '3 киши бор',
    '3-kishi bor', '3-ta ayolkishi bor', '3-ta kishi bor', '3-ta odam bor', '3kishi bor',
    '3kishi ekan', '3kishimiz', '3ta odam bor', '3та одам бор', '4 kishi bor edi',
    '4 kishi bor ekan', '4 kishimiz', '4 odam bor', '4 киши бор', '4 одам бор', '4-kishi bor',
    '4-ta ayolkishi bor', '4-ta kishi bor', '4-ta odam bor', '4kishi bor', '4kishi ekan',
    '4kishimiz', '4ta odam bor', '4та одам бор', 'amirsoydan 1kishi',
    'ayol kishi bor mashina sorashyabdi', 'ayollar bor mashina kerak', 'ayollar bor moshina kerak',
    'bagdodan 1kishi bor', 'bir qiz bir bola bor', 'bitta odam bor', "bog'doddan 2kishi",
    'Chirchiqdan 1 kishi', 'chirchiqdan 1kishi', 'ertagaga qoqonga 1kishi', "farg'onaga 1kishi",
    "farg'onaga 2kishi", "farg'onaga 3kishi", "farg'onaga 4kishi", 'fargonadan 1kishi',
    'fargonaga 2kishi', 'fargonaga odam bor', "g'azalkantdan 2 kishi", "g'azalkentdan 1kishi",
    'gazalkentdan 1kishi', 'gazalkentdan 2kishi', 'ikkita odam bor', 'kampilek odam bor',
    'katta yoshli ayol bor', 'kompilek odam bor', 'komplek odam bor', 'komplekt odam bor',
    "o'zimizdan 1kishi", 'odam bor', 'odam bor 1', 'odam bor 2', 'odam bor 3', 'odam bor 4',
    'odam bor edi', 'odam bor ekan', 'odam borakan', 'odam.bor', 'odambor', 'ozimizdan 1kishi',
    'ozimizdan 2 kishi', 'Qibraydan 1 kishi', 'qiz bola bor', 'qoqondan odam bor',
    'qoqonga 1kishi', 'qoqonga odam bor', 'rishtonga 1kishi', 'rishtonga 1kishi bor',
    'rishtonga 2kishi', 'rishtonga 3kishi', 'rishtonga 4kishi', 'rishtonga bir kishi',
    'rishtonga odam bor', 'tashkentdan rishtonga odam bor', "to'rtta odam bor", 'tortta odam bor',
    'toshkenda odam bor', "toshkendan bog'dodga odam bor", "toshkendan farg'onaga odam bor",
    'Toshkenga 1kishi', 'toshkenga 1kishi bor', 'toshkentdan 1 kishi bering degan',
    'toshkentdan 1 kishi bering deganga', 'toshkentdan 2 kishi bering degan',
    'toshkentdan 2 kishi bering deganga', 'toshkentdan 3 kishi bering degan',
    'toshkentdan 3 kishi bering deganga', 'toshkentdan 4 kishi bering degan',
    'toshkentdan 4 kishi bering deganga', 'toshkentdan bagdodga odam bor', 'toshkentdan bir kishi',
    'Toshkentdan Rishtonga 1odam bor', 'toshkentga 1kishi', 'toshkentga 1kishi bor',
    'Toshkentga 1ta odam bor', 'toshkentga 2kishi', 'toshkentga 3kishi', 'toshkentga 4kishi',
    'toshkentga odam bor', 'toshketga 1kishi', 'towga 1kishi', 'towga 2kishi', 'towga 3kishi',
    'towga 4kishi', 'uchkoprikda 1kishi', 'uchkoprikdan 1kishi', 'uchta odam bor',
    'yangiqorgondan 1kishi', 'Yangiyuldan 1 kishi', 'Zangiotadan 1 kishi', 'амирсойдан 1киши',
    'аёл киши бор машина сўрашяпти', 'аёллар бор машина керак', 'бағдодан 1киши бор',
    'бир қиз бир бола бор', 'битта одам бор', 'боғдоддан 2киши', 'газалкентдан 1киши',
    'газалкентдан 2киши', 'зангиотадан 1 киши', 'иккита одам бор', 'кампилек одам бор',
    'катта ёшли аёл бор', 'компилек одам бор', 'компилект odam бор', 'комплек одам бор',
    'комплект одам бор', 'одам бор', 'одам бор 1', 'одам бор 2', 'одам бор 3', 'одам бор 4',
    'одам бор эди', 'одам бор экан', 'озимиздан 1киши', 'озимиздан 2 киши', 'риштонга 1 киши',
    'риштонга одам бор', 'ташкентдан риштонга одам бор', 'тошкентга 1 киши', 'тошкентга одам бор',
    'тошкентдан бағдодга одам бор', 'тошкентдан боғдодга одам бор',
    'тошкентдан фарғонага одам бор', 'тўрта одам бор', 'тўртта одам бор', 'учкўприкда 1киши',
    'учкўприкдан 1киши', 'учта одам бор', 'фарғонага 1 киши', 'фарғонага 2киши',
    'фарғонага одам бор', 'фарғонадан 1киши', 'чирчиқдан 1 киши', 'чирчиқдан 1киши',
    'эртагага қўқонга 1киши', 'янгийўлдан 1 киши', 'янгиқўрғондан 1киши', 'ўзимиздан 1киши',
    'ғазалкентдан 1киши', 'ғазалкентдан 2 киши', 'қибрайдан 1 киши', 'қиз бола бор',
    'қўқонга 1киши', 'қўқонга одам бор', 'қўқондан одам бор', "Bitta odam Bor",
    "rishtonda bitaa odam", "Rishton dan Toshga 1ta odam bor", "pochta bor ekan", "pochta borekan",
    "pochta borakan", "bochta bor edi", "oldi mestaga odam bor", "bogdodga odam bor",
    "buvaydaga odam bor", "buvaydadan odam bor", "fargonaga 2 kishi", "toshkentdan pustoy mashina kerak",
    "toshdan 2 kishimiz", "rishtonga 3 ta odam bor", "ayollari bor mashina kerak",
    "ayol kishisi bor mashina bormi", "oldi bo'sh mashina kerak", "orqa salonga odam bor",
    "hozirga yurib turgan mashina kerak", "hozirga yuradigan moshina bormi",
]

# --- MASHINA / MOSHINA KERAK ---
KEYWORDS_BASE_MASHINA_KERAK = [
    'bagajli mashina kerak', 'bosh mashina bormi', 'bosh mashina kerak', 'jentra kerak',
    'kobalt kerak', 'mashina izlayapman', 'mashina kera', 'mashina keraa', 'mashina kerak',
    'mashina kerak edi', 'mashina kere', 'mashina kerek', 'mashina topaman', 'moshina kerak',
    'pustoy mashina kerak', 'yengil mashina kerak', 'багажли машина керак', 'бош машина борми',
    'бош машина керак', 'джентра керак', 'енгил машина керак', 'машина бор', 'машина излаяпман',
    'машина керeк', 'машина керак', 'машина кере', 'мошина керак', 'пустой машина керак',
]

# --- POCHTA / DOSTAVKA ---
KEYWORDS_BASE_POCHTA_DOSTAVKA = [
    'dastafka', 'dastafka bor', 'dastavka bor', 'dostavka bor', 'pochta bor', 'pochta bormi',
    'pochta kerak', 'pochta ketadi', 'pochta olib ketadi', 'даставка бор', 'доставка бор',
    'почта бор', 'почта керак', 'почта кетади', 'почта олиб кет', 'почта олиб кетади', 'пошта бор',
    'риштонга почта бор', 'риштондан почта бор', 'тошкентга почта бор', 'тошкентдан почта бор',
]

# --- KETADI / KETMOQCHI ---
KEYWORDS_BASE_KETADI_BOSHQA = [
    'bagdodga ketishi kerak', 'ketadi', 'ketishi kerak', 'ketvotti', 'toshkentga ketaman',
    'бағдодга кетиши керак', 'кетади', 'кетвотти', 'кетиши керак', 'тошкентга кетаман',
]

# --- BOSHQA KALIT SO'ZLAR ---
KEYWORDS_BASE_BOSHQA = [
    '1 kiwi bor edi', '1 kiwi bor ekan', '1 ta kamlarga', '1ta kamla', '1ta kamlarga',
    '2 kiwi bor edi', '2 kiwi bor ekan', '2 kiwimiz', '2kiwimiz', '3 kiwi bor edi',
    '3 kiwi bor ekan', '3 kiwimiz', '3kiwimiz', '4 kiwi bor edi', '4 kiwi bor ekan', '4 kiwimiz',
    '4kiwimiz', 'bagajga yuk bor', "birinchi so'raganga", 'bitta kamlarga', 'boshi bormi',
    'fargonaga kim yuryabdi', 'kim yurapti akalar', 'kim yuryabdi', "o'zimizdan kim bor",
    'ozimizdan kim bor', 'poshta  bor', 'Rishotondan 1kiwi', 'rishotondan 1kiwi bor',
    'shopir kerak', 'srochni kim yuryabdi', 'srochni yuradigan taxi kerak',
    'toshkentdan 1 kiwi bering degan', 'toshkentdan 1 kiwi bering deganga',
    'toshkentdan 2 kiwi bering deganga', 'toshkentdan 3 kiwi bering deganga',
    'toshkentdan 4 kiwi bering deganga', 'yuk bor', 'yuradiganla bormi', 'yuradiganlar bormi',
    'yurayotganla bomi', 'yurayotganla bormi', 'yurayotganlar bomi', 'yurayotganlar bormi',
    'yurediganla bormi', 'yurediganlar bomi', 'yurediganlar bormi', 'доставкa бор',
    'доставкa керак', 'кетвотди', 'кетишади', 'кетяпт', 'ким юрапти акалар', 'ким юряпти',
    'кобальт керак', 'машina кераа', 'озимиздан ким бор', 'срочни юрадиган такси керак',
    'фарғонага ким юряпти', 'шопир керак', 'юрадиганла борми', 'юрадиганлар борми',
    'юраётганла боми', 'юраётганла борми', 'юраётганлар боми', 'юраётганлар борми',
    'юредигaнла борми', 'юредигaнлар боми', 'юредигaнлар борми', 'ўзимиздан ким бор',
]

KEYWORDS_BASE = (
    KEYWORDS_BASE_ODAM_BOR +
    KEYWORDS_BASE_MASHINA_KERAK +
    KEYWORDS_BASE_POCHTA_DOSTAVKA +
    KEYWORDS_BASE_KETADI_BOSHQA +
    KEYWORDS_BASE_BOSHQA
)
# Quyidagilar - yuqoridagi lotincha so'zlarning kirillcha (o'zbek-kirill)
# ko'rinishi, avtomatik harf-ma-harf o'giril(transliteratsiya qilin)gan va
# faqat mavjud bo'lmagan (hali ro'yxatda yo'q) so'zlargina qo'shilgan.

# --- ODAM / KISHI / QIZ / AYOL BOR — kirillcha ---
KEYWORDS_TRANSLIT_ODAM_BOR = [
    '1 киши бор еди', '1 киши бор екан', '1 киши екан', '1киши бор', '1киши екан', '1одам бор',
    '1та қиз бола бор', '1та қиз бор', '2 киши бор еди', '2 киши бор екан', '2 киши екан',
    '2 кишимиз', '2-киши бор', '2-та аёлкиши бор', '2-та киши бор', '2-та одам бор', '2киши бор',
    '2киши екан', '2кишимиз', '3 киши бор еди', '3 киши бор екан', '3 киши екан', '3 кишимиз',
    '3-киши бор', '3-та аёлкиши бор', '3-та киши бор', '3-та одам бор', '3киши бор', '3киши екан',
    '3кишимиз', '4 киши бор еди', '4 киши бор екан', '4 кишимиз', '4-киши бор', '4-та аёлкиши бор',
    '4-та киши бор', '4-та одам бор', '4киши бор', '4киши екан', '4кишимиз',
    'аёл киши бор машина сорашябди', 'аёллар бор мошина керак', 'багдодан 1киши бор',
    'ертагага қоқонга 1киши', 'одам бор еди', 'одам бор екан', 'одам боракан', 'одам.бор',
    'одамбор', 'риштонга 1киши', 'риштонга 1киши бор', 'риштонга 2киши', 'риштонга 3киши',
    'риштонга 4киши', 'риштонга бир киши', 'тоwга 1киши', 'тоwга 2киши', 'тоwга 3киши',
    'тоwга 4киши', 'тортта одам бор', 'тошкенга 1киши', 'тошкенга 1киши бор', 'тошкенда одам бор',
    'тошкендан боғдодга одам бор', 'тошкендан фарғонага одам бор', 'тошкентга 1киши',
    'тошкентга 1киши бор', 'тошкентга 1та одам бор', 'тошкентга 2киши', 'тошкентга 3киши',
    'тошкентга 4киши', 'тошкентдан 1 киши беринг деган', 'тошкентдан 1 киши беринг деганга',
    'тошкентдан 2 киши беринг деган', 'тошкентдан 2 киши беринг деганга',
    'тошкентдан 3 киши беринг деган', 'тошкентдан 3 киши беринг деганга',
    'тошкентдан 4 киши беринг деган', 'тошкентдан 4 киши беринг деганга',
    'тошкентдан багдодга одам бор', 'тошкентдан бир киши', 'тошкентдан риштонга 1одам бор',
    'тошкетга 1киши', 'учкоприкда 1киши', 'учкоприкдан 1киши', 'фаргонага 2киши',
    'фаргонага одам бор', 'фаргонадан 1киши', 'фарғонага 1киши', 'фарғонага 3киши',
    'фарғонага 4киши', 'янгиюлдан 1 киши', 'янгиқоргондан 1киши', 'ғазалкантдан 2 киши',
    'қоқонга 1киши', 'қоқонга одам бор', 'қоқондан одам бор', "rishtonga 2kishi bor ekan", 
    "kim oladi", "tom bagaj kerak",
]

# --- MASHINA / MOSHINA KERAK — kirillcha ---
KEYWORDS_TRANSLIT_MASHINA_KERAK = [
    'жентра керак', 'йенгил машина керак', 'кобалт керак', 'машина кера', 'машина кераа',
    'машина керак еди', 'машина керек', 'машина топаман',
]

# --- POCHTA / DOSTAVKA — kirillcha ---
KEYWORDS_TRANSLIT_POCHTA_DOSTAVKA = [
    'дастафка', 'дастафка бор', 'почта борми',
]

# --- KETADI / KETMOQCHI — kirillcha ---
KEYWORDS_TRANSLIT_KETADI_BOSHQA = [
    'багдодга кетиши керак',
]

# --- BOSHQA KALIT SO'ZLAR — kirillcha ---
KEYWORDS_TRANSLIT_BOSHQA = [
    '1 киwи бор еди', '1 киwи бор екан', '1 та камларга', '1та камла', '1та камларга',
    '2 киwи бор еди', '2 киwи бор екан', '2 киwимиз', '2киwимиз', '3 киwи бор еди',
    '3 киwи бор екан', '3 киwимиз', '3киwимиз', '4 киwи бор еди', '4 киwи бор екан', '4 киwимиз',
    '4киwимиз', 'багажга юк бор', 'биринчи сўраганга', 'битта камларга', 'боши борми',
    'ким юрябди', 'ришотондан 1киwи', 'ришотондан 1киwи бор', 'срочни ким юрябди',
    'срочни юрадиган тахи керак', 'тошкентдан 1 киwи беринг деган',
    'тошкентдан 1 киwи беринг деганга', 'тошкентдан 2 киwи беринг деганга',
    'тошкентдан 3 киwи беринг деганга', 'тошкентдан 4 киwи беринг деганга', 'фаргонага ким юрябди',
    'юк бор', 'юредиганла борми', 'юредиганлар боми', 'юредиганлар борми',
    "пучта бор",
]

KEYWORDS_TRANSLIT = (
    KEYWORDS_TRANSLIT_ODAM_BOR +
    KEYWORDS_TRANSLIT_MASHINA_KERAK +
    KEYWORDS_TRANSLIT_POCHTA_DOSTAVKA +
    KEYWORDS_TRANSLIT_KETADI_BOSHQA +
    KEYWORDS_TRANSLIT_BOSHQA
)

# Ikkala ro'yxatni (lotincha + kirillcha) birlashtiramiz va aniq takrorlarni olib tashlaymiz.
KEYWORDS = list(dict.fromkeys(KEYWORDS_BASE + KEYWORDS_TRANSLIT))

KEYWORDS_RE = re.compile("|".join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)



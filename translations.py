TRANSLATIONS = {
    "tr": {
        "start": "Merhaba! Destek botuna hoş geldiniz. Sorununuzu aşağıdaki düğmelerden seçin.",
        "help": "Ana AI botunu kullanmak için mesajınızı gönderin. Yardıma ihtiyacınız olursa buradan yazın.",
        "ask_payment": "Ödeme sorununu açıklayın",
        "ask_support": "Sorununuzu açıklayın",
    },
    "id": {
        "start": "Halo! Selamat datang di bot dukungan. Pilih masalah Anda menggunakan tombol di bawah.",
        "help": "Untuk menggunakan bot AI utama, kirim pesan Anda. Jika butuh bantuan, hubungi di sini.",
        "ask_payment": "Jelaskan masalah pembayaran Anda",
        "ask_support": "Jelaskan pertanyaan Anda",
    },
    "ar": {
        "start": "مرحباً! أهلاً بك في بوت الدعم. اختر مشكلتك عبر الأزرار أدناه.",
        "help": "لاستخدام البوت الرئيسي أرسل رسالتك. لأي مساعدة اكتب هنا.",
        "ask_payment": "صف مشكلتك في الدفع",
        "ask_support": "صف سؤالك",
    },
    "vi": {
        "start": "Xin chào! Chào mừng đến với bot hỗ trợ. Hãy chọn vấn đề của bạn bằng các nút bên dưới.",
        "help": "Để dùng bot AI chính, hãy gửi tin nhắn của bạn. Nếu cần hỗ trợ, hãy nhắn tại đây.",
        "ask_payment": "Hãy mô tả vấn đề thanh toán của bạn",
        "ask_support": "Hãy mô tả câu hỏi của bạn",
    },
    "pt": {
        "start": "Olá! Bem-vindo ao bot de suporte. Escolha seu problema pelos botões abaixo.",
        "help": "Para usar o bot de IA principal, envie sua mensagem. Se precisar de ajuda, fale aqui.",
        "ask_payment": "Descreva seu problema com o pagamento",
        "ask_support": "Descreva sua dúvida",
    },
    "en": {
        "start": "Hello! Welcome to the support bot. Choose your issue using the buttons below.",
        "help": "To use the main AI bot, send your message. For help, contact here.",
        "ask_payment": "Describe your payment issue",
        "ask_support": "Describe your question",
    },
}

SUPPORTED_LANGS = {"tr", "id", "ar", "vi", "pt"}


def get_translation(lang: str, key: str) -> str:
    lang = lang if lang in TRANSLATIONS else "en"
    return TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, ""))

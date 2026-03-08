import re

class CustomNLPEvaluator:
    def __init__(self, transcript: str):
        self.text = re.sub(r'[^\w\s]', '', transcript.lower())
        self.profanity_penalty = 0

    def check_profanity(self):
        bad_words = ["bodoh", "gila", "tolol", "anjing", "kasar"]
        found = [word for word in bad_words if re.search(rf'\b{word}\b', self.text)]
        if found:
            self.profanity_penalty = 20
            return f"PERINGATAN: Kata tidak pantas ({', '.join(found)})."
        return "Bersih."

    def evaluate_m1_salam(self):
        keywords = ["selamat pagi", "selamat siang", "selamat sore", "halo", "hai", "permisi"]
        return (100, "Salam baik.") if any(w in self.text for w in keywords) else (0, "Tidak ada salam.")

    def evaluate_m2_perkenalan(self):
        has_intro = bool(re.search(r'\b(nama saya|saya|perkenalkan)\b', self.text))
        has_brand = bool(re.search(r'\b(spg|lasegar|twist|dari)\b', self.text))
        if has_intro and has_brand: return 100, "Perkenalan lengkap."
        elif has_intro or has_brand: return 50, "Perkenalan parsial."
        return 0, "Tidak ada perkenalan."

    def evaluate_m3_pk_detail(self):
        score, reasons = 0, []
        if any(w in self.text for w in ["leci", "jeruk", "lemon"]): score += 25; reasons.append("varian")
        if any(w in self.text for w in ["panas dalam", "segar", "adem"]): score += 25; reasons.append("manfaat")
        if any(w in self.text for w in ["coba", "cobain", "tester"]): score += 25; reasons.append("sampling")
        if any(w in self.text for w in ["dingin", "kulkas", "es"]): score += 25; reasons.append("penyajian")
        return score, f"Detail: {', '.join(reasons)}" if score > 0 else "Tidak ada detail produk."

    def evaluate_m4_crosselling(self):
        count = sum(1 for w in ["ambil 2", "sekalian", "hemat", "stok", "promo"] if w in self.text)
        if count >= 2: return 100, "Cross-selling proaktif."
        elif count == 1: return 50, "Cross-selling minimal."
        return 0, "Tidak ada cross-selling."

    def evaluate_m5_closing(self):
        keywords = ["terima kasih", "makasih", "sehat selalu", "mari"]
        return (100, "Penutup baik.") if any(w in self.text for w in keywords) else (0, "Tidak ada penutup.")

    def run_evaluation(self):
        catatan = self.check_profanity()
        m1_v, m1_r = self.evaluate_m1_salam()
        m2_v, m2_r = self.evaluate_m2_perkenalan()
        m3_v, m3_r = self.evaluate_m3_pk_detail()
        m4_v, m4_r = self.evaluate_m4_crosselling()
        m5_v, m5_r = self.evaluate_m5_closing()
        
        total = (0.05 * m1_v) + (0.05 * m2_v) + (0.50 * m3_v) + (0.35 * m4_v) + (0.05 * m5_v)
        total_akhir = max(0, total - self.profanity_penalty)
        
        detail_json = {
            "m1_salam": {"nilai": m1_v, "reasoning": m1_r},
            "m2_perkenalan": {"nilai": m2_v, "reasoning": m2_r},
            "m3_pk_detail": {"nilai": m3_v, "reasoning": m3_r},
            "m4_crosselling": {"nilai": m4_v, "reasoning": m4_r},
            "m5_closing": {"nilai": m5_v, "reasoning": m5_r},
            "catatan": catatan
        }
        return total_akhir, detail_json
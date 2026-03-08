import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from thefuzz import fuzz

factory = StemmerFactory()
stemmer = factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

class CustomNLPEvaluator:
    def __init__(self, transcript: str, product_knowledge: list = None):
        clean_text = re.sub(r'[^\w\s]', '', transcript.lower())
        self.raw_tokens = clean_text.split()
        
        stemmed_sentence = stemmer.stem(clean_text)
        self.stemmed_tokens = stemmed_sentence.split()
        self.stemmed_text = stemmed_sentence
        
        self.profanity_penalty = 0
        self.negation_words = ["tidak", "bukan", "jangan", "kurang", "gak", "nggak", "ndak", "tak", "belom", "belum"]
        
        self.product_knowledge_paragraphs = product_knowledge or []

    def _is_negated(self, index, window=3):
        start_index = max(0, index - window)
        preceding_words = self.raw_tokens[start_index:index]
        return any(neg in preceding_words for neg in self.negation_words)

    def _check_keywords(self, keywords, threshold=80, ignore_negation=False):
        for i, (raw_token, stemmed_token) in enumerate(zip(self.raw_tokens, self.stemmed_tokens)):
            for word in keywords:
                if word == stemmed_token or fuzz.ratio(word, raw_token) >= threshold:
                    if ignore_negation or not self._is_negated(i):
                        return True
        return False

    def _count_keywords(self, keywords, threshold=80):
        count = 0
        matched_keywords = set()
        for i, (raw_token, stemmed_token) in enumerate(zip(self.raw_tokens, self.stemmed_tokens)):
            for word in keywords:
                if word not in matched_keywords:
                    if word == stemmed_token or fuzz.ratio(word, raw_token) >= threshold:
                        if not self._is_negated(i):
                            count += 1
                            matched_keywords.add(word)
        return count

    def check_profanity(self):
        bad_words = ["bodoh", "gila", "tolol", "anjing", "kasar"]
        found = [word for word in bad_words if self._check_keywords([word], threshold=90, ignore_negation=True)]
        if found:
            self.profanity_penalty = 20
            return f"PERINGATAN: Kata tidak pantas terdeteksi."
        return "Bersih."

    def evaluate_m1_salam(self):
        original_raw = self.raw_tokens
        original_stemmed = self.stemmed_tokens
        self.raw_tokens = original_raw[:10]
        self.stemmed_tokens = original_stemmed[:10]
        
        keywords = ["pagi", "siang", "sore", "halo", "hai", "permisi"]
        is_valid = self._check_keywords(keywords, threshold=85)
        
        self.raw_tokens = original_raw
        self.stemmed_tokens = original_stemmed
        return (100, "Salam baik di awal percakapan.") if is_valid else (0, "Tidak ada salam di awal percakapan.")

    def evaluate_m2_perkenalan(self):
        has_intro = self._check_keywords(["nama", "saya", "kenal"]) 
        has_brand = self._check_keywords(["spg", "lasegar", "twist", "dari"])
        if has_intro and has_brand: return 100, "Perkenalan lengkap."
        elif has_intro or has_brand: return 50, "Perkenalan parsial."
        return 0, "Tidak ada perkenalan."

    def evaluate_m3_pk_detail(self):
        if not self.product_knowledge_paragraphs:
            return 0, "Tidak ada Product Knowledge yang diatur oleh Supervisor."

        score = 0
        reasons = []
        bobot_per_paragraf = 100 / len(self.product_knowledge_paragraphs)

        for i, paragraph in enumerate(self.product_knowledge_paragraphs):
            clean_para = re.sub(r'[^\w\s]', '', paragraph.lower())
            
            no_stop_para = stopword_remover.remove(clean_para)
            
            stemmed_para = stemmer.stem(no_stop_para)
            
            target_keywords = list(set(stemmed_para.split()))
            target_keywords = [w for w in target_keywords if len(w) > 2]

            match_count = self._count_keywords(target_keywords)
            
            threshold_match = 2 if len(target_keywords) >= 3 else 1
            
            if match_count >= threshold_match:
                score += bobot_per_paragraf
                label = " ".join(paragraph.split()[:3]) + "..."
                reasons.append(f"Poin '{label}' tersampaikan")
        
        return round(score), f"Tersampaikan: {', '.join(reasons)}" if score > 0 else "Gagal menyampaikan Product Knowledge."

    def evaluate_m4_crosselling(self):
        count = self._count_keywords(["ambil", "sekalian", "hemat", "stok", "promo"])
        if count >= 2: return 100, "Cross-selling proaktif."
        elif count == 1: return 50, "Cross-selling minimal."
        return 0, "Tidak ada cross-selling."

    def evaluate_m5_closing(self):
        original_raw = self.raw_tokens
        original_stemmed = self.stemmed_tokens
        self.raw_tokens = original_raw[-15:] if len(original_raw) >= 15 else original_raw
        self.stemmed_tokens = original_stemmed[-15:] if len(original_stemmed) >= 15 else original_stemmed
        
        keywords = ["kasih", "makasih", "sehat", "mari"]
        is_valid = self._check_keywords(keywords, threshold=85)
        
        self.raw_tokens = original_raw
        self.stemmed_tokens = original_stemmed
        return (100, "Penutup baik di akhir percakapan.") if is_valid else (0, "Tidak ada penutup di akhir percakapan.")

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
"""
医療情報のデモ用データおよび関数実装

このモジュールでは、医療用語、症状、治療法、医療制度、予防医学、FAQの情報を
ダミーデータとして定義し、各種検索・取得用の関数を実装しています。
"""

# --- ダミーデータ定義 ---

# 医療用語データ
medical_terms_data = [
    {
        "id": "TERM-001",
        "name": "血糖値",
        "category": "test",
        "definition": "血液中のグルコース濃度を示す値。糖尿病の診断や管理に重要な指標です。",
        "notes": "空腹時血糖値や食後血糖値など、測定時の状況によって値が異なります。",
    },
    {
        "id": "TERM-002",
        "name": "高血圧",
        "category": "disease",
        "definition": "血圧が持続的に高い状態。",
        "notes": "生活習慣の改善や薬物治療が推奨される場合があります。",
    },
]

# 症状データ
symptoms_data = [
    {
        "id": "SYMP-001",
        "name": "頭痛",
        "body_part": "head",
        "description": "頭部に感じる痛み。緊張型頭痛、片頭痛などの種類があります。",
    },
    {
        "id": "SYMP-002",
        "name": "胸痛",
        "body_part": "chest",
        "description": "胸部に感じる痛み。心疾患や筋肉の緊張など、原因は多岐にわたります。",
    },
]

# 治療法データ
treatments_data = [
    {
        "id": "TRT-001",
        "name": "インスリン療法",
        "treatment_type": "medication",
        "description": "糖尿病治療において、血糖値を管理するためにインスリンを投与する治療法です。",
    },
    {
        "id": "TRT-002",
        "name": "冠動脈バイパス手術",
        "treatment_type": "surgery",
        "description": "狭窄した冠動脈をバイパスして血流を改善するための手術です。",
    },
]

# 医療制度データ
healthcare_systems_data = [
    {
        "id": "SYS-001",
        "name": "健康保険",
        "system_type": "insurance",
        "description": "国民全体が加入する公的な医療保険制度です。",
    },
    {
        "id": "SYS-002",
        "name": "介護保険",
        "system_type": "service",
        "description": "高齢者向けの介護サービスを提供するための制度です。",
    },
]

# 予防医学情報データ
prevention_info_data = {
    "lifestyle": {
        "title": "生活習慣病の予防",
        "advice": "バランスの良い食事、定期的な運動、十分な睡眠が大切です。",
    },
    "infectious": {
        "title": "感染症の予防",
        "advice": "手洗い、うがい、ワクチン接種など基本的な感染予防策が重要です。",
    },
    "mental": {
        "title": "精神疾患の予防",
        "advice": "ストレス管理や適度な休息、専門家との相談が推奨されます。",
    },
    "other": {
        "title": "その他の疾病予防",
        "advice": "定期検診を受けるなど、早期発見・早期治療に努めることが重要です。",
    },
}

# FAQデータ
faq_data = [
    {
        "question": "血糖値とは何ですか？",
        "answer": "血糖値は血液中のグルコース濃度を示す値で、糖尿病の診断や管理に用いられます。",
        "category": "general",
    },
    {
        "question": "高血圧の原因は何ですか？",
        "answer": "高血圧は遺伝、生活習慣、ストレスなど複数の要因が影響します。",
        "category": "general",
    },
    {
        "question": "健康保険の仕組みはどうなっていますか？",
        "answer": "健康保険は加入者が医療費の一部を負担することで、医療サービスを受けやすくする制度です。",
        "category": "insurance",
    },
]

# --- 関数実装 ---


def get_medical_term(term_id: str) -> dict:
    """
    指定した医療用語IDに対応する詳細情報を取得します。
    """
    for term in medical_terms_data:
        if term["id"] == term_id:
            return term
    return {"error": "該当する医療用語が見つかりません"}


def search_medical_terms(query: str, category: str = None) -> dict:
    """
    検索キーワードと任意のカテゴリで医療用語を検索します。
    """
    results = []
    query_lower = query.lower()
    for term in medical_terms_data:
        if (
            query_lower in term["name"].lower()
            or query_lower in term["definition"].lower()
        ):
            if category:
                if term.get("category", "").lower() == category.lower():
                    results.append(term)
            else:
                results.append(term)
    return {"results": results}


def get_symptom_info(symptom_id: str) -> dict:
    """
    指定した症状IDに対応する詳細情報を取得します。
    """
    for symptom in symptoms_data:
        if symptom["id"] == symptom_id:
            return symptom
    return {"error": "該当する症状情報が見つかりません"}


def search_symptoms(query: str, body_part: str = None) -> dict:
    """
    検索キーワードと任意の身体部位で症状を検索します。
    """
    results = []
    query_lower = query.lower()
    for symptom in symptoms_data:
        if (
            query_lower in symptom["name"].lower()
            or query_lower in symptom["description"].lower()
        ):
            if body_part:
                if symptom.get("body_part", "").lower() == body_part.lower():
                    results.append(symptom)
            else:
                results.append(symptom)
    return {"results": results}


def get_treatment_info(treatment_id: str) -> dict:
    """
    指定した治療法IDに対応する詳細情報を取得します。
    """
    for treatment in treatments_data:
        if treatment["id"] == treatment_id:
            return treatment
    return {"error": "該当する治療法情報が見つかりません"}


def search_treatments(query: str, treatment_type: str = None) -> dict:
    """
    検索キーワードと任意の治療タイプで治療法を検索します。
    """
    results = []
    query_lower = query.lower()
    for treatment in treatments_data:
        if (
            query_lower in treatment["name"].lower()
            or query_lower in treatment["description"].lower()
        ):
            if treatment_type:
                if (
                    treatment.get("treatment_type", "").lower()
                    == treatment_type.lower()
                ):
                    results.append(treatment)
            else:
                results.append(treatment)
    return {"results": results}


def get_healthcare_system_info(system_id: str) -> dict:
    """
    指定した医療制度IDに対応する詳細情報を取得します。
    """
    for system in healthcare_systems_data:
        if system["id"] == system_id:
            return system
    return {"error": "該当する医療制度情報が見つかりません"}


def search_healthcare_systems(query: str, system_type: str = None) -> dict:
    """
    検索キーワードと任意の制度タイプで医療制度を検索します。
    """
    results = []
    query_lower = query.lower()
    for system in healthcare_systems_data:
        if (
            query_lower in system["name"].lower()
            or query_lower in system["description"].lower()
        ):
            if system_type:
                if system.get("system_type", "").lower() == system_type.lower():
                    results.append(system)
            else:
                results.append(system)
    return {"results": results}


def get_prevention_info(disease_type: str = None) -> dict:
    """
    指定した疾患タイプに対応する予防医学情報を取得します。
    疾患タイプが指定されない場合は、すべての予防情報を返します。
    """
    if disease_type:
        info = prevention_info_data.get(disease_type.lower())
        if info:
            return info
        else:
            return {"error": "該当する予防医学情報が見つかりません"}
    else:
        # すべての予防情報をリスト形式で返す
        return {"results": list(prevention_info_data.values())}


def get_faq(query: str = None, category: str = None) -> dict:
    """
    FAQを検索します。検索キーワードまたはカテゴリが指定された場合は、条件に合致するFAQを返します。
    何も指定されない場合は全FAQを返します。
    """
    results = []
    for faq in faq_data:
        match = True
        if query:
            query_lower = query.lower()
            if (
                query_lower not in faq["question"].lower()
                and query_lower not in faq["answer"].lower()
            ):
                match = False
        if category:
            if faq.get("category", "").lower() != category.lower():
                match = False
        if match:
            results.append(faq)
    return {"results": results}

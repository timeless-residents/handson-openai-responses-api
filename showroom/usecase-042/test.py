import json
from openai import OpenAI

# OpenAI クライアントを初期化します（API キーは環境変数等で設定済みと仮定）
client = OpenAI()


def main():
    response = client.responses.create(
        model="gpt-4o-2024-08-06",  # サポートされているモデルスナップショットを指定
        input=[
            {"role": "system", "content": "Extract the event information."},
            {
                "role": "user",
                "content": "Alice and Bob are going to a science fair on Friday.",
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "calendar_event",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The title or name of the event.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date of the event.",
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of participants attending the event.",
                        },
                    },
                    "required": ["name", "date", "participants"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )

    # モデルの出力（JSON 文字列）を Python の辞書に変換して表示
    event = json.loads(response.output_text)
    print(json.dumps(event, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

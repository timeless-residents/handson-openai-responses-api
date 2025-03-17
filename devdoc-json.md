今回の実行結果から、以下の点が考えられます。

### 原因と解決策
- **原因:**  
  当初、`analyze_multiple_sources` 関数で使用していた JSON スキーマの定義において、すべてのプロパティ（特に「信頼できる情報源」と「不確実または矛盾する情報」）が必須項目（required）に含まれていなかったため、レスポンスがスキーマと合致せずエラーが発生していました。

- **解決策:**  
  エラーメッセージに従い、スキーマ内の全プロパティを required 配列に追加することで、返される JSON が正しく検証されるよう修正しました。その結果、各機能（対象者別メッセージ生成、外国人向けメッセージ、複数の情報源からの分析、SNS投稿生成）が意図した通りの出力を返すようになりました。

### 改善点と今後の対策
- **エラーハンドリングの強化:**  
  API呼び出し部分や JSON の変換処理に対して、より詳細なエラーハンドリングを実装することで、予期せぬ入力やレスポンスにも柔軟に対応できるようにする。

- **動的スキーマ生成:**  
  災害情報や情報源の内容が変動する可能性があるため、必要に応じてスキーマ自体を動的に生成・調整できる仕組みを検討する。

- **ユーザーインターフェースの向上:**  
  コンソールへの出力だけでなく、GUI や Web インターフェースを介して結果を分かりやすく提示できるようにすることで、現場での迅速な意思決定を支援する。

- **テストケースの充実:**  
  複数の災害シナリオに対応できるよう、異なる条件や情報ソースを用いたテストケースを充実させ、システム全体の堅牢性を高める。

以上のように、今回のエラーは JSON スキーマの不整合が原因でしたが、修正後は各機能が意図通りに動作しています。今後はエラーハンドリングや柔軟性の向上を図ることで、より堅牢なシステムを構築できると考えられます。

---

Try it out
Try it out in the Playground or generate a ready-to-use schema definition to experiment with structured outputs.

Introduction
JSON is one of the most widely used formats in the world for applications to exchange data.

Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema, so you don't need to worry about the model omitting a required key, or hallucinating an invalid enum value.

Some benefits of Structured Outputs include:

Reliable type-safety: No need to validate or retry incorrectly formatted responses
Explicit refusals: Safety-based model refusals are now programmatically detectable
Simpler prompting: No need for strongly worded prompts to achieve consistent formatting
Getting a structured response
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "calendar_event",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "date": {
                        "type": "string"
                    },
                    "participants": {
                        "type": "array", 
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["name", "date", "participants"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

event = json.loads(response.output_text)
Supported models
Structured Outputs is available in our latest large language models, starting with GPT-4o:

gpt-4.5-preview-2025-02-27 and later
o3-mini-2025-1-31 and later
o1-2024-12-17 and later
gpt-4o-mini-2024-07-18 and later
gpt-4o-2024-08-06 and later
Older models like gpt-4-turbo and earlier may use JSON mode instead.

When to use Structured Outputs via function calling vs via text.format
Structured Outputs is available in two forms in the OpenAI API:

When using function calling
When using a json_schema response format
Function calling is useful when you are building an application that bridges the models and functionality of your application.

For example, you can give the model access to functions that query a database in order to build an AI assistant that can help users with their orders, or functions that can interact with the UI.

Conversely, Structured Outputs via response_format are more suitable when you want to indicate a structured schema for use when the model responds to the user, rather than when the model calls a tool.

For example, if you are building a math tutoring application, you might want the assistant to respond to your user using a specific JSON Schema so that you can generate a UI that displays different parts of the model's output in distinct ways.

Put simply:

If you are connecting the model to tools, functions, data, etc. in your system, then you should use function calling
If you want to structure the model's output when it responds to the user, then you should use a structured text.format
The remainder of this guide will focus on non-function calling use cases in the Responses API. To learn more about how to use Structured Outputs with function calling, check out the Function Calling guide.

Structured Outputs vs JSON mode
Structured Outputs is the evolution of JSON mode. While both ensure valid JSON is produced, only Structured Outputs ensure schema adherance. Both Structured Outputs and JSON mode are supported in the Responses API,Chat Completions API, Assistants API, Fine-tuning API and Batch API.

We recommend always using Structured Outputs instead of JSON mode when possible.

However, Structured Outputs with response_format: {type: "json_schema", ...} is only supported with the gpt-4o-mini, gpt-4o-mini-2024-07-18, and gpt-4o-2024-08-06 model snapshots and later.

Structured Outputs	JSON Mode
Outputs valid JSON	Yes	Yes
Adheres to schema	Yes (see supported schemas)	No
Compatible models	gpt-4o-mini, gpt-4o-2024-08-06, and later	gpt-3.5-turbo, gpt-4-* and gpt-4o-* models
Enabling	text: { format: { type: "json_schema", "strict": true, "schema": ... } }	text: { format: { type: "json_object" } }
Examples

Chain of thought

Structured data extraction

UI generation

Moderation
Chain of thought
You can ask the model to output an answer in a structured, step-by-step way, to guide the user through the solution.

Structured Outputs for chain-of-thought math tutoring
import json
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "math_reasoning",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": { "type": "string" },
                                "output": { "type": "string" }
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                        }
                    },
                    "final_answer": { "type": "string" }
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

math_reasoning = json.loads(response.output_text)
Example response
{
  "steps": [
    {
      "explanation": "Start with the equation 8x + 7 = -23.",
      "output": "8x + 7 = -23"
    },
    {
      "explanation": "Subtract 7 from both sides to isolate the term with the variable.",
      "output": "8x = -23 - 7"
    },
    {
      "explanation": "Simplify the right side of the equation.",
      "output": "8x = -30"
    },
    {
      "explanation": "Divide both sides by 8 to solve for x.",
      "output": "x = -30 / 8"
    },
    {
      "explanation": "Simplify the fraction.",
      "output": "x = -15 / 4"
    }
  ],
  "final_answer": "x = -15 / 4"
}
How to use Structured Outputs with text.format
Step 1: Define your schema
Step 2: Supply your schema in the API call
Step 3: Handle edge cases
Refusals with Structured Outputs
When using Structured Outputs with user-generated input, OpenAI models may occasionally refuse to fulfill the request for safety reasons. Since a refusal does not necessarily follow the schema you have supplied in response_format, the API response will include a new field called refusal to indicate that the model refused to fulfill the request.

When the refusal property appears in your output object, you might present the refusal in your UI, or include conditional logic in code that consumes the response to handle the case of a refused request.

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"}
    ],
    response_format=MathReasoning,
)

math_reasoning = completion.choices[0].message

# If the model refuses to respond, you will get a refusal message
if (math_reasoning.refusal):
    print(math_reasoning.refusal)
else:
    print(math_reasoning.parsed)
The API response from a refusal will look something like this:

{
  "id": "resp_1234567890",
  "object": "response",
  "created_at": 1721596428,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "input": [],
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [{
    "id": "msg_1234567890",
    "type": "message",
    "role": "assistant",
    "content": [
      {
        "type": "refusal",
        "refusal": "I'm sorry, I cannot assist with that request."
      }
    ]
  }],
  "usage": {
    "input_tokens": 81,
    "output_tokens": 11,
    "total_tokens": 92,
    "output_tokens_details": {
      "reasoning_tokens": 0,
    }
  },
}
Tips and best practices
Handling user-generated input
If your application is using user-generated input, make sure your prompt includes instructions on how to handle situations where the input cannot result in a valid response.

The model will always try to adhere to the provided schema, which can result in hallucinations if the input is completely unrelated to the schema.

You could include language in your prompt to specify that you want to return empty parameters, or a specific sentence, if the model detects that the input is incompatible with the task.

Handling mistakes
Structured Outputs can still contain mistakes. If you see mistakes, try adjusting your instructions, providing examples in the system instructions, or splitting tasks into simpler subtasks. Refer to the prompt engineering guide for more guidance on how to tweak your inputs.


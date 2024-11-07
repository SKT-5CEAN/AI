import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

#모델과 토크나이저 불러오기
tokenizer = GPT2Tokenizer.from_pretrained('./fine_tuned_kogpt2')
model = GPT2LMHeadModel.from_pretrained('./fine_tuned_kogpt2').to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

def generate_question(input_text, max_length=50):
    model.eval()
    inputs = tokenizer(input_text, return_tensors='pt', truncation=True, max_length=128).to(model.device)
    generated = model.generate(inputs['input_ids'], max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)
    return tokenizer.decode(generated[0], skip_special_tokens=True)

# 테스트용 자기소개서 문장 입력
input_text = "저는 팀 프로젝트에서 리더 역할을 맡았으며..." #예시 문장
predicted_question = generate_question(input_text)
print(f"예상 면접 질문: {predicted_question}")

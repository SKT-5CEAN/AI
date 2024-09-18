#pip installs torch pandas transformers

import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from torch.utils.data import Dataset, DataLoader
import torch
from transformers import AdamW, get_linear_schedule_with_warmup

#데이터 로드
df = pd.read_clipboard('데이터셋')
train_data = df[['기업명','자소서 문장','면접질문']]

class InterveiwDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> Any:
        input_text = self.data.iloc[idx, 0]
        target_text = self.data.iloc[idx, 1]
        inputs = self.tokenizer(input_text, truncation=True, padding="max_length", max_length=self.max_length, return_tensors="pt")
        targets = self.tokenizer(target_text, truncation=True, padding="max_length", max_length=self.max_length, return_tensors="pt")
        return {"input_ids": inputs["input_ids"].squeeze(), "attention_mask": inputs["attention_mask"].squeeze(), "labels": targets["input_ids"].squeeze()}
    
tokenizer = GPT2Tokenizer.from_pretrained('taeminlee/kogpt2')
model = GPT2LMHeadModel.from_pretrained('taeminlee/kogpt2')

dataset = InterveiwDataset(train_data, tokenizer)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

optimizer = AdamW(model.parameters(), lr=5e-5)
epochs = 3 #반복수
total_steps = len(dataloader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

#모델 학습 루프
model.train()
for epoch in range(epochs):
    for batch in dataloader:
        optimizer.zero_grad()
        input_ids = batch[input_ids].to(model.device)
        attention_mask = batch['attention_mask'].to(model.device)
        labels = batch['labels'].to(model.device)
        outputs = model(input_ids=input_ids, attention_mask = attention_mask, labels = labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()

# 파인튜닝된 모델 저장
model.save_pretrained('./fine_tuned_kogpt2')
tokenizer.save_pretrained('./fine_tuned_kogpt2')
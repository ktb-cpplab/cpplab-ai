from transformers import AutoTokenizer, AutoModel
import torch

class SentenceEmbedding:
    def __init__(self):
        model_path = "/Users/sanghun/Desktop/2024_KTB/11teamCCP/models/ko-sroberta-multitask/models--jhgan--ko-sroberta-multitask/snapshots/ab957ae6a91e99c4cad36d52063a2a9cf1bf4419"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # Contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    ## get_embeddings 는 기본적으로 string의 list 형태로 입력받습니다
    ## 하나의 sentence 입력 시 get_embeddings("test")[0].tolist() 형태로 사용하시면 됩니다
    def get_embeddings(self, sentences):
        if not sentences:
            raise ValueError("The sentences list is empty.")
        # Tokenize sentences
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform mean pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        return sentence_embeddings

    def get_mean_embedding(self, sentences):
        if not sentences:
            raise ValueError("The sentences list is empty.")
        if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
            raise TypeError("The sentences should be a list of strings.")
        sentence_embeddings = self.get_embeddings(sentences)
        # Compute the mean embedding over all sentences
        mean_embedding = sentence_embeddings.mean(dim=0)
        return mean_embedding.cpu().tolist()

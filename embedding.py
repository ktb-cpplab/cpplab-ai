from transformers import AutoTokenizer,AutoModel
import torch


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def get_embedding(sentences):

    path = "/Users/sanghun/Desktop/2024_KTB/11teamCCP/models/ko-sroberta-multitask/models--jhgan--ko-sroberta-multitask/snapshots/ab957ae6a91e99c4cad36d52063a2a9cf1bf4419"
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModel.from_pretrained(path)


    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

# Perform pooling. In this case, mean pooling.
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    #최종적으로 저장할 정보가 1차원 배열이기 때문에 index가 0인 배열만 반환한다
    #즉 원래는 여러개의 문장을 임베딩할 수 있지만 일단 현재는 하나의 문장을 임베딩하는 함수로 사용한다.
    return sentence_embeddings[0].tolist()

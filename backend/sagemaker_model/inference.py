import json
import torch
from transformers import AutoTokenizer, AutoModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def model_fn(model_dir):
    model_path = f"{model_dir}"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    model.to(device)
    model.eval()
    return {"tokenizer": tokenizer, "model": model}

def input_fn(request_body, request_content_type):
    if request_content_type == "application/json":
        lines = request_body.strip().split("\n")
        inputs = [json.loads(line) for line in lines]
        return inputs
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(inputs, model_dict):
    tokenizer = model_dict["tokenizer"]
    model = model_dict["model"]

    texts = [item["inputs"] for item in inputs]
    encoded = tokenizer(
        texts, padding=True, truncation=True, return_tensors="pt", max_length=128
    )
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        outputs = model(**encoded)
        embeddings = outputs.last_hidden_state[:, 0]

    embeddings = embeddings.cpu().tolist()
    results = []
    for inp, emb in zip(inputs, embeddings):
        results.append({
            "id": inp.get("id"),
            "text": inp.get("inputs"),
            "embedding": emb
        })
    return results

def output_fn(predictions, content_type):
    if content_type == "application/json":
        return "\n".join(json.dumps(pred) for pred in predictions)
    raise ValueError(f"Unsupported content type: {content_type}")

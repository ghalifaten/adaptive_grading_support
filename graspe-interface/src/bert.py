import torch


def bert_checker(model_loaded, tokenizer, sent):
    encoded_dict = tokenizer.encode_plus(
        sent,  # Sentence to encode.
        add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
        max_length=64,  # Pad & truncate all sentences.
        pad_to_max_length=True,
        return_attention_mask=True,  # Construct attn. masks.
        return_tensors='pt',  # Return pytorch tensors.
    )
    
    # Add the encoded sentence to the list.
    input_id = encoded_dict['input_ids']

    # And its attention mask (simply differentiates padding from non-padding).
    attention_mask = encoded_dict['attention_mask']
    input_id = torch.LongTensor(input_id)
    attention_mask = torch.LongTensor(attention_mask)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_loaded = model_loaded.to(device)
    input_id = input_id.to(device)
    attention_mask = attention_mask.to(device)
    with torch.no_grad():
        # Forward pass, calculate logit predictions
        outputs = model_loaded(input_id, token_type_ids=None, attention_mask=attention_mask)
    logits = outputs[0]
    index = logits.argmax()
    return index
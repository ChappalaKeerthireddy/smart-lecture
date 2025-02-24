from transformers import BartTokenizer, BartForConditionalGeneration

tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def summarize_text_from_file(input_file):
    try:
        with open(input_file, "r") as file:
            text = file.read()

        if len(text) == 0:
            return None
        
        # Tokenizing input text
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
        
        # Generating summary
        summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary
    except Exception as e:
        print(f"Error in summarization: {e}")
        return None

if __name__ == "__main__":
    print("Summary:\n", summarize_text_from_file("transcription.txt"))

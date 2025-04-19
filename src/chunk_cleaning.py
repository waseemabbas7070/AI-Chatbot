import os
from groq import Groq
from pdf_loader import pdf_loader,splitter
extracted_text = pdf_loader(r"artifacts\\PDFPaper.pdf")
text_chunks = splitter(extracted_text)
from dotenv import load_dotenv
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Create a list to collect the cleaned outputs
all_cleaned = []

for chunk in text_chunks:
    prompt = f"""
    You are a world class text pre-processor, here is the raw data from a PDF, please parse and return it in a way that is crispy and usable to send to a podcast writer.

    The raw data is messed up with new lines, Latex math and you will see fluff that we can remove completely. Basically take away any details that you think might be useless in a podcast author's transcript.

    Remember, the podcast could be on any topic whatsoever so the issues listed above are not exhaustive

    Please be smart with what you remove and be creative ok?

    Remember DO NOT START SUMMARIZING THIS, YOU ARE ONLY CLEANING UP THE TEXT AND RE-WRITING WHEN NEEDED

    Be very smart and aggressive with removing details, you will get a running portion of the text and keep returning the processed text.

    PLEASE DO NOT ADD MARKDOWN FORMATTING, STOP ADDING SPECIAL CHARACTERS THAT MARKDOWN CAPATILISATION ETC LIKES

    ALWAYS start your response directly with processed text and NO ACKNOWLEDGEMENTS about my questions ok?
    Here is the text:
    {chunk}
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.7
    )

    cleaned = response.choices[0].message.content
    print(cleaned)  # Keep your original print
    all_cleaned.append(cleaned)  # Store each output

# Save all output after loop finishes
with open("processed_output.txt", "w", encoding="utf-8") as f:
    for part in all_cleaned:
        f.write(part.strip() + "\n\n")  # Each chunk separated by new lines
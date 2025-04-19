def generate_podcast():
    import ast, re, os, nest_asyncio, asyncio
    from gtts import gTTS
    import edge_tts
    import ffmpeg
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()
    open_api_key = os.environ.get("open_api_key")

    nest_asyncio.apply()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=open_api_key,
    )

    SYSTEM_PROMPT = """
    You are an international Oscar-winning screenwriter.

    You have been working with multiple award-winning podcasters.

    Your job is to use the podcast transcript written below to re-write it for an AI Text-To-Speech Pipeline. A very dumb AI had written this so you have to step up for your kind.

    Make it as engaging as possible, Speaker 1 and 2 will be simulated by different voice engines.

    Speaker 1: Leads the conversation, asking insightful and thought-provoking questions. Speaker 1 digs deep into the topic, often bringing up real-world examples, analogies, and anecdotes to make the conversation more relatable and interesting. Speaker 1 keeps the conversation flowing and encourages Speaker 2 to elaborate, making sure the podcast is informative and entertaining.

    Speaker 2: Answers Speaker 1’s questions and provides in-depth responses. Speaker 2 is curious, open to new ideas, and engages in the conversation with enthusiasm. Their responses include personal experiences, analogies, and thoughtful reflections, ensuring the discussion is rich and engaging.

    The tone should be conversational, with a good balance between informative and entertaining content. The questions should be designed to spark detailed responses from Speaker 2, and the answers should be relatable and engaging, sprinkled with personal anecdotes.

    Remember:
    - Speaker 1 asks questions and leads the conversation.
    - Speaker 2 responds with answers, elaborating and adding their own insights.
    - Keep the flow natural, with pauses, questions, and explanations.

    Strictly format your response as a list of tuples, where each tuple contains the speaker’s name and the dialogue.

    START YOUR RESPONSE DIRECTLY WITH SPEAKER 1:

    Strictly return your response as a list of tuples, okay?
    """
    print("Processing...")
    with open('processed_output.txt', 'r', encoding='utf-8') as file:
        Cleaned_Text = file.read()

    completion = client.chat.completions.create(
        extra_body={},
        model="meta-llama/llama-4-maverick:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": Cleaned_Text}
        ]
    )

    raw_output = completion.choices[0].message.content.strip()
    match = re.search(r"\[.*?\]", raw_output, re.DOTALL)

    if not match:
        raise ValueError("No list of tuples found in the model's response. Check the prompt or the returned content:\n\n" + raw_output)

    cleaned_output = match.group(0)
    dialogue = ast.literal_eval(cleaned_output)
    print("Processing Complete")
    with open("formatted_podcast_script.txt", "w", encoding="utf-8") as f:
        for speaker, line in dialogue:
            f.write(f"{speaker}: {line}\n\n")

    speaker_1_lines = []
    speaker_2_lines = []

    for entry in dialogue:
        if len(entry) != 2:
            continue
        speaker, line = entry
        if speaker == "Speaker 1":
            speaker_1_lines.append(line)
        elif speaker == "Speaker 2":
            speaker_2_lines.append(line)

    with open("speaker_1.txt", "w", encoding="utf-8") as f1:
        for line in speaker_1_lines:
            f1.write(line + "\n")

    with open("speaker_2.txt", "w", encoding="utf-8") as f2:
        for line in speaker_2_lines:
            f2.write(line + "\n")
    print("Generating Audio...")
    os.makedirs("audio", exist_ok=True)
    num_lines = min(len(speaker_1_lines), len(speaker_2_lines))

    async def generate_edge_voice(text, filename, voice="en-GB-RyanNeural"):
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(filename)

    segment_list = []

    for i in range(num_lines):
        speaker1_path = f"audio/speaker1_{i}.mp3"
        gTTS(speaker_1_lines[i], lang='en', tld='com').save(speaker1_path)

        speaker2_path = f"audio/speaker2_{i}.mp3"
        asyncio.run(generate_edge_voice(speaker_2_lines[i], speaker2_path))

        segment_list.extend([
            f"file '{os.path.abspath(speaker1_path)}'",
            f"file '{os.path.abspath(speaker2_path)}'"
        ])

    concat_file_path = "audio/inputs.txt"
    with open(concat_file_path, "w", encoding="utf-8") as f:
        for line in segment_list:
            f.write(line + "\n")

    output_file = "podcast_episode.mp3"
    ffmpeg.input(concat_file_path, format='concat', safe=0).output(output_file, acodec='copy').overwrite_output().run()
    return output_file
    print("Audio Generation Complete")


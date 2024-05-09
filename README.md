# PAGES
Welcome to the PAGES project! This project introduces a proof-of-concept system aimed at enhancing the audio book listening experience through the generation of ambient music tailored to the tone and content of audiobooks.

## Overview

The system utilizes several popular models to achieve its goal:

1. **Whisper API**: This component extracts text from audio data, providing the book text needed for analysis and music generation.
   
2. **LLaMA 2**: LLaMA is a Large Language Model, which we use here to extract the tone and content information from the book text, which is then used to generate music.
   
3. **MusicGen**: MusicGen is a music generation model which is prompted to generate music based on the qualities extracted by the LLaMA model. Since MusicGen is able to accept both text and audio prompts, it is able to create seamless transitions between sections of differing tones in the text, enhancing the integration of music with the narrative tone.
   
The result is an ambient music generation system that dynamically adapts to the content for which it is generating.

## Usage

PAGES is designed to work locally on your machine using a Flask web application. To use the system, follow these steps:

1. **Install Dependencies**: Make sure you have all the necessary dependencies installed. Details can be found in the `requirements.txt` file.

2. **Run Flask Application**: Start the Flask application by running the `app.py` file:

    ```bash
    python app.py
    ```

3. **Access the Web Interface**: Once the Flask application is running, access the web interface by navigating to `http://localhost:5001` in your web browser.

4. **Upload Audio Files**: Use the web interface to upload your audiobook files. Alternatively, you can record yourself reading a book directly through the web interface.

5. **Text Extraction**: The Whisper system will automatically extract text from the uploaded audio files, and begin the text extraction process using the LLaMA large language model.

6. **Generate Ambient Music**: After the text extraction is complete, the MusicGen model will then generate ambient music based on the analyzed text and extracted musical qualities.

7. **Enjoy**: After the music generation process is complete, you can listen to the generated ambient music alongside your input audio directly through the web interface. The inferface allows you to balance the volume of the ambient music and the input audio, and you can also listen to some of our pre-cooked examples.
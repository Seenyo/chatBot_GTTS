import json
import os
import random
import openai

from dotenv import load_dotenv

import streamlit as st
from google.cloud import texttospeech as gtts


def intro():
    st.write('# Welcome to CGLab Home! 👏')
    st.sidebar.success('Hello there my friends!!')


def chat_bot():

    base_path = './chatbot/'
    env_path =  base_path + 'env/'
    json_path = base_path + 'json/'
    audio_path = base_path + 'audio/'
    load_dotenv(dotenv_path=env_path+'.env')

    openai.api_key = os.getenv('OPENAI_API_KEY')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env_path + 'chatbot-388815-3845c11e4053.json'

    if['voice_dict'] not in st.session_state:
        try:
            with open(json_path + 'voice_dict.json') as vf:
                st.session_state['voice_dict'] = json.load(vf)
        except FileNotFoundError:
            print("Couldn't Find File!")

    if ['config'] not in st.session_state:
        try:
            with open(json_path + 'config.json') as in_f:
                st.session_state['config'] = json.load(in_f)

        except FileNotFoundError:
            initial_state = {
                'language': 'en-US',
                'voice': 'en-US-Neural2-A',
                'pitch': 0.00,
                'speed': 1.00,
            }
            st.session_state['config'] = initial_state

    config = st.session_state['config']
    voice_dict = st.session_state['voice_dict']
    client = gtts.TextToSpeechClient()

    def gen_audio(texts):

        generated_response = gtts.SynthesisInput(text=texts)

        voice_conf = gtts.VoiceSelectionParams(
            language_code=config['language'],
            name=config['voice'],
        )

        audio_config = gtts.AudioConfig(
            audio_encoding=gtts.AudioEncoding.MP3,
            pitch=config['pitch'],
            speaking_rate=config['speed'],
        )

        response = client.synthesize_speech(
            input=generated_response,
            voice=voice_conf,
            audio_config=audio_config
        )

        with open(audio_path + 'output.mp3', "wb") as out:
            out.write(response.audio_content)

        return "output.mp3"

    def gen_response(inputted_texts):

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "system", "content": f"You are a Engineer."}, {"role": "user", "content": inputted_texts}],
        )

        message = response.choices[0].message['content'].strip()

        return message


    st.title('ChatBot!')
    dialects = ["en-US", "en-GB", "en-AU", "en-IN"]
    config['language'] = st.selectbox("Dialect", dialects, index=dialects.index(config['language']))
    config['voice'] = st.selectbox("Voice", voice_dict[config['language']])
    config['pitch'] = st.slider("Pitch", min_value=-20.00, max_value=20.00, value=config['pitch'])
    config['speed'] = st.slider("Speed", min_value=0.25, max_value=4.00, value=config['speed'])

    if st.button("Save Config"):
        with open(json_path + 'config.json', 'w') as out_f:
            json.dump(st.session_state['config'], out_f)


    text = st.text_input("Enter somthing")

    if st.button("Send Message"):
        gpt_response = gen_response(text)
        audio_file = gen_audio(gpt_response)
        st.write(gpt_response)
        st.audio(audio_path + audio_file, format='audio/mp3')


def to_do():
    from streamlit_elements import elements, dashboard, mui

    json_path = './todo/json/'
    os.makedirs(json_path, exist_ok=True)

    with elements('todo'):

        if 'tasks' not in st.session_state:
            try:
                with open(json_path + 'task_data.json', 'r') as i_task:
                    st.session_state['tasks'] = json.load(i_task)
            except FileNotFoundError:
                st.session_state['tasks'] = []

        if 'layout' not in st.session_state:
            try:
                with open(json_path + 'layout.json', 'r') as i_lay:
                    st.session_state['layout'] = json.load(i_lay)
            except FileNotFoundError:
                st.session_state['layout'] = []

        def add_task():
            new_task_id = str(max((int(t['i']) for t in st.session_state['tasks']), default=0) + 1)
            random_color = [random.choice(range(128, 256)) for _ in range(3)]
            new_color = '#%02X%02X%02X' % (random_color[0], random_color[1], random_color[2])
            st.session_state['tasks'].append(
                dashboard.Item(new_task_id, 0, 2, 1, 1, color=new_color, text="", font='serif', fontsize="10px"))

        def save_tasks():
            with open(json_path + 'task_data.json', 'w') as o_task:
                json.dump(st.session_state['tasks'], o_task)
            with open(json_path + 'layout.json', 'w') as o_lay:
                json.dump(st.session_state['layout'], o_lay)

        def change_font(new_font):
            for cfs in selected_tasks:
                task_to_change_f = next(t for t in st.session_state['tasks'] if t['text'] == cfs)
                task_to_change_f['font'] = new_font

        def change_fontsize(fontsize):
            for cfs in selected_tasks:
                task_to_change_fs = next(t for t in st.session_state['tasks'] if t['text'] == cfs)
                task_to_change_fs['fontsize'] = fontsize

        def clone_tasks():
            for cl in selected_tasks:
                task_to_clone = next(t for t in st.session_state['tasks'] if t['text'] == cl)
                new_task_id = str(max((int(t['i']) for t in st.session_state['tasks']), default=0) + 1)
                st.session_state['tasks'].append(
                    dashboard.Item(new_task_id, 0, 2, 1, 1, color=task_to_clone['color'], text=task_to_clone['text']
                                   , font=task_to_clone['font'], fontsize=task_to_clone['fontsize']))

        def delete_tasks():
            st.session_state['tasks'] = [t for t in st.session_state['tasks'] if t['text'] not in selected_tasks]

        def handle_layout_change(updated_layout):
            st.session_state['layout'] = updated_layout

        colAdd, colSave, colNull, colChoose, colFont, colFontSize, colClone, colDel = st.columns(
            [0.1, 0.1, 1, 0.2, 0.15, 0.15, 0.1, 0.1])

        with colAdd:
            st.button('Add', on_click=add_task)
        with colSave:
            st.button('Save', on_click=save_tasks)
        with colChoose:
            task_text = [task['text'] for task in st.session_state['tasks']]
            selected_tasks = st.multiselect("label", task_text, label_visibility="collapsed")
        with colFont:
            font = st.selectbox("label", (
            'serif', 'san serif', 'arial', 'times new roman', 'helvetica', 'verdana', 'courier new', 'georgia',
            'palatino', 'garamond', 'bookman', 'trebuchet ms'), label_visibility="collapsed")
            change_font(font)
        with colFontSize:
            size = st.selectbox("label",
                                ('10px', '15px', '20px', '25px', '30px', '35px', '40px', '45px', '50px', '55px'),
                                label_visibility="collapsed")
            change_fontsize(size)
        with colClone:
            st.button('Clone', on_click=clone_tasks)
        with colDel:
            st.button('Delete', on_click=delete_tasks)

        with dashboard.Grid(st.session_state['layout'], cols={'xl': 30, 'lg': 20, 'md': 15, 'sm': 10, 'xs': 8},
                            rowHeight=50, draggableHandle='.draggable', onLayoutChange=handle_layout_change):
            for index, task in enumerate(st.session_state['tasks']):

                def make_handle_change(idx):
                    def handle_each_change(event):
                        if event and 'target' in event and 'value' in event['target']:
                            st.session_state['tasks'][idx]['text'] = event['target']['value']

                    return handle_each_change

                handle_change = make_handle_change(index)

                with mui.Card(key=task['i'],
                              sx={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': task['color']}):
                    with mui.CardContent(className='draggable', sx={"flex": 1, "minHeight": 0}):
                        mui.TextField(
                            label="",
                            defaultValue=task['text'],
                            multiline=True,
                            variant="standard",
                            sx={
                                "font-size": task['fontsize'],
                                "width": "100%",
                                "height": "100%",
                            },
                            InputProps={
                                'style': {
                                    'fontSize': "100%",
                                    'color': "#303030",
                                    'fontWeight': 'bold',
                                    'fontFamily': task['font'],
                                },
                                'disableUnderline': 'true'
                            },
                            onChange=handle_change,
                        )


page_names_to_funcs = {
    "Home": intro,
    "Text to Speech Demo": chat_bot,
    "ToDo Demo": to_do,
}

st.set_page_config(layout="wide")
demo_name = st.sidebar.selectbox("Choose the page", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()

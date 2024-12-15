from pprint import pprint
from tqdm import tqdm
import google.generativeai as genai
import easygui
import json
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

DEBUG = False

if 'GOOGLE_API_KEY' in os.environ:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
else:
    genai.configure()

qtype = genai.protos.Schema(
    type_ = genai.protos.Type.STRING,
    format_ = 'enum',
    enum = ["Multiple Choice", "True/False"]
)

banswer = genai.protos.Schema(
    type_ = genai.protos.Type.STRING,
    format_ = 'enum',
    enum = ["True", "False", "Unanswered", "Unknown"]
)

bbox = genai.protos.Schema(
    type_ = genai.protos.Type.ARRAY,
    items = genai.protos.Schema(
        type_ = genai.protos.Type.NUMBER,
        format_ = 'float',
        description = 'The bounding box of the checkbox, in [ymin, xmin, ymax, xmax] format'
    ),
    min_items = 4,
    max_items = 4
)

moption = genai.protos.Schema(
    type_ = genai.protos.Type.OBJECT,
    properties = {
        'option_contents': genai.protos.Schema(type_ = genai.protos.Type.STRING),
        'option_state': genai.protos.Schema(type_ = genai.protos.Type.STRING, format_ = 'enum', enum = ['Ticked', 'Crossed', 'Filled', 'Circled', 'Empty', 'Unknown']),
        'bounding_box': bbox
    },
    required = ['option_contents', 'option_state', 'bounding_box']
)

result = genai.protos.Schema(
    type_ = genai.protos.Type.OBJECT,
    properties = {
        'question_number': genai.protos.Schema(type_ = genai.protos.Type.INTEGER),
        'question_contents': genai.protos.Schema(type_ = genai.protos.Type.STRING),
        'question_type': qtype,
        'boolean_answer': banswer,
        'options': genai.protos.Schema(
            type_ = genai.protos.Type.ARRAY,
            items = moption
        )
    },
    required = ['question_number', 'question_contents', 'question_type']
)

results = genai.protos.Schema(
    type_ = genai.protos.Type.ARRAY,
    items = result,
    min_items = 1
)

model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp', safety_settings=None, generation_config=genai.GenerationConfig(
    candidate_count=1,
    temperature=0.05,
    response_schema=results,
    response_mime_type='application/json'
))

# master_path = easygui.fileopenbox('Please upload master key', filetypes=['*.csv', 'CSV files'])
# converter = DocumentConverter()
file_paths = easygui.fileopenbox('Please upload student response', filetypes=[['*.png', '*.jpg', 'Images']], multiple=True)
results = []
for file in tqdm([i for i in file_paths if str(i).endswith(('.png', '.jpg'))]):
    # uploaded_files.append(genai.upload_file(file))
    img = Image.open(file)
    # result = converter.convert(file)
    # print(result.document.export_to_markdown())
    # [print(i.label, '\n', i.text) for i in result.document.texts]
    results.append(model.generate_content([img,"Transcribe this image. For each question, write the question number, its contents, its type (Multiple Choice or True/False). If it is a Multiple Choice question, state each of its options, their state, and their bounding boxes. If it is a True/False question, state the state of the answer as well as the value of the answer written."]))

final_json = []
debug_output = []

for result in results:
    try:
        res_json = json.loads(result.text)
        _ = [final_json.append(i) for i in res_json]
        debug_output.append(result.text)
    except Exception as e:
        print('ERROR: Invalid JSON')
        raise e

if DEBUG:
    print('\nDEBUG: LLM Response:')
    pprint(final_json) 

def argmax(a, key=None):
    return a.index(max(a, key=key))

def print_qa(json):
    json = sorted(json, key=lambda x: x['question_number'])
    for result in json:
        print(f'{result['question_number']}. {result['question_contents']}')
        if result['question_type'] == 'Multiple Choice':
            marked_options = [(i, option) for i, option in enumerate(result['options']) if option['option_state'] not in ['Empty', 'Unknown']]
            if marked_options:
                for (number, option) in marked_options:
                    print(f'  {number + 1}. [{option['option_state']}] {option['option_contents']}')
                print(f'{len(marked_options)} option(s) selected')
            else:
                print("No option selected")
        elif result['question_type'] == 'True/False':
            print(result['boolean_answer'])
        else:
            print(result['question_number'], "Unknown question type")
        print()

print_qa(final_json)

with open('output.json', 'w') as f:
    json.dump(final_json, f, indent=4)

with open('output.txt', 'w') as f:
    json_sorted = sorted(final_json, key=lambda x: x['question_number'])
    for result in json_sorted:
        f.write(f'{result['question_number']}. {result['question_contents']}\n')
        if result['question_type'] == 'Multiple Choice':
            marked_options = [(i, option) for i, option in enumerate(result['options']) if option['option_state'] not in ['Empty', 'Unknown']]
            if marked_options:
                for (number, option) in marked_options:
                    f.write(f'  {number + 1}. [{option['option_state']}] {option['option_contents']}\n')
                f.write(f'{len(marked_options)} option(s) selected\n')
            else:
                f.write("No option selected\n")
        elif result['question_type'] == 'True/False':
            f.write(f'{result['boolean_answer']}\n')
        else:
            f.write(f'{result['question_number']} Unknown question type\n')
        f.write('\n')


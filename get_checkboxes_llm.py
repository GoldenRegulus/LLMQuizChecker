from pprint import pprint
from tqdm import tqdm
import google.generativeai as genai
import easygui
import json
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

DEBUG = True

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
file_paths = easygui.fileopenbox('Please upload student response', filetypes=[['*.png', '*.jpg', 'Images'], ['*.doc', '*.docx', 'Word Files'], ['*.pdf', 'PDF Files']], multiple=True)
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
        if result['question_type'] == 'Multiple Choice':
            print(result['question_number'], result['options'][argmax(result['options'], key=lambda x: x['marked'])]['content'])
        else:
            print(result['question_number'], result['boolean_answer']['boolean_value'])

# print_qa(final_json)

# answers = dict([(i['question_number'], argmax(list(map(lambda x: x['marked'], i['options']))) + 1) for i in res_json])

# if DEBUG:
#     print('\nDEBUG: Student Answers')
#     pprint(answers)

# with open(master_path, 'r') as f:
#     # print([k for line in f.readlines() for k in line.strip().split(',')])
#     rubric = dict([(int(line.strip().split(',')[0]), (int(line.strip().split(',')[1]), int(line.strip().split(',')[2]))) for line in f.readlines()])

# if DEBUG:
#     print('\nDEBUG: Rubric')
#     pprint(rubric)

# total = 0
# for (q, (a, m)) in rubric.items():
#     if q in answers:
#         total += m * (a == answers[q])

# print(f'Total: {total}/{sum([i[1] for i in rubric.values()])}')



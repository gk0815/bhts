
import json
import pandas as pd
import xlsxwriter
import openpyxl
import logging
from io import BytesIO
from xlrd import open_workbook
from flask import Flask, request, flash, url_for, redirect, make_response, jsonify
from ibm_watson import NaturalLanguageClassifierV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from werkzeug.utils import secure_filename
from flask import send_file, send_from_directory, safe_join, abort

app = Flask(__name__)

API_Key = 'JmWSCUWImhs5eeA24JwrmRWrnNyQShEAIme66xdOLMBY'

URL = 'https://api.us-south.natural-language-classifier.watson.cloud.ibm.com/instances/984f49d2-5f22-4273-b933-6912b331c78c'

Text = 'How hot will it be today?'

classifier_id = '3c5290x834-nlc-348'

Input_Excel_path = 'weather_excel1.xlsx'

Output_Excel_path = 'Output.xlsx'

authenticator = IAMAuthenticator(API_Key)
natural_language_classifier = NaturalLanguageClassifierV1(authenticator=authenticator)
natural_language_classifier.set_service_url(URL)


@app.route('/create', methods=['GET'])
def create_classifier():
    with open('./train.csv', 'rb') as training_data:
        classifier = natural_language_classifier.create_classifier(
			training_data=training_dat,
			training_metadata='{"name": "my_Classifier","language": "en"}'
		).get_result()
        print (json.dumps(classifier, indent=2))
        return classifier

@app.route('/check_status', methods=['GET'])
def check_status_classifier():
    status = natural_language_classifier.get_classifier(classifier_id).get_result()
    print (json.dumps(status, indent=2))
    return status

@app.route('/classify', methods=['GET'])
def classify_text():
    classes = natural_language_classifier.classify(classifier_id, Text).get_result()
    response = json.dumps(classes, indent=2)
    print (response)
    return classes

@app.route('/delete', methods=['GET'])
def delete_classifier():
    natural_language_classifier.delete_classifier(classifier_id)
    print ('Done')
    return 'Done'

@app.route('/api', methods=['GET', 'POST'])
def classify_excel():
    if request.method == 'POST':
        try:
            file_ = request.files['file']
        except KeyError as e:
            print (e)
            return make_response(jsonify(message="Sample file 'file' missing in POST request"), 400)
        cols = [0,1,2]
        df = pd.read_excel(file_, skiprows=1, usecols=cols)
        df.head()
        print (df)
        CPT_Number = df['CPT Number'].to_list()
        Quality_Classification = df['Quality Classification'].to_list()
        Brief_Description = df['Brief Description'].to_list()
        print (CPT_Number)
        print (Quality_Classification)
        print (Brief_Description)

        sheet = pd.DataFrame(columns=[
            'CPT_Number',
            'Quality_Classification',
            'Brief_Description',
            'Most_Probable_As_Reported_Code',
            'Most_Probable_As_Reported_Code_Confidence',
            'Second Most Probable As Reported Code',
            'Second Most Probable As Reported Code Confidence',
            'Level 1,2 & 3',
            'Level 4 &5',
            'Input to the System',
            ])

        count = 0
        try :
            for word in Brief_Description:
                response = natural_language_classifier.classify(classifier_id, word).get_result()
                top_class = response['top_class']
                # print (top_class)
                text = response['text']
                # print (text)
                # print (response['classes'])
                class_name = []
                confidence = []
                for classes in response['classes']:
                    print (classes['class_name'], ',', classes['confidence'])
                    class_name.append(classes['class_name'])
                    confidence.append(classes['confidence'])
                print (class_name)
                print (confidence)

                Most_Probable_As_Reported_Code = class_name[0]
                Most_Probable_As_Reported_Code_confidence = confidence[0]

                Second_Most_Probable_As_Reported_Code = class_name[1]
                Second_Most_Probable_As_Reported_Code_confidence = confidence[1]

                print (Most_Probable_As_Reported_Code, Most_Probable_As_Reported_Code_confidence)
                print (Second_Most_Probable_As_Reported_Code, Second_Most_Probable_As_Reported_Code_confidence)

                if Most_Probable_As_Reported_Code == response['top_class']:
                    print ('TRUE')

                count = count + 1
                print(count)

                sheet = sheet.append({
                    'Brief_Description': text,
                    'Most_Probable_As_Reported_Code': Most_Probable_As_Reported_Code,
                    'Most_Probable_As_Reported_Code_Confidence': Most_Probable_As_Reported_Code_confidence,
                    'Second Most Probable As Reported Code': Second_Most_Probable_As_Reported_Code,
                    'Second Most Probable As Reported Code Confidence': Second_Most_Probable_As_Reported_Code_confidence,
                    }, ignore_index = True)
        except Exception as e:
            logging.error('I am here --------------------', count)

        sheet['CPT_Number']= df['CPT Number']
        sheet['Quality_Classification'] = df['Quality Classification']
        print (sheet)
           
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet.to_excel(writer, index = False, header = True, sheet_name = 'API Output Format')

        # the writer has done its job
        writer.close()

        # go back to the beginning of the stream
        output.seek(0)
        print ('Done')
        return send_file(output, attachment_filename='Output.xlsx', as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        return jsonify({'result': request.get_array(field_name='file')})
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xlsx only)</h1>
    <form action="/api" method=post enctype=multipart/form-data>
    <p><input type=file name=file><input type=submit value=Upload>
    </form>
    '''

@app.route('/download', methods=['GET'])
def return_files_tut():
    try:
        return send_from_directory(xlsx_data, attachment_filename='Output.xlsx', as_attachment= True)
        output = BytesIO()
    except Exception as e:

        return str(e)

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

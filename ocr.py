
import os
from flask import Flask, render_template, request, redirect, url_for
import pytesseract


app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    folder_path = request.form['folder_path']
    keyword = "Sender's Reference"
    
    # Redirect to a new route that will execute the image processing code
    return redirect(url_for('execute_processing', folder_path=folder_path, keyword=keyword))

# Add a new route to execute the image processing code
@app.route('/execute_processing/<folder_path>/<keyword>')
def execute_processing(folder_path, keyword):
    from PIL import Image
    import pytesseract
    import os
    from flask import Flask, render_template

  
    def extract_reference_number(image_path, keyword):
        # Open the image file
        image = Image.open(image_path)

        # Use Tesseract OCR to extract text from the image
        extracted_text = pytesseract.image_to_string(image)

        # Find the index of the keyword in the extracted text
        keyword_index = extracted_text.find(keyword)

        if keyword_index != -1:
            # Extract the text after the keyword
            text_after_keyword = extracted_text[keyword_index + len(keyword):].strip()

            # Split the text and take the first word as the reference number
            reference_number = text_after_keyword.split()[0]

            return reference_number
        else:
            print(f"Keyword '{keyword}' not found in the image.")
            return None

    def process_folder(folder_path, keyword):
        # Get a list of all files in the specified folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        for file_name in files:
            # Create the full path to the image file
            image_path = os.path.join(folder_path, file_name)

            # Extract the reference number from the current image
            reference_number = extract_reference_number(image_path, keyword)

            # Rename the file with the extracted reference number
            if reference_number is not None:
                new_file_name = f"{reference_number}.jpg"
                new_file_path = os.path.join(folder_path, new_file_name)

                try:
                    os.rename(image_path, new_file_path)
                    print(f"File {file_name} renamed successfully to: {new_file_path}")
                except OSError as e:
                    print(f"Error renaming the file {file_name}: {e}")
            else:
                print(f"File {file_name} not renamed due to missing reference number.")
                
        return f"Processing complete for folder: {folder_path}"

    return process_folder(folder_path, keyword)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)

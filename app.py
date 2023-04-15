import PySimpleGUI as sg
from PIL import Image
import io
from flask import Flask, request, render_template, send_file, after_this_request
import platform
import webbrowser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    input_path = request.files['file'].stream
    try:
        with Image.open(input_path) as img:
            # Convert the input image to WebP format and store it in memory
            img_webp = io.BytesIO()
            img.save(img_webp, "webp")

            # Prompt the user to download or view the converted image
            download_layout = [
                [sg.Text("Select an option:")],
                [sg.Button("Download", key="-DOWNLOAD-"), sg.Button("View", key="-VIEW-")]
            ]
            download_window = sg.Window("Image Conversion Complete", download_layout)
            download_event, _ = download_window.read()

            # If the "Download" button is pressed, prompt the user to save the converted image to disk
            if download_event == "-DOWNLOAD-":
                filename = "converted_image.webp"
                with open(filename, "wb") as f:
                    f.write(img_webp.getvalue())
                @after_this_request
                def close_window(response):
                    download_window.close()
                    return response
                return send_file(filename, as_attachment=True)

            # If the "View" button is pressed, show the converted image in a new window
            elif download_event == "-VIEW-":
                view_layout = [[sg.Image(data=img_webp.getvalue())]]
                view_window = sg.Window("Converted Image", view_layout, finalize=True)
                view_window.Maximize()
                if platform.system() == "Darwin":
                    webbrowser.open("http://localhost:5000/close_window", new=0)
                else:
                    sg.popup_auto_close("Closing in 5 seconds...", auto_close_duration=5000)
                    view_window.close()

            download_window.close()

    except:
        sg.popup("An error occurred while converting the image")
    return ""

@app.route('/close_window')
def close_window():
    sg.popup_auto_close("Closing in 5 seconds...", auto_close_duration=5000)
    sg.Window.get_active_window().close()
    return "Window closed"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import dash
from dash import html
from dash.dependencies import Input, Output, State
import cv2
import base64
import numpy as np

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Video(id='camera-preview', autoPlay=False),
    html.Button('Scan QR Code', id='scan-button'),
    html.Div(id='qrcode-result')
])


# Function to decode base64 image data
def decode_image(base64_string):
    img_data = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


# Callback to capture video stream and display QR code result
@app.callback(
    Output('qrcode-result', 'children'),
    Input('scan-button', 'n_clicks'),
    State('camera-preview', 'src')
)
def scan_qrcode(n_clicks, camera_preview_src):
    if n_clicks is None:
        return None

    # Capture the current frame from the camera preview
    _, frame = cv2.VideoCapture(0).read()

    # Convert the frame to base64 for displaying in the Dash app
    retval, buffer = cv2.imencode('.jpg', frame)
    camera_preview_src = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')

    # Use an external library (e.g., pyzbar) to decode QR code from the frame
    # Install pyzbar using: pip install pyzbar
    from pyzbar.pyzbar import decode
    decoded_objects = decode(frame)

    # Display the result
    if decoded_objects:
        result_text = decoded_objects[0].data.decode('utf-8')
        return f'QR Code Result: {result_text}'
    else:
        return 'No QR Code detected'


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False, host='10.50.3.152', port=59280)
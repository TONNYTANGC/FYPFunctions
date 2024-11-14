from sklearn.preprocessing import MinMaxScaler
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import tensorflow as tf
import numpy as np
import uvicorn
import os
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ['TF_TENSORRT_DISABLE'] = '1'

app = FastAPI()

# Load your pre-trained GRU model
model = tf.keras.models.load_model('gru_model.h5')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # Receive heart rate data from the client as a comma-separated string
                data = await websocket.receive_text()
                logger.info(f"Received data: {data}")
                
                # Convert data to a NumPy array of floats
                heart_rate_data = np.array([float(x) for x in data.split(",")])
                logger.info(f"Processed heart rate data: {heart_rate_data}")
                
                # Define the sequence length (timesteps)
                sequence_length = len(heart_rate_data) - 1  # Exclude the last data point
                logger.info(f"Sequence length: {sequence_length}")

                # Reshape data for GRU input: (batch_size=1, timesteps, features)
                input_data = heart_rate_data[:-1].reshape((1, sequence_length, 1))
                logger.info(f"Input data shape for model: {input_data.shape}")

                # Initialize and fit scaler
                scaler = MinMaxScaler(feature_range=(0, 1))
                scaler.fit(heart_rate_data[:-1].reshape(-1, 1))

                # Model prediction
                predicted_heart_rate_scaled = model.predict(input_data)
                logger.info(f"Predicted scaled heart rate: {predicted_heart_rate_scaled}")

                # Inverse scaling to get the original heart rate
                predicted_heart_rate = scaler.inverse_transform(predicted_heart_rate_scaled)
                logger.info(f"Predicted heart rate (original scale): {predicted_heart_rate}")

                # Ensure predicted_heart_rate is a float for tolerance checking
                predicted_heart_rate_value = predicted_heart_rate[0][0] if predicted_heart_rate.size == 1 else float(predicted_heart_rate[0][0])
                logger.info(f"Predicted heart rate value (for comparison): {predicted_heart_rate_value}")

                # Current heart rate and tolerance
                current_heart_rate = heart_rate_data[-1]
                tolerance = 10
                logger.info(f"Current heart rate: {current_heart_rate}, Tolerance: {tolerance}")

                # Check within tolerance range
                if (predicted_heart_rate_value - tolerance) <= current_heart_rate <= (predicted_heart_rate_value + tolerance):
                    response = "Normal"
                else:
                    response = "Abnormal"
                
                # Send response
                await websocket.send_text(response)

            except ValueError as e:
                logger.error(f"Value error processing data: {e}")
            except TypeError as e:
                logger.error(f"Type error processing data: {e}")
            except Exception as e:
                # Print complete error details for debugging
                error_message = f"Unexpected error processing data: {traceback.format_exc()}"
                logger.error(error_message)
                break
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by the client.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
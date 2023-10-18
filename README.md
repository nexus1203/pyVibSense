# pyVibSense :chart_with_upwards_trend:
pyVibSense is the official user interface designed for data collection and visualization using the [VibSense](https://github.com/nexus1203/VibSense) wireless vibration sensor.

:star: **Key Features**:
- **Real-time Data Visualization**: Seamlessly view and analyze vibration data in real-time.
- **Socket Integration**: Built-in socket communication ensures efficient data transfer from VibSense devices.
- **Modern UI**: Powered by PyQt5, pyVibSense offers a sleek and intuitive user interface.
- **Easy Data Export**: Export the collected data in csv format for further processing or analysis.

## :gear: Requirements

- Python 3.x
- PyQt5
- pyqtgraph
- socket
- numpy
- scipy

## :rocket: Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nexus1203/pyVibSense.git
2. **Navigate to the Directory and Install Dependencies:**
  ```bash
  Copy code
  cd pyVibSense
  pip install -r requirements.txt
  ```
3. **Run the Application:**
  ```bash
  Copy code
  python main.py
  ```

:computer: Usage

Ensure your VibSense device is powered on and transmitting data.
Launch the pyVibSense application.
Connect to the VibSense device using the provided interface.
Begin real-time data visualization and collection.

:bulb: Tips

Make sure the VibSense device and the machine running pyVibSense are on the same network for successful data transmission.
For issues or feature requests, please raise an issue in the GitHub repository.

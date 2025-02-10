# Blood Pressure Monitor

A web application for tracking and managing blood pressure measurements, built with Flask. Just created this as my doctor asked me to monitor my blood pressure for some time and report back, and I didn't want to use my blood pressure monitor's app for privacy reasons. Works with ANY blood pressure monitor because you just input your measurements to the app manually. Comes with easy Light/Dark mode switching.

Measurements are entered in batches of 3, as it is recommended by doctors that you take 3 measurements every time you take your blood pressure and use their average.

## Features

### User Management
- Create new user profiles with first name, last name, and date of birth
- View all registered users on the home page
- Delete user profiles and their associated data

### Measurement Recording
- Record up to 3 blood pressure measurements at a time
- Each measurement includes:
  - Systolic pressure (30-230 mmHg)
  - Diastolic pressure (30-230 mmHg)
  - Heart rate/BPM (30-230 bpm)
- Automatic validation of measurement ranges
- All measurements are timestamped

### Reporting and Analysis
- View measurements in various time periods:
  - Today
  - Last 7 days
  - Last week (Monday to Sunday)
  - Last 30 days
  - Custom date range
- Statistical analysis including:
  - Minimum values
  - Maximum values
  - Average values
- Visual indicators for blood pressure categories:
  - Optimal
  - Normal
  - High Normal
  - High
  - Very High

### Data Management
- Export measurements to CSV file
- Import measurements from CSV file
- Generate PDF reports with:
  - User information
  - Date range statistics
  - Averaged measurements (multiple readings taken at the same time are averaged)
- PDF reports open in a new tab for easy printing

### Data Format
CSV files must follow this format:

csv
Date,Time,Systolic,Diastolic,BPM
05/02/2024,11:52,118,77,80
05/02/2024,11:52,112,72,70

Easiest way is to create a user, add a first set of measurements, export a CSV, then open that in Excel to understant the formatting you need to create a new CSV to import.

- Date format: DD/MM/YYYY
- Time format: HH:MM
- Values must be within valid ranges (30-230)

### Blood Pressure Categories

#### Systolic (mmHg)
- < 90: Low
- 90-119: Optimal
- 120-129: Normal
- 130-139: High Normal
- => 140: High

#### Diastolic (mmHg)
- < 60: Low
- 60-79: Optimal
- 80-84: Normal
- 85-89: High Normal
- => 90: High

## Security
- Input validation for all form submissions
- CSRF protection
- Secure file uploads with type checking
- Error handling for all operations

## License
AGPL-3.0 license

## Authors
BuggyPasta, with lots of help from A.I. because BuggyPasta is otherwise WORTHLESS in programming

## Acknowledgments
Vectors and icons by <a href="https://www.figma.com/@maryakveo?ref=svgrepo.com" target="_blank">Mary Akveo</a> in PD License via <a href="https://www.svgrepo.com/" target="_blank">SVG Repo</a>

## Docker Installation

### Prerequisites
- Docker
- Docker Compose

### Installation with Docker Compose

```yaml
version: '3.8'

services:
  bloodpressuretracker:
    container_name: bloodpressuretracker
    build:
      context: https://github.com/BuggyPasta/BloodPressureTracker.git
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    volumes:
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/data:/app/data
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/config:/app/config
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/db:/app/db
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
```

## Future development
None planned, which is why you see in the docker compose above the 2 last lines instructing Watchtower to not bother checking for any updates. If you are not running Watchtower, feel free to remove them.


## VERY IMPORTANT NOTE. NO, SERIOUSLY.
This app is designed to work ONLY ON A LOCAL environment and is NOT secured in any way to work exposed to the Internet. As it will contain sensitive personal data, remember that you use it at your own risk. I STRONGLY recommend that you DO NOT EXPOSE it publically. Also, make sure you read the DISCLAIMER below.

## DISCLAIMER

This application is intended for informational and personal tracking purposes only. It is not a medical device and does not provide medical advice, diagnosis, or treatment. The information presented, including calculations and trends, MAY NOT be accurate or reliable and should NOT be used as a substitute for professional medical advice from a qualified healthcare provider.

There is absolutely NO guarantee that the calculations, averages, or any other data provided by this application are correct. Always consult with your doctor or healthcare professional regarding any questions or concerns about your health or medical condition. Do NOT rely on this application for medical decisions or emergencies.

The developer(s) of this application are not responsible for any inaccuracies, misinterpretations, or misuse of the information provided. By using this application, you acknowledge that you automatically assume full and exclusive responsibility for your health decisions and agree that the developer(s) shall not be held liable for any consequences arising from your use of this application.
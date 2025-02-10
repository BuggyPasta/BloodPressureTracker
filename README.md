# Blood Pressure Monitor

A web application for tracking and managing blood pressure measurements, built with Flask.

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
  - ?? Optimal
  - ?? Normal
  - ?? High Normal
  - ?? High
  - ?? Very High

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

- Date format: DD/MM/YYYY
- Time format: HH:MM
- Values must be within valid ranges (30-230)

## Technical Details

### Built With
- Python/Flask
- SQLAlchemy
- ReportLab (PDF generation)
- JavaScript/jQuery
- Bootstrap 5

### Requirements
- Python 3.x
- Flask
- SQLAlchemy
- ReportLab
- Other dependencies listed in requirements.txt

### Blood Pressure Categories

#### Systolic (mmHg)
- < 90: Low
- 90-119: Optimal
- 120-129: Normal
- 130-139: High Normal
- = 140: High

#### Diastolic (mmHg)
- < 60: Low
- 60-79: Optimal
- 80-84: Normal
- 85-89: High Normal
- = 90: High

## Security
- Input validation for all form submissions
- CSRF protection
- Secure file uploads with type checking
- Error handling for all operations

## License
[Your chosen license]

## Contributing
Do as you like!

## Authors
Buggy Pasta, with the help of A.I. because he is otherwise worthless in programming

## Acknowledgments
- Vectors and icons by <a href="https://www.figma.com/@maryakveo?ref=svgrepo.com" target="_blank">Mary Akveo</a> in PD License via <a href="https://www.svgrepo.com/" target="_blank">SVG Repo</a>

## Docker Installation

### Prerequisites
- Docker
- Docker Compose

### Installation with Docker Compose

version: '3.8'

services:
  bloodpressuretracker:
    container_name: bloodpressuretracker
    build:
      context: https://github.com/BuggyPasta/BloodPressureTracker.git
      dockerfile: Dockerfile
    ports:
      - "2025:5000"
    volumes:
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/data:/app/data
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/config:/app/config
      - /home/YOUR_USER_FOLDER/bloodpressuretracker/db:/app/db
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
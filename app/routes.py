from io import BytesIO
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, Response
from .models import db, User, Measurement
from datetime import datetime, timedelta, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import csv
import json
import io

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    users = User.query.order_by(User.first_name, User.last_name, User.date_of_birth).all()
    return render_template('home.html', users=users)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%d/%m/%Y').date()
            ).first()
            
            if existing_user:
                return jsonify({'error': 'User already exists'}), 400
                
            # Create new user
            user = User(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%d/%m/%Y').date()
            )
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'message': 'User registered successfully', 'user_id': user.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
            
    return render_template('register.html')

@bp.route('/user/<int:user_id>')
def user_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_dashboard.html', user=user)

@bp.route('/user/<int:user_id>/add_measurements', methods=['GET', 'POST'])
def add_measurements(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            current_datetime = datetime.now()
            measurements_data = []
            
            for i in range(1, 4):
                systolic = request.form.get(f'systolic_{i}')
                diastolic = request.form.get(f'diastolic_{i}')
                bpm = request.form.get(f'bpm_{i}')
                
                if not all([systolic, diastolic, bpm]):
                    continue
                    
                try:
                    systolic = int(systolic)
                    diastolic = int(diastolic)
                    bpm = int(bpm)
                    
                    if not (30 <= systolic <= 230 and 30 <= diastolic <= 230 and 30 <= bpm <= 230):
                        return jsonify({'error': 'Please check your input, something doesn\'t look right'}), 400
                        
                    measurements_data.append({
                        'systolic': systolic,
                        'diastolic': diastolic,
                        'bpm': bpm
                    })
                except ValueError:
                    return jsonify({'error': 'Please check your input, something doesn\'t look right'}), 400
            
            for data in measurements_data:
                measurement = Measurement(
                    user_id=user_id,
                    date=current_datetime.date(),
                    time=current_datetime.time(),
                    systolic=data['systolic'],
                    diastolic=data['diastolic'],
                    bpm=data['bpm']
                )
                db.session.add(measurement)
            
            db.session.commit()
            return jsonify({'message': 'Measurements saved successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error saving measurements'}), 500
            
    return render_template('add_measurements.html', user=user)

@bp.route('/user/<int:user_id>/report')
def view_report(user_id):
    user = User.query.get_or_404(user_id)
    report_type = request.args.get('type')
    
    # If no report type is specified, just show the selection screen
    if not report_type:
        return render_template('view_report.html', 
                             user=user,
                             measurements=None,
                             stats=None,
                             start_date=None,
                             end_date=None)
    
    # Calculate date range based on report type
    end_date = datetime.now().date()
    if report_type == 'today':
        start_date = end_date
    elif report_type == 'last_10_days':
        start_date = end_date - timedelta(days=9)
    elif report_type == 'custom':
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%d/%m/%Y').date()
            end_date = datetime.strptime(request.args.get('end_date'), '%d/%m/%Y').date()
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Invalid date format'})
            flash('Invalid date format')
            return redirect(url_for('main.user_dashboard', user_id=user_id))

    # Get measurements and group by date/time
    measurements = Measurement.query.filter(
        Measurement.user_id == user_id,
        Measurement.date >= start_date,
        Measurement.date <= end_date
    ).order_by(Measurement.date, Measurement.time).all()

    # Group measurements by date and time
    grouped_measurements = {}
    for m in measurements:
        key = (m.date, m.time)
        if key not in grouped_measurements:
            grouped_measurements[key] = []
        grouped_measurements[key].append(m)

    # Calculate averages for each group
    averaged_measurements = []
    for (date, time), group in grouped_measurements.items():
        avg_systolic = round(sum(m.systolic for m in group) / len(group))
        avg_diastolic = round(sum(m.diastolic for m in group) / len(group))
        avg_bpm = round(sum(m.bpm for m in group) / len(group))
        
        avg_measurement = Measurement(
            user_id=user_id,
            date=date,
            time=time,
            systolic=avg_systolic,
            diastolic=avg_diastolic,
            bpm=avg_bpm
        )
        averaged_measurements.append(avg_measurement)

    # Sort the averaged measurements
    averaged_measurements.sort(key=lambda m: (m.date, m.time))

    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not averaged_measurements:
            return jsonify({'error': 'No data found'})
        return jsonify({'success': True})

    # Calculate statistics using averaged measurements
    stats = calculate_stats(averaged_measurements) if averaged_measurements else None

    return render_template('view_report.html', 
                         user=user,
                         measurements=averaged_measurements,
                         stats=stats,
                         start_date=start_date,
                         end_date=end_date,
                         get_bp_icon=get_bp_icon)

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        confirmation = request.form.get('confirmation')
        
        if confirmation != 'DELETE':
            return jsonify({'error': 'Invalid confirmation'}), 400
            
        Measurement.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error deleting user'}), 500

@bp.route('/user/<int:user_id>/export_csv')
def export_csv(user_id):
    try:
        user = User.query.get_or_404(user_id)
        measurements = Measurement.query.filter_by(user_id=user_id).order_by(Measurement.date, Measurement.time).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Time', 'Systolic', 'Diastolic', 'BPM'])
        
        for m in measurements:
            writer.writerow([
                m.date.strftime('%d/%m/%Y'),
                m.time.strftime('%H:%M'),
                m.systolic,
                m.diastolic,
                m.bpm
            ])
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=measurements_{user.first_name}_{user.last_name}.csv'}
        )
    except Exception as e:
        return jsonify({'error': 'Error exporting CSV'}), 500

@bp.route('/user/<int:user_id>/import_csv', methods=['POST'])
def import_csv(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV format'}), 400
            
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            rows_added = 0
            
            for row in csv_reader:
                try:
                    measurement = Measurement(
                        user_id=user_id,
                        date=datetime.strptime(row['Date'], '%d/%m/%Y').date(),
                        time=datetime.strptime(row['Time'], '%H:%M').time(),
                        systolic=int(row['Systolic']),
                        diastolic=int(row['Diastolic']),
                        bpm=int(row['BPM'])
                    )
                    db.session.add(measurement)
                    rows_added += 1
                except (ValueError, KeyError) as e:
                    db.session.rollback()
                    return jsonify({'error': f'Invalid data format in CSV: {str(e)}'}), 400
                
            db.session.commit()
            return jsonify({'message': f'CSV imported successfully. {rows_added} measurements added.'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error processing CSV file: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error importing CSV: {str(e)}'}), 500

@bp.route('/user/<int:user_id>/generate_pdf', methods=['POST'])
def generate_pdf_report(user_id):
    try:
        user = User.query.get_or_404(user_id)
        start_date = datetime.strptime(request.form['start_date'], '%d/%m/%Y').date()
        end_date = datetime.strptime(request.form['end_date'], '%d/%m/%Y').date()
        
        # Get measurements and group by date/time
        measurements = Measurement.query.filter(
            Measurement.user_id == user_id,
            Measurement.date >= start_date,
            Measurement.date <= end_date
        ).order_by(Measurement.date, Measurement.time).all()

        # Group measurements by date and time
        grouped_measurements = {}
        for m in measurements:
            key = (m.date, m.time)
            if key not in grouped_measurements:
                grouped_measurements[key] = []
            grouped_measurements[key].append(m)

        # Calculate averages for each group
        averaged_measurements = []
        for (date, time), group in grouped_measurements.items():
            avg_systolic = round(sum(m.systolic for m in group) / len(group))
            avg_diastolic = round(sum(m.diastolic for m in group) / len(group))
            avg_bpm = round(sum(m.bpm for m in group) / len(group))
            
            avg_measurement = Measurement(
                user_id=user_id,
                date=date,
                time=time,
                systolic=avg_systolic,
                diastolic=avg_diastolic,
                bpm=avg_bpm
            )
            averaged_measurements.append(avg_measurement)

        # Sort the averaged measurements
        averaged_measurements.sort(key=lambda m: (m.date, m.time))
        
        if not averaged_measurements:
            return jsonify({'error': 'No data found for the chosen period'}), 404

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
            title=f'Blood Pressure Report - {user.first_name} {user.last_name}'  # Add PDF title
        )

        styles = getSampleStyleSheet()
        # Center-aligned title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # 1 = center
            spaceAfter=20
        )
        
        # Style for user info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,  # Center-aligned
            spaceAfter=5
        )

        elements = []
        
        # Center-aligned title
        elements.append(Paragraph(
            f"Blood Pressure History<br/>{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}",
            title_style
        ))
        
        # User info on one line with separators
        elements.append(Paragraph(
            f"{user.first_name} {user.last_name} | "
            f"DOB: {user.date_of_birth.strftime('%d %B %Y')} | "
            f"Age: {user.get_age()} years",
            info_style
        ))
        elements.append(Spacer(1, 30))

        # Statistics table with improved formatting
        stats = calculate_stats(averaged_measurements)
        stats_data = [
            ['', 'Minimum', 'Maximum', 'Average'],
            ['Systolic', stats['systolic']['min'], stats['systolic']['max'], stats['systolic']['avg']],
            ['Diastolic', stats['diastolic']['min'], stats['diastolic']['max'], stats['diastolic']['avg']],
            ['BPM', stats['bpm']['min'], stats['bpm']['max'], stats['bpm']['avg']]
        ]
        
        stats_table = Table(stats_data, colWidths=[doc.width/4]*4)
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 30))

        # Measurements table with improved formatting
        table_data = [['Date', 'Time', 'Systolic', 'Diastolic', 'BPM']]
        for m in averaged_measurements:
            table_data.append([
                m.date.strftime('%d/%m/%Y'),
                m.time.strftime('%H:%M'),
                str(m.systolic),
                str(m.diastolic),
                str(m.bpm)
            ])
        
        measurements_table = Table(table_data, colWidths=[doc.width/5]*5)
        measurements_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(measurements_table)

        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            download_name=f'BP_Report_{user.last_name}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF report'}), 500

def calculate_stats(measurements):
    try:
        systolic_values = [m.systolic for m in measurements]
        diastolic_values = [m.diastolic for m in measurements]
        bpm_values = [m.bpm for m in measurements]
        
        return {
            'systolic': {
                'min': min(systolic_values),
                'max': max(systolic_values),
                'avg': round(sum(systolic_values) / len(systolic_values))
            },
            'diastolic': {
                'min': min(diastolic_values),
                'max': max(diastolic_values),
                'avg': round(sum(diastolic_values) / len(diastolic_values))
            },
            'bpm': {
                'min': min(bpm_values),
                'max': max(bpm_values),
                'avg': round(sum(bpm_values) / len(bpm_values))
            }
        }
    except Exception as e:
        # Return default values if calculation fails
        return {
            'systolic': {'min': 0, 'max': 0, 'avg': 0},
            'diastolic': {'min': 0, 'max': 0, 'avg': 0},
            'bpm': {'min': 0, 'max': 0, 'avg': 0}
        }

def get_bp_icon(type, value):
    try:
        if type == 'systolic':
            if value < 90:
                return 'Face3Neutral.svg'
            elif value < 120:
                return 'Face1VeryHappy.svg'
            elif value <= 129:
                return 'Face2Happy.svg'
            elif value <= 139:
                return 'Face4Unhappy.svg'
            else:
                return 'Face5VeryUnhappy.svg'
        else:  # diastolic
            if value < 60:
                return 'Face3Neutral.svg'
            elif value < 80:
                return 'Face1VeryHappy.svg'
            elif value <= 84:
                return 'Face2Happy.svg'
            elif value <= 89:
                return 'Face4Unhappy.svg'
            else:
                return 'Face5VeryUnhappy.svg'
    except Exception as e:
        return 'Face3Neutral.svg'  # Return neutral face as default

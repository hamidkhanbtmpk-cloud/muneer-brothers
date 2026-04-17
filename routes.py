import os
import secrets
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, current_user, logout_user, login_required
from models import db, Service, Client, Message, User, Employee, Office
from flask_bcrypt import Bcrypt

bp = Blueprint('routes', __name__)
bcrypt = Bcrypt()

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    if not os.path.exists(os.path.dirname(picture_path)):
        os.makedirs(os.path.dirname(picture_path))
    form_picture.save(picture_path)
    return picture_fn

@bp.route('/')
def index():
    services = Service.query.all()
    employees = Employee.query.order_by(Employee.serial_no.asc()).all()
    offices = Office.query.all()
    return render_template('index.html', services=services, employees=employees, offices=offices)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        msg = request.form.get('message')
        if not name or not email or not msg:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('routes.contact'))
        new_message = Message(name=name, email=email, message=msg)
        db.session.add(new_message)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('routes.contact'))
    return render_template('contact.html')

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Login Unsuccessful. Please check credentials.', 'danger')
    return render_template('admin/login.html')

@bp.route('/admin/dashboard')
@login_required
def dashboard():
    s_count = Service.query.count()
    m_count = Message.query.count()
    e_count = Employee.query.count()
    o_count = Office.query.count()
    messages = Message.query.order_by(Message.timestamp.desc()).limit(5).all()
    return render_template('admin/dashboard.html', s_count=s_count, m_count=m_count, e_count=e_count, o_count=o_count, messages=messages)

@bp.route('/admin/employees', methods=['GET', 'POST'])
@login_required
def manage_employees():
    if request.method == 'POST':
        name = request.form.get('name')
        designation = request.form.get('designation')
        description = request.form.get('description')
        serial_no = request.form.get('serial_no', 0)
        picture_file = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                picture_file = save_picture(file)
        new_emp = Employee(name=name, designation=designation, description=description, image_file=picture_file, serial_no=int(serial_no))
        db.session.add(new_emp)
        db.session.commit()
        flash('Expert added!', 'success')
        return redirect(url_for('routes.manage_employees'))
    employees = Employee.query.order_by(Employee.serial_no.asc()).all()
    return render_template('admin/employees.html', employees=employees)

@bp.route('/admin/employee/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.name = request.form.get('name')
        emp.designation = request.form.get('designation')
        emp.description = request.form.get('description')
        emp.serial_no = int(request.form.get('serial_no', 0))
        if 'image' in request.files and request.files['image'].filename != '':
            emp.image_file = save_picture(request.files['image'])
        db.session.commit()
        flash('Expert updated!', 'success')
        return redirect(url_for('routes.manage_employees'))
    return render_template('admin/edit_employee.html', emp=emp)

@bp.route('/admin/employee/delete/<int:id>')
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash('Expert removed successfully!', 'danger')
    return redirect(url_for('routes.manage_employees'))

@bp.route('/admin/offices', methods=['GET', 'POST'])
@login_required
def manage_offices():
    if request.method == 'POST':
        office_type = request.form.get('office_type')
        address = request.form.get('address')
        new_office = Office(office_type=office_type, address=address)
        db.session.add(new_office)
        db.session.commit()
        flash('Office added!', 'success')
        return redirect(url_for('routes.manage_offices'))
    offices = Office.query.all()
    return render_template('admin/offices.html', offices=offices)

@bp.route('/admin/office/delete/<int:id>')
@login_required
def delete_office(id):
    off = Office.query.get_or_404(id)
    db.session.delete(off)
    db.session.commit()
    flash('Office removed!', 'danger')
    return redirect(url_for('routes.manage_offices'))

@bp.route('/admin/services', methods=['GET', 'POST'])
@login_required
def manage_services():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        picture_file = 'service_default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                picture_file = save_picture(file)
        new_service = Service(title=title, description=description, image=picture_file)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('routes.manage_services'))
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@bp.route('/admin/service/delete/<int:id>')
@login_required
def delete_service(id):
    ser = Service.query.get_or_404(id)
    db.session.delete(ser)
    db.session.commit()
    flash('Service removed!', 'danger')
    return redirect(url_for('routes.manage_services'))

@bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('routes.index'))
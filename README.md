# Survey Management System

A comprehensive survey management system built with Django, featuring Persian language support, PDF report generation, and a modern user interface.

## Features

- **Multi-section Surveys**: Create and manage surveys with multiple sections
- **Persian Language Support**: Full RTL support with Persian date handling
- **PDF Report Generation**: Automatic PDF generation of survey responses
- **Modern UI/UX**: Clean and responsive interface with Bootstrap 5
- **Admin Dashboard**: Comprehensive admin interface for survey management
- **User Authentication**: Secure login and registration system
- **Session Management**: Track survey completion status
- **Customizable Copyright**: Easy configuration through environment variables

## Tech Stack

- **Backend**: Django 5.1.7
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (default), PostgreSQL (optional)
- **PDF Generation**: ReportLab
- **Date Handling**: django-jalali, django-jalali-date
- **Text Processing**: arabic-reshaper, python-bidi
- **Production Server**: Gunicorn
- **Static Files**: Whitenoise

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/survey-project.git
cd survey-project
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
COPYRIGHT_TEXT=تمامی حقوق این سامانه متعلق به شرکت ... می‌باشد © 2024
COPYRIGHT_LINK=https://example.com
COPYRIGHT_COMPANY=نام شرکت
```

5. Run migrations:
```bash
cd myproject
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
survey-project/
├── myproject/                 # Main project directory
│   ├── manage.py
│   ├── myproject/            # Project settings
│   ├── surveys/              # Main app
│   │   ├── migrations/
│   │   ├── static/
│   │   ├── templates/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   └── staticfiles/          # Collected static files
├── static/                   # Project-wide static files
├── templates/               # Project-wide templates
├── requirements.txt         # Project dependencies
└── .env                    # Environment variables
```

## Usage

1. **Admin Interface**
   - Access admin panel at `/admin/`
   - Create and manage surveys
   - View survey responses

2. **Survey Creation**
   - Create new surveys with multiple sections
   - Add questions with various types
   - Set survey status (active/inactive)

3. **Survey Taking**
   - Users can take surveys
   - Progress is saved automatically
   - PDF reports are generated upon completion

4. **PDF Reports**
   - Automatic generation of survey responses
   - Persian text support
   - Professional formatting

## Deployment

For production deployment:

1. Set `DEBUG=False` in settings.py
2. Configure your web server (Nginx/Apache)
3. Set up proper security measures
4. Configure static files serving
5. Set up database (PostgreSQL recommended)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django framework and its community
- Bootstrap team for the UI framework
- All contributors and maintainers of the used packages

## Contact

Arash Bordbar - [@bordbararash](https://twitter.com/bordbararash) - bordbar@fums.ac.ir


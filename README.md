# Hotel Booking System

A comprehensive web-based hotel booking system built with Django that allows users to book hotel rooms, manage reservations, and handle hotel information efficiently.

## Features

- User authentication and authorization
- Hotel room management
- Booking system
- Admin dashboard
- Responsive design
- Media handling for hotel images
- Database management

## Technology Stack

- Python 3.x
- Django
- SQLite (Database)
- HTML/CSS
- JavaScript
- Bootstrap

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AbdullahHashmi663/HBS-07-05.git
cd HBS-07-05
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `hotel/` - Main application directory
- `hotel_booking_system/` - Project settings directory
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded media files
- `manage.py` - Django management script

## Usage

1. Access the admin panel at `http://localhost:8000/admin`
2. Create hotel information and room details
3. Users can register and book rooms through the main interface
4. Manage bookings and reservations through the admin panel

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Abdullah Hashmi - [GitHub Profile](https://github.com/AbdullahHashmi663)

Project Link: [https://github.com/AbdullahHashmi663/HBS-07-05](https://github.com/AbdullahHashmi663/HBS-07-05) 
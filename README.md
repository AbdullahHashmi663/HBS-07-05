# Hotel Management System

A comprehensive web-based hotel booking and management system built with Django, designed to streamline hotel operations and enhance guest experience.

## Features

- **User Management**
  - User authentication and authorization
  - Role-based access control (Admin, Receptionist)
  - User profile management

- **Room Management**
  - Room type creation and management
  - Room status tracking (Available, Occupied, Maintenance)
  - Room amenities and pricing configuration
  - Room image upload and display

- **Booking System**
  - Online room booking and reservation
  - Check-in/Check-out management
  - Booking status tracking
  - Special requests handling

- **Guest Management**
  - Guest information storage
  - ID document upload and verification
  - Guest history tracking
  - Multiple ID types support (Passport, CNIC, Driving License)

- **Administrative Features**
  - Dashboard with key metrics
  - Booking reports and analytics
  - Payment processing
  - System configuration

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (Development)
- **Frontend**: 
  - HTML/CSS/JavaScript
  - Bootstrap
  - Crispy Forms
- **Additional Tools**:
  - Pillow (Image processing)
  - xhtml2pdf (PDF generation)
  - ReportLab (PDF reports)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdullahHashmi663/Hotel-Management-System.git
   cd Hotel-Management-System
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Project Structure

```
Hotel-Management-System/
├── hotel/                  # Main application
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   ├── static/            # Static files (CSS, JS, images)
│   └── management/        # Custom management commands
├── hotel_booking_system/  # Project configuration
├── media/                 # User uploaded files
├── static/               # Static files
└── templates/            # Base templates
```

## Usage

1. **Admin Access**
   - Log in with superuser credentials
   - Access admin dashboard at `/admin/`
   - Manage users, rooms, and system settings

2. **Room Management**
   - Create and edit room types
   - Set room prices and amenities
   - Upload room images
   - Track room status

3. **Booking Process**
   - Browse available rooms
   - Make reservations
   - Process check-ins/check-outs
   - Handle payments

4. **Guest Management**
   - Register new guests
   - Upload guest documents
   - Track guest history
   - Manage guest preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries or support, please contact the project maintainer at [your-email@example.com]

## Acknowledgments

- Django Documentation
- Bootstrap
- Crispy Forms
- All contributors and supporters 
import sqlite3

def create_hotelinfo_table():
    # Connect to SQLite database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hotel_hotelinfo';")
    if cursor.fetchone() is None:
        # Create the HotelInfo table if it doesn't exist
        cursor.execute('''
        CREATE TABLE hotel_hotelinfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL DEFAULT 'Hotel Booking System',
            address VARCHAR(255) NOT NULL DEFAULT '123 Hotel Street, City Name',
            phone VARCHAR(20) NOT NULL DEFAULT '+123 456 7890',
            email VARCHAR(254) NOT NULL DEFAULT 'info@hotelname.com',
            logo VARCHAR(100) NULL,
            description TEXT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Insert default record
        cursor.execute('''
        INSERT INTO hotel_hotelinfo (name, address, phone, email, description)
        VALUES ('Hotel Booking System', '123 Hotel Street, City Name', '+123 456 7890', 'info@hotelname.com', '');
        ''')
        
        print("HotelInfo table created successfully")
    else:
        print("HotelInfo table already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_hotelinfo_table() 
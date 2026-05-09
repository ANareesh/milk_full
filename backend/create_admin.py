"""Script to create an admin user interactively."""
import sys
import os

sys.path.insert(0, r'c:\Users\arena\OneDrive\Desktop\ASN-Dairy-Farm\ASN-Dairy-Farm\backend')

from app.core.database import SessionLocal
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.models.user import UserRole


def create_admin_user():
    """Create a new admin user."""
    print("\n" + "="*60)
    print("     CREATE ADMIN USER")
    print("="*60)
    
    # Get user input
    username = input("\nEnter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    full_name = input("Enter admin full name: ").strip()
    phone_number = input("Enter phone number (optional, press Enter to skip): ").strip() or None
    password = input("Enter admin password: ").strip()
    
    # Validate inputs
    if not username or not email or not full_name or not password:
        print("\n✗ Error: Username, email, full name, and password are required!")
        return
    
    if "@" not in email:
        print("\n✗ Error: Invalid email format!")
        return
    
    if len(password) < 6:
        print("\n✗ Error: Password must be at least 6 characters!")
        return
    
    # Create user object
    user_data = UserCreate(
        username=username,
        email=email,
        full_name=full_name,
        phone_number=phone_number,
        password=password,
        role=UserRole.admin,
    )
    
    # Create user in database
    db = SessionLocal()
    try:
        user = AuthService.register_user(db, user_data)
        print("\n" + "="*60)
        print("✓ Admin user created successfully!")
        print("="*60)
        print(f"  User ID:      {user.id}")
        print(f"  Username:     {user.username}")
        print(f"  Email:        {user.email}")
        print(f"  Full Name:    {user.full_name}")
        print(f"  Phone:        {user.phone_number or 'N/A'}")
        print(f"  Role:         {user.role}")
        print("="*60 + "\n")
    except ValueError as e:
        print(f"\n✗ Error: {e}\n")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()

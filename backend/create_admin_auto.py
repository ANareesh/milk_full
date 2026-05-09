"""Script to create an admin user directly."""
import sys
sys.path.insert(0, r'c:\Users\arena\OneDrive\Desktop\ASN-Dairy-Farm\ASN-Dairy-Farm\backend')

from app.core.database import SessionLocal
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.models.user import UserRole

# Admin credentials
admin_username = "admin"
admin_email = "nareesh9are@gmail.com"
admin_full_name = "Admin User"
admin_phone = "6300437431"
admin_password = "Randstad@12345"

db = SessionLocal()
try:
    # Check if admin already exists
    from app.crud.user import crud_user
    existing_admin = crud_user.get_by_username(db, admin_username)
    if existing_admin:
        print(f"\n✗ Admin user '{admin_username}' already exists!")
        print(f"   ID: {existing_admin.id}")
        print(f"   Email: {existing_admin.email}\n")
        sys.exit(0)
    
    # Create admin user
    user_data = UserCreate(
        username=admin_username,
        email=admin_email,
        full_name=admin_full_name,
        phone_number=admin_phone,
        password=admin_password,
        role=UserRole.admin,
    )
    
    user = AuthService.register_user(db, user_data)
    
    print("\n" + "="*60)
    print("✓ ADMIN USER CREATED SUCCESSFULLY")
    print("="*60)
    print(f"  User ID:      {user.id}")
    print(f"  Username:     {user.username}")
    print(f"  Email:        {user.email}")
    print(f"  Full Name:    {user.full_name}")
    print(f"  Phone:        {user.phone_number}")
    print(f"  Role:         {user.role}")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
finally:
    db.close()

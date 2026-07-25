"""
Step 2 Tests – Models (No DB required, tests structure & logic only)
Run with: python test_step2.py
"""
import sys
print("=" * 55)
print("   SKILLLOOP - STEP 2 MODEL TESTS")
print("=" * 55)

# ---------------------------------------------------------------
# TEST 1: Import all models
# ---------------------------------------------------------------
print("\n[TEST 1] Importing all models...")
try:
    from app.models.user         import User, UserModel
    from app.models.gig          import GigModel
    from app.models.order        import OrderModel
    from app.models.wallet       import WalletModel, TransactionModel
    from app.models.message      import MessageModel
    from app.models.notification import NotificationModel
    from app.models.project      import ProjectModel, BidModel
    from app.models.review       import ReviewModel
    print("  ✅ All models imported successfully")
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    sys.exit(1)

# ---------------------------------------------------------------
# TEST 2: User object creation (no DB)
# ---------------------------------------------------------------
print("\n[TEST 2] User object creation...")
fake_user_data = {
    "user_id":    1,
    "name":       "Ali Hassan",
    "email":      "ali@uni.edu",
    "password_hash": None,
    "university": "FAST University",
    "country":    "Pakistan",
    "bio":        "Full stack developer",
    "profile_pic": None,
    "role":       "both",
    "is_verified": True,
    "verification_method": "email",
    "auth_provider": "local",
    "google_id":  None,
    "is_active":  True,
    "joined_at":  None,
    "last_login": None,
    "rating":     4.8,
    "total_reviews": 12
}

user = User(fake_user_data)
assert user.name       == "Ali Hassan",        "❌ name mismatch"
assert user.email      == "ali@uni.edu",       "❌ email mismatch"
assert user.is_seller() == True,               "❌ seller check failed"
assert user.is_buyer()  == True,               "❌ buyer check failed"
assert user.is_admin()  == False,              "❌ admin check failed"
assert user.get_id()    == "1",                "❌ get_id failed"
assert user.is_verified == True,               "❌ verified check failed"
print("  ✅ User object: name, email, role, get_id all correct")

# Test buyer-only role
buyer_data = {**fake_user_data, "role": "buyer"}
buyer = User(buyer_data)
assert buyer.is_buyer()  == True
assert buyer.is_seller() == False
print("  ✅ Buyer-only role check passed")

# Test seller-only role
seller_data = {**fake_user_data, "role": "seller"}
seller = User(seller_data)
assert seller.is_seller() == True
assert seller.is_buyer()  == False
print("  ✅ Seller-only role check passed")

# Test admin role
admin_data = {**fake_user_data, "role": "admin"}
admin = User(admin_data)
assert admin.is_admin() == True
print("  ✅ Admin role check passed")

# ---------------------------------------------------------------
# TEST 3: Password hashing
# ---------------------------------------------------------------
print("\n[TEST 3] Password hashing...")
from werkzeug.security import generate_password_hash, check_password_hash

password    = "SecurePass123"
hashed      = generate_password_hash(password)
user_with_pw = User({**fake_user_data, "password_hash": hashed})

assert user_with_pw.check_password("SecurePass123") == True
assert user_with_pw.check_password("WrongPassword") == False
print("  ✅ Password hash & check working correctly")

# ---------------------------------------------------------------
# TEST 4: Order states validation
# ---------------------------------------------------------------
print("\n[TEST 4] Order states...")
valid_states = OrderModel.STATES
assert "Pending"    in valid_states, "❌ Pending missing"
assert "InProgress" in valid_states, "❌ InProgress missing"
assert "Delivered"  in valid_states, "❌ Delivered missing"
assert "Completed"  in valid_states, "❌ Completed missing"
assert "Cancelled"  in valid_states, "❌ Cancelled missing"
print(f"  ✅ All order states present: {valid_states}")

# ---------------------------------------------------------------
# TEST 5: Model methods exist (duck-type check)
# ---------------------------------------------------------------
print("\n[TEST 5] Checking all model methods exist...")

user_methods = ["get_by_id","get_by_email","create","update_profile",
                "update_role","verify_user","get_top_performers",
                "get_new_talent","get_rising_stars"]
for m in user_methods:
    assert hasattr(UserModel, m), f"❌ UserModel missing method: {m}"
print("  ✅ UserModel – all methods present")

gig_methods = ["get_by_id","get_by_seller","create","update",
               "search","get_featured","increment_views","deactivate"]
for m in gig_methods:
    assert hasattr(GigModel, m), f"❌ GigModel missing method: {m}"
print("  ✅ GigModel – all methods present")

order_methods = ["get_by_id","get_by_buyer","get_by_seller",
                 "create","update_status","set_delivery_link"]
for m in order_methods:
    assert hasattr(OrderModel, m), f"❌ OrderModel missing method: {m}"
print("  ✅ OrderModel – all methods present")

wallet_methods = ["get_balance","credit","debit","escrow","release_escrow"]
for m in wallet_methods:
    assert hasattr(WalletModel, m), f"❌ WalletModel missing method: {m}"
print("  ✅ WalletModel – all methods present")

msg_methods = ["get_by_order","send","mark_read",
               "unread_count","get_conversations"]
for m in msg_methods:
    assert hasattr(MessageModel, m), f"❌ MessageModel missing method: {m}"
print("  ✅ MessageModel – all methods present")

notif_methods = ["create","get_by_user","mark_read",
                 "mark_all_read","unread_count"]
for m in notif_methods:
    assert hasattr(NotificationModel, m), f"❌ NotificationModel missing: {m}"
print("  ✅ NotificationModel – all methods present")

project_methods = ["get_by_id","get_open","create","close","award"]
for m in project_methods:
    assert hasattr(ProjectModel, m), f"❌ ProjectModel missing: {m}"
print("  ✅ ProjectModel – all methods present")

bid_methods = ["get_by_id","get_by_project","place","accept","reject_others"]
for m in bid_methods:
    assert hasattr(BidModel, m), f"❌ BidModel missing: {m}"
print("  ✅ BidModel – all methods present")

review_methods = ["get_by_gig","get_by_seller","create","average_for_seller"]
for m in review_methods:
    assert hasattr(ReviewModel, m), f"❌ ReviewModel missing: {m}"
print("  ✅ ReviewModel – all methods present")

# ---------------------------------------------------------------
# TEST 6: User repr
# ---------------------------------------------------------------
print("\n[TEST 6] User __repr__...")
assert "ali@uni.edu" in repr(user), "❌ repr broken"
print(f"  ✅ repr: {repr(user)}")

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print()
print("=" * 55)
print("  ✅ ALL STEP 2 TESTS PASSED!")
print("  Models are correctly structured.")
print("  (DB tests will run after DB setup in later steps)")
print("=" * 55)
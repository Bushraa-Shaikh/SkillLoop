from app.utils.helpers import is_valid_email, is_student_email, validate_password

print("=" * 50)
print("   SKILLLOOP MANUAL TESTER")
print("=" * 50)

while True:
    print("\nWhat do you want to test?")
    print("1 - Email Validation")
    print("2 - Student Email Check")
    print("3 - Password Validation")
    print("4 - Test All Three Together")
    print("q - Quit")

    choice = input("\nEnter choice: ").strip()

    if choice == "q":
        print("Goodbye!")
        break

    elif choice == "1":
        email = input("Enter any email: ").strip()
        result = is_valid_email(email)
        if result:
            print(f"✅ '{email}' is a VALID email format")
        else:
            print(f"❌ '{email}' is an INVALID email format")

    elif choice == "2":
        email = input("Enter email to check if student: ").strip()
        result = is_student_email(email)
        if result:
            print(f"🎓 '{email}' IS a student email (.edu / .ac.uk etc.)")
        else:
            print(f"👤 '{email}' is NOT a student email")

    elif choice == "3":
        password = input("Enter a password to test: ").strip()
        ok, msg = validate_password(password)
        if ok:
            print(f"✅ Password is STRONG: {msg}")
        else:
            print(f"❌ Password is WEAK: {msg}")

    elif choice == "4":
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        print("\n--- Results ---")
        print(f"Valid email format : {is_valid_email(email)}")
        print(f"Student email      : {is_student_email(email)}")
        ok, msg = validate_password(password)
        print(f"Password strength  : {'✅ Strong' if ok else '❌ Weak'} — {msg}")

    else:
        print("Invalid choice, try again.")
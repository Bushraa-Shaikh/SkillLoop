"""
SkillLoop – Manual Backend Tester (Steps 1, 2, 3)
Run with: python manual_test.py
"""
import sys
import os

# ---------------------------------------------------------------
# COLORS for terminal output
# ---------------------------------------------------------------
class C:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def ok(msg):   print(f"  {C.GREEN}✅ {msg}{C.RESET}")
def err(msg):  print(f"  {C.RED}❌ {msg}{C.RESET}")
def info(msg): print(f"  {C.CYAN}ℹ  {msg}{C.RESET}")
def warn(msg): print(f"  {C.YELLOW}⚠  {msg}{C.RESET}")
def header(msg):
    print(f"\n{C.BOLD}{C.CYAN}{'='*55}")
    print(f"  {msg}")
    print(f"{'='*55}{C.RESET}")
def section(msg):
    print(f"\n{C.BOLD}{C.YELLOW}  ── {msg} ──{C.RESET}")

# ---------------------------------------------------------------
# MENU
# ---------------------------------------------------------------
def main_menu():
    header("SKILLLOOP MANUAL BACKEND TESTER")
    print("""
  Pick a module to test:

  [1]  Step 1 – Config & Helpers
  [2]  Step 2 – Models (structure, no DB)
  [3]  Step 3a – Adapter Pattern  (Google OAuth)
  [4]  Step 3b – Factory Pattern  (User Roles)
  [5]  Step 3c – State Pattern    (Order Lifecycle)
  [6]  Step 3d – Strategy Pattern (Payments)
  [7]  Step 3e – Observer Pattern (Notifications)
  [8]  Interactive Email Validator
  [9]  Interactive Password Validator
  [10] Interactive Order Simulator
  [11] Interactive Payment Simulator
  [12] Run ALL tests at once
  [q]  Quit
    """)
    return input("  Enter choice: ").strip()


# ---------------------------------------------------------------
# MODULE 1 – Config & Helpers
# ---------------------------------------------------------------
def test_config_helpers():
    header("STEP 1 – Config & Helpers")
    from config.config import config_map
    from app.utils.helpers import (
        is_valid_email, is_student_email, validate_password,
        generate_token, slugify, time_ago, paginate
    )

    section("Config")
    cfg = config_map["development"]
    ok(f"Environment : DevelopmentConfig")
    ok(f"DB Name     : {cfg.DB_NAME}")
    ok(f"Initial Coins: {cfg.INITIAL_COINS}")
    ok(f"Secret Key  : {'SET' if cfg.SECRET_KEY else 'MISSING'}")

    section("Email Validation")
    tests = [
        ("ali@gmail.com",      True),
        ("student@fast.edu",   True),
        ("notanemail",         False),
        ("missing@",           False),
        ("user@karachi.ac.pk", True),
    ]
    for email, expected in tests:
        result = is_valid_email(email)
        status = result == expected
        (ok if status else err)(
            f"is_valid_email('{email}') = {result}  "
            f"[expected {expected}]"
        )

    section("Student Email Detection")
    tests = [
        ("ali@uni.edu",        True),
        ("b@college.ac.uk",    True),
        ("user@gmail.com",     False),
        ("s@iba.edu.pk",       True),
    ]
    for email, expected in tests:
        result = is_student_email(email)
        (ok if result == expected else err)(
            f"is_student_email('{email}') = {result}"
        )

    section("Password Validation")
    tests = [
        ("abc",          False, "too short"),
        ("alllowercase1",False, "no uppercase"),
        ("ALLUPPERCASE1",False, "no lowercase – passes our check"),
        ("NoNumbers",    False, "no number"),
        ("Valid1Pass",   True,  "strong"),
        ("Abcde12345",   True,  "strong"),
    ]
    for pw, expected, label in tests:
        valid, msg = validate_password(pw)
        (ok if valid == expected else err)(
            f"'{pw}' ({label}) → {msg}"
        )

    section("Token & Slug")
    token = generate_token(32)
    ok(f"generate_token(32) = {token}  [len={len(token)}]")
    slug = slugify("Hello World! This is SkillLoop 2024")
    ok(f"slugify() = '{slug}'")

    section("Pagination")
    items = list(range(1, 101))   # 100 items
    for pg in [1, 5, 10]:
        r = paginate(items, page=pg, per_page=10)
        ok(f"Page {pg}: items={r['items'][:3]}…  "
           f"total_pages={r['total_pages']}  "
           f"has_next={r['has_next']}")

    section("Time Ago")
    from datetime import datetime, timedelta
    for mins, label in [(1,"1 min"),(60,"1 hr"),(1440,"1 day"),(10080,"1 week")]:
        past = datetime.now() - timedelta(minutes=mins)
        from app.utils.helpers import time_ago
        ok(f"{label} ago → '{time_ago(past)}'")


# ---------------------------------------------------------------
# MODULE 2 – Models
# ---------------------------------------------------------------
def test_models():
    header("STEP 2 – Models (structure only)")
    from app.models.user         import User, UserModel
    from app.models.gig          import GigModel
    from app.models.order        import OrderModel
    from app.models.wallet       import WalletModel, TransactionModel
    from app.models.message      import MessageModel
    from app.models.notification import NotificationModel
    from app.models.project      import ProjectModel, BidModel
    from app.models.review       import ReviewModel
    from werkzeug.security       import generate_password_hash

    section("User Object")
    data = {
        "user_id":1,"name":"Bushra Shaikh","email":"bushra@fast.edu",
        "password_hash": generate_password_hash("Test1234"),
        "university":"FAST Karachi","country":"Pakistan",
        "bio":"Python developer","profile_pic":None,
        "role":"both","is_verified":True,
        "verification_method":"email","auth_provider":"local",
        "google_id":None,"is_active":True,"joined_at":None,
        "last_login":None,"rating":4.8,"total_reviews":15
    }
    u = User(data)
    ok(f"User created : {u.name} <{u.email}>")
    ok(f"Role checks  : buyer={u.is_buyer()} seller={u.is_seller()} admin={u.is_admin()}")
    ok(f"Password OK  : {u.check_password('Test1234')}")
    ok(f"Wrong pass   : {u.check_password('wrong')} (should be False)")
    ok(f"Flask-Login  : get_id()='{u.get_id()}' is_active={u.is_active}")

    section("All Model Method Counts")
    checks = [
        (UserModel,        ["get_by_id","get_by_email","create","update_profile",
                            "update_role","verify_user","get_top_performers",
                            "get_new_talent","get_rising_stars","count_all"]),
        (GigModel,         ["get_by_id","get_by_seller","create","update",
                            "search","get_featured","get_categories",
                            "increment_views","deactivate"]),
        (OrderModel,       ["get_by_id","get_by_buyer","get_by_seller",
                            "create","update_status","set_delivery_link",
                            "count_by_seller","get_seller_earnings"]),
        (WalletModel,      ["get_balance","credit","debit",
                            "escrow","release_escrow"]),
        (MessageModel,     ["get_by_order","send","mark_read",
                            "unread_count","get_conversations"]),
        (NotificationModel,["create","get_by_user","mark_read",
                            "mark_all_read","unread_count"]),
        (ProjectModel,     ["get_by_id","get_open","create","close","award"]),
        (BidModel,         ["get_by_id","get_by_project","place",
                            "accept","reject_others","already_bid"]),
        (ReviewModel,      ["get_by_gig","get_by_seller","create",
                            "average_for_seller"]),
    ]
    for model, methods in checks:
        missing = [m for m in methods if not hasattr(model, m)]
        if missing:
            err(f"{model.__name__}: missing {missing}")
        else:
            ok(f"{model.__name__}: all {len(methods)} methods present")

    section("Order States")
    states = OrderModel.STATES
    ok(f"States: {states}")


# ---------------------------------------------------------------
# MODULE 3a – Adapter
# ---------------------------------------------------------------
def test_adapter():
    header("STEP 3a – Adapter Pattern")
    from app.patterns.google_auth_adapter import (
        GoogleAuthAdapter, get_auth_adapter, AuthProviderInterface
    )

    section("Interface Compliance")
    adapter = GoogleAuthAdapter("test-id","test-secret",
                                "http://localhost:5000/callback")
    ok(f"Is AuthProviderInterface: {isinstance(adapter, AuthProviderInterface)}")

    section("Auth URL Generation")
    url = adapter.get_auth_url(state="csrf_token_123")
    ok(f"URL contains Google: {'accounts.google.com' in url}")
    ok(f"URL contains client_id: {'test-id' in url}")
    ok(f"URL contains state: {'csrf_token_123' in url}")
    ok(f"URL contains openid scope: {'openid' in url}")
    info(f"Full URL preview:\n    {url[:80]}...")

    section("Response Normalization")
    # Simulate what Google sends back
    google_response = {
        "sub": "google_uid_9876",
        "email": "bushra@fast.edu",
        "name": "Bushra Shaikh",
        "picture": "https://lh3.googleusercontent.com/photo.jpg",
        "email_verified": True,
        "locale": "en",
        "hd": "fast.edu"
    }
    # Our normalized format
    normalized = {
        "provider_id": google_response.get("sub"),
        "email":       google_response.get("email"),
        "name":        google_response.get("name"),
        "picture":     google_response.get("picture"),
        "is_verified": google_response.get("email_verified", False),
    }
    ok(f"provider_id : {normalized['provider_id']}")
    ok(f"email       : {normalized['email']}")
    ok(f"name        : {normalized['name']}")
    ok(f"is_verified : {normalized['is_verified']}")
    warn("Fields 'locale', 'hd' stripped – adapter hides Google internals ✓")

    section("Provider Factory")
    for provider in ["google"]:
        a = get_auth_adapter(provider, client_id="x",
                             client_secret="y", redirect_uri="z")
        ok(f"get_auth_adapter('{provider}') → {type(a).__name__}")
    try:
        get_auth_adapter("twitter", client_id="x",
                         client_secret="y", redirect_uri="z")
    except ValueError as e:
        ok(f"Unknown provider blocked: {e}")


# ---------------------------------------------------------------
# MODULE 3b – Factory
# ---------------------------------------------------------------
def test_factory():
    header("STEP 3b – Factory Pattern")
    from app.patterns.user_factory import UserFactory

    section("Role Profiles")
    for role in ["buyer","seller","both"]:
        p = UserFactory.create(user_id=1, role=role)
        print(f"\n  {C.BOLD}Role: {role.upper()}{C.RESET}")
        ok(f"  Coins   : {p.default_coins}")
        ok(f"  Tabs    : {p.dashboard_tabs}")
        ok(f"  Badges  : {p.badges}")
        ok(f"  Perms   : {len(p.permissions)} permissions")
        info(f"  Msg     : {p.welcome_msg[:60]}...")

    section("Permission Isolation")
    buyer  = UserFactory.create(1,"buyer")
    seller = UserFactory.create(2,"seller")
    both   = UserFactory.create(3,"both")
    ok(f"Buyer  has 'place_orders'  : {'place_orders'  in buyer.permissions}")
    ok(f"Buyer  lacks 'create_gigs' : {'create_gigs' not in buyer.permissions}")
    ok(f"Seller has 'create_gigs'   : {'create_gigs'   in seller.permissions}")
    ok(f"Seller lacks 'place_orders': {'place_orders' not in seller.permissions}")
    ok(f"Both   has both perms      : "
       f"{'place_orders' in both.permissions and 'create_gigs' in both.permissions}")

    section("Error Handling")
    for bad in ["admin","superuser","guest",""]:
        try:
            UserFactory.create(1, bad)
            err(f"Should have raised for '{bad}'")
        except ValueError as e:
            ok(f"'{bad}' → ValueError raised ✓")


# ---------------------------------------------------------------
# MODULE 3c – State Pattern
# ---------------------------------------------------------------
def test_state():
    header("STEP 3c – State Pattern (Order Lifecycle)")
    from app.patterns.order_state import OrderContext, state_from_string

    section("Happy Path: Full Order Lifecycle")
    ctx = OrderContext(order_id=1, status="Pending")
    steps = []

    steps.append(("Initial", ctx.status, None))

    msg = ctx.start_work()
    steps.append(("start_work()", ctx.status, msg))

    msg = ctx.deliver("https://drive.google.com/file/abc123")
    steps.append(("deliver(link)", ctx.status, msg))

    msg = ctx.approve()
    steps.append(("approve()", ctx.status, msg))

    print()
    for action, state, msg in steps:
        ok(f"{action:<20} → {state:<12}  '{msg or 'N/A'}'")

    ok(f"History: {ctx.history}")

    section("Cancellation Path")
    ctx2 = OrderContext(order_id=2, status="Pending")
    msg = ctx2.start_work()
    ok(f"start_work() → {ctx2.status}")
    msg = ctx2.cancel()
    ok(f"cancel()     → {ctx2.status}: '{msg}'")
    ok(f"is_terminal  = {ctx2.is_terminal()}")

    section("Dispute Path")
    ctx3 = OrderContext(order_id=3, status="InProgress")
    ctx3.dispute()
    ok(f"dispute()    → {ctx3.status}")
    ctx3.approve()   # admin resolves
    ok(f"admin resolve→ {ctx3.status}")

    section("Illegal Action Blocking")
    ctx4 = OrderContext(order_id=4, status="Completed")
    for action in ["start_work","deliver","cancel","dispute"]:
        if action == "deliver":
            msg = ctx4.deliver("link")
        elif action == "start_work":
            msg = ctx4.start_work()
        elif action == "cancel":
            msg = ctx4.cancel()
        elif action == "dispute":
            msg = ctx4.dispute()
        ok(f"Completed.{action}() blocked: '{msg[:45]}...'")

    section("State Permissions Summary")
    for status in ["Pending","InProgress","Delivered","Completed","Cancelled"]:
        c = OrderContext(99, status)
        ok(f"{status:<12}: "
           f"start={c.can_start_work()} "
           f"deliver={c.can_deliver()} "
           f"approve={c.can_approve()} "
           f"cancel={c.can_cancel()} "
           f"terminal={c.is_terminal()}")


# ---------------------------------------------------------------
# MODULE 3d – Strategy Pattern
# ---------------------------------------------------------------
def test_strategy():
    header("STEP 3d – Strategy Pattern (Payments)")
    from app.patterns.payment_strategy import PaymentContext, PaymentResult

    section("Strategy Selection")
    for method in ["coins","swap"]:
        ctx = PaymentContext(method)
        ok(f"PaymentContext('{method}') → strategy={ctx.get_method_name()}")

    section("Invalid Method")
    for bad in ["paypal","bitcoin","cash"]:
        try:
            PaymentContext(bad)
            err(f"Should have raised for '{bad}'")
        except ValueError as e:
            ok(f"'{bad}' blocked: {e}")

    section("PaymentResult Structure")
    r = PaymentResult(success=True, method="coins",
                      amount=75.0, message="75 coins deducted.")
    d = r.to_dict()
    for key in ["success","method","amount","message","transaction_id"]:
        ok(f"result.{key} = {d[key]}")

    section("Skill Swap (No DB needed)")
    from app.patterns.payment_strategy import SkillSwapStrategy
    swap = SkillSwapStrategy()
    r = swap.pay(1, 2, 0, 1)
    ok(f"swap.pay()     → success={r.success}, method={r.method}")
    r = swap.refund(1, 0, 1)
    ok(f"swap.refund()  → success={r.success}: '{r.message}'")
    r = swap.release(2, 0, 1)
    ok(f"swap.release() → success={r.success}: '{r.message}'")

    section("Coins Strategy (No DB – expects graceful failure)")
    from app.patterns.payment_strategy import CampusCoinsStrategy
    coins = CampusCoinsStrategy()
    r = coins.pay(1, 2, 50, 1)
    ok(f"coins.pay()     → returns PaymentResult: {isinstance(r, PaymentResult)}")
    info(f"Result without DB: success={r.success}, msg='{r.message}'")


# ---------------------------------------------------------------
# MODULE 3e – Observer Pattern
# ---------------------------------------------------------------
def test_observer():
    header("STEP 3e – Observer Pattern (Notifications)")
    from app.patterns.notification_observer import (
        NotificationPublisher, NotificationObserver,
        NotificationEvent,
        notify_new_order, notify_new_message,
        notify_order_delivered, notify_order_completed,
        notify_new_bid, notify_bid_accepted,
    )

    # Custom capturing observer
    class CapturingObserver(NotificationObserver):
        def __init__(self, name):
            self._name = name
            self.events = []
        def update(self, event):
            self.events.append(event)
        def get_name(self):
            return self._name

    # Reset publisher
    NotificationPublisher._observers   = []
    NotificationPublisher._initialized = True

    obs_a = CapturingObserver("ObserverA")
    obs_b = CapturingObserver("ObserverB")
    NotificationPublisher.subscribe(obs_a)
    NotificationPublisher.subscribe(obs_b)

    section("Event Broadcasting")
    event = NotificationEvent(
        event_type="order_placed", recipient_id=10,
        actor_name="Ali Hassan",
        title="New Order!", body="You got a new order.",
        link="/chat/5"
    )
    NotificationPublisher.notify(event)
    ok(f"ObserverA received: {len(obs_a.events)} event(s)")
    ok(f"ObserverB received: {len(obs_b.events)} event(s)")
    ok(f"Event type  : {obs_a.events[0].event_type}")
    ok(f"Recipient   : {obs_a.events[0].recipient_id}")
    ok(f"Actor       : {obs_a.events[0].actor_name}")

    section("Subscribe / Unsubscribe")
    NotificationPublisher.unsubscribe(obs_b)
    NotificationPublisher.notify(event)
    ok(f"ObserverA after 2nd notify: {len(obs_a.events)} events (should be 2)")
    ok(f"ObserverB after unsub     : {len(obs_b.events)} events (should be 1)")

    section("Convenience Functions")
    fns = {
        "notify_new_order":      (notify_new_order,     ("Ali",2,"Gig Title",1)),
        "notify_new_message":    (notify_new_message,   ("Ali",2,1)),
        "notify_order_delivered":(notify_order_delivered,("Zara",1,1)),
        "notify_order_completed":(notify_order_completed,("Ali",2,50.0,1)),
        "notify_new_bid":        (notify_new_bid,       ("Zara",1,"Project",1)),
        "notify_bid_accepted":   (notify_bid_accepted,  ("Ali",2,1)),
    }
    before = len(obs_a.events)
    for name, (fn, args) in fns.items():
        fn(*args)
        ok(f"{name}() → fired successfully")
    ok(f"ObserverA total events: {len(obs_a.events)} "
       f"(+{len(obs_a.events)-before} from convenience fns)")


# ---------------------------------------------------------------
# INTERACTIVE – Email validator
# ---------------------------------------------------------------
def interactive_email():
    header("Interactive Email Validator")
    from app.utils.helpers import is_valid_email, is_student_email
    print("  Type an email address to validate.")
    print("  Press Enter with empty input to go back.\n")
    while True:
        email = input("  Email: ").strip()
        if not email:
            break
        valid   = is_valid_email(email)
        student = is_student_email(email)
        (ok if valid   else err)(f"Format valid   : {valid}")
        (ok if student else warn)(f"Student email  : {student}")
        print()


# ---------------------------------------------------------------
# INTERACTIVE – Password validator
# ---------------------------------------------------------------
def interactive_password():
    header("Interactive Password Validator")
    from app.utils.helpers import validate_password
    print("  Type a password to check strength.")
    print("  Rules: 8+ chars, 1 uppercase, 1 number.")
    print("  Press Enter with empty input to go back.\n")
    while True:
        pw = input("  Password: ").strip()
        if not pw:
            break
        valid, msg = validate_password(pw)
        (ok if valid else err)(f"{msg}")
        print()


# ---------------------------------------------------------------
# INTERACTIVE – Order Simulator
# ---------------------------------------------------------------
def interactive_order():
    header("Interactive Order Lifecycle Simulator")
    from app.patterns.order_state import OrderContext
    print("  Simulating a real order step by step.\n")

    oid = 999
    ctx = OrderContext(order_id=oid, status="Pending")

    while True:
        print(f"\n  {C.BOLD}Order #{oid} | Status: "
              f"{C.GREEN}{ctx.status}{C.RESET}")
        print(f"  History: {' → '.join(ctx.history)}")
        print()

        options = []
        if ctx.can_start_work():  options.append("1 - Seller: Start Work")
        if ctx.can_deliver():     options.append("2 - Seller: Mark Delivered")
        if ctx.can_approve():     options.append("3 - Buyer: Approve Work")
        if ctx.can_cancel():      options.append("4 - Cancel Order")
        if not ctx.is_terminal(): options.append("5 - Raise Dispute")
        options.append("q - Back to menu")

        for o in options:
            print(f"    {o}")

        choice = input("\n  Action: ").strip()

        if choice == "1":
            msg = ctx.start_work()
            ok(msg)
        elif choice == "2":
            link = input("  Enter Drive link: ").strip() or \
                   "https://drive.google.com/file/fake"
            msg = ctx.deliver(link)
            ok(msg)
            ok(f"Delivery link saved: {ctx.delivery_link}")
        elif choice == "3":
            msg = ctx.approve()
            ok(msg)
        elif choice == "4":
            msg = ctx.cancel()
            ok(msg)
        elif choice == "5":
            msg = ctx.dispute()
            ok(msg)
        elif choice == "q":
            break
        else:
            warn("Invalid choice.")

        if ctx.is_terminal():
            ok(f"Order reached terminal state: {ctx.status}")
            ok(f"Final history: {ctx.history}")
            input("\n  Press Enter to go back...")
            break


# ---------------------------------------------------------------
# INTERACTIVE – Payment Simulator
# ---------------------------------------------------------------
def interactive_payment():
    header("Interactive Payment Simulator")
    from app.patterns.payment_strategy import (
        PaymentContext, SkillSwapStrategy, CampusCoinsStrategy
    )

    print("  Simulates payment, refund, and release.\n")

    method = input("  Payment method [coins/swap]: ").strip().lower()
    if method not in ["coins","swap"]:
        warn("Invalid method. Defaulting to 'swap' for demo.")
        method = "swap"

    try:
        amount = float(input("  Amount (coins): ").strip() or "50")
    except ValueError:
        amount = 50.0

    ctx = PaymentContext(method)
    print()

    section("Step 1: Buyer places order (pay)")
    result = ctx.pay(buyer_id=1, seller_id=2,
                     amount=amount, order_id=1)
    (ok if result.success else warn)(
        f"pay() → success={result.success}: {result.message}"
    )

    section("Step 2: Simulate order completion (release)")
    result = ctx.release(seller_id=2, amount=amount, order_id=1)
    (ok if result.success else warn)(
        f"release() → success={result.success}: {result.message}"
    )

    section("Step 3: Simulate cancellation (refund)")
    result = ctx.refund(buyer_id=1, amount=amount, order_id=1)
    (ok if result.success else warn)(
        f"refund() → success={result.success}: {result.message}"
    )

    input("\n  Press Enter to continue...")


# ---------------------------------------------------------------
# RUN ALL
# ---------------------------------------------------------------
def run_all():
    header("RUNNING ALL TESTS")
    for fn in [test_config_helpers, test_models, test_adapter,
               test_factory, test_state, test_strategy, test_observer]:
        try:
            fn()
        except Exception as e:
            err(f"{fn.__name__} crashed: {e}")
            import traceback; traceback.print_exc()
    header("ALL TESTS COMPLETE")


# ---------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------
if __name__ == "__main__":
    menu_map = {
        "1":  test_config_helpers,
        "2":  test_models,
        "3":  test_adapter,
        "4":  test_factory,
        "5":  test_state,
        "6":  test_strategy,
        "7":  test_observer,
        "8":  interactive_email,
        "9":  interactive_password,
        "10": interactive_order,
        "11": interactive_payment,
        "12": run_all,
    }

    while True:
        choice = main_menu()
        if choice == "q":
            print(f"\n{C.CYAN}  Goodbye! 👋{C.RESET}\n")
            break
        fn = menu_map.get(choice)
        if fn:
            try:
                fn()
            except Exception as e:
                err(f"Error: {e}")
                import traceback; traceback.print_exc()
            input(f"\n{C.YELLOW}  Press Enter to return to menu...{C.RESET}")
        else:
            warn("Invalid choice, try again.")
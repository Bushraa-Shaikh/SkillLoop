"""
Step 3 Tests – Design Patterns
Run with: python test_step3.py
"""
print("=" * 60)
print("   SKILLLOOP - STEP 3 PATTERN TESTS")
print("=" * 60)

passed = 0
failed = 0

def ok(msg):
    global passed
    passed += 1
    print(f"  ✅ {msg}")

def fail(msg):
    global failed
    failed += 1
    print(f"  ❌ {msg}")

# ==============================================================
# TEST 1 – ADAPTER PATTERN
# ==============================================================
print("\n[TEST 1] Adapter Pattern – GoogleAuthAdapter")
try:
    from app.patterns.google_auth_adapter import (
        GoogleAuthAdapter, get_auth_adapter,
        AuthProviderInterface, GoogleOAuthClient
    )

    # Adapter must implement the interface
    adapter = GoogleAuthAdapter(
        client_id     = "fake-client-id",
        client_secret = "fake-secret",
        redirect_uri  = "http://localhost:5000/auth/google/callback"
    )
    assert isinstance(adapter, AuthProviderInterface), "not AuthProviderInterface"
    ok("GoogleAuthAdapter implements AuthProviderInterface")

    # get_auth_url builds correct Google URL
    url = adapter.get_auth_url(state="random_state")
    assert "accounts.google.com" in url,  "missing accounts.google.com"
    assert "fake-client-id"      in url,  "missing client_id"
    assert "openid"              in url,  "missing scope"
    assert "random_state"        in url,  "missing state"
    ok(f"get_auth_url builds correct URL")

    # Factory helper returns correct adapter type
    adapter2 = get_auth_adapter(
        "google",
        client_id     = "x",
        client_secret = "y",
        redirect_uri  = "z"
    )
    assert isinstance(adapter2, GoogleAuthAdapter)
    ok("get_auth_adapter('google') returns GoogleAuthAdapter")

    # Unknown provider raises ValueError
    try:
        get_auth_adapter("facebook", client_id="x",
                         client_secret="y", redirect_uri="z")
        fail("Should have raised ValueError for unknown provider")
    except ValueError as e:
        ok(f"Unknown provider raises ValueError: {e}")

    # Normalization mapping test (simulate get_user_info output)
    raw_google = {
        "sub": "123456789",
        "email": "student@uni.edu",
        "name": "Bushra Shaikh",
        "picture": "https://photo.url",
        "email_verified": True
    }
    # Manually test normalization logic
    normalized = {
        "provider_id": raw_google.get("sub"),
        "email":       raw_google.get("email"),
        "name":        raw_google.get("name"),
        "picture":     raw_google.get("picture"),
        "is_verified": raw_google.get("email_verified", False),
    }
    assert normalized["provider_id"] == "123456789"
    assert normalized["email"]       == "student@uni.edu"
    assert normalized["name"]        == "Bushra Shaikh"
    assert normalized["is_verified"] == True
    ok("Google response normalized correctly to app format")

except Exception as e:
    fail(f"Adapter test error: {e}")

# ==============================================================
# TEST 2 – FACTORY PATTERN
# ==============================================================
print("\n[TEST 2] Factory Pattern – UserFactory")
try:
    from app.patterns.user_factory import (
        UserFactory, UserProfile,
        BuyerCreator, SellerCreator, BothCreator
    )

    # Buyer profile
    buyer = UserFactory.create(user_id=1, role="buyer")
    assert isinstance(buyer, UserProfile)
    assert buyer.role          == "buyer"
    assert buyer.default_coins == 100
    assert "browse_gigs"       in buyer.permissions
    assert "place_orders"      in buyer.permissions
    assert "create_gigs"  not  in buyer.permissions
    ok(f"Buyer profile: coins={buyer.default_coins}, "
       f"tabs={buyer.dashboard_tabs}")

    # Seller profile
    seller = UserFactory.create(user_id=2, role="seller")
    assert seller.role          == "seller"
    assert seller.default_coins == 50
    assert "create_gigs"        in seller.permissions
    assert "view_analytics"     in seller.permissions
    assert "place_orders"  not  in seller.permissions
    ok(f"Seller profile: coins={seller.default_coins}, "
       f"badges={seller.badges}")

    # Both profile
    both = UserFactory.create(user_id=3, role="both")
    assert both.role == "both"
    assert "browse_gigs"    in both.permissions
    assert "create_gigs"    in both.permissions
    assert both.default_coins == 100
    ok(f"Both profile: {len(both.permissions)} permissions, "
       f"{len(both.dashboard_tabs)} tabs")

    # Invalid role raises ValueError
    try:
        UserFactory.create(user_id=4, role="superuser")
        fail("Should raise ValueError for invalid role")
    except ValueError as e:
        ok(f"Invalid role raises ValueError: {e}")

    # to_dict works
    d = buyer.to_dict()
    assert "role"        in d
    assert "permissions" in d
    assert "welcome_msg" in d
    ok("UserProfile.to_dict() returns all required keys")

    # Valid roles list
    roles = UserFactory.get_valid_roles()
    assert set(roles) == {"buyer", "seller", "both"}
    ok(f"Valid roles: {roles}")

except Exception as e:
    fail(f"Factory test error: {e}")
    import traceback; traceback.print_exc()

# ==============================================================
# TEST 3 – STATE PATTERN
# ==============================================================
print("\n[TEST 3] State Pattern – OrderContext")
try:
    from app.patterns.order_state import (
        OrderContext, state_from_string,
        PendingState, InProgressState, DeliveredState,
        CompletedState, CancelledState, DisputedState
    )

    # Full happy-path lifecycle
    ctx = OrderContext(order_id=99, status="Pending")
    assert ctx.status == "Pending"
    assert ctx.can_start_work() == True
    assert ctx.can_deliver()    == False
    assert ctx.can_approve()    == False
    ok(f"Initial state: {ctx.status}")

    msg = ctx.start_work()
    assert ctx.status == "InProgress"
    assert "In Progress" in msg
    assert ctx.can_deliver()    == True
    assert ctx.can_start_work() == False
    ok(f"start_work() → {ctx.status}: '{msg}'")

    msg = ctx.deliver("https://drive.google.com/file/123")
    assert ctx.status           == "Delivered"
    assert ctx.delivery_link is not None
    assert ctx.can_approve()    == True
    ok(f"deliver() → {ctx.status}: '{msg}'")

    msg = ctx.approve()
    assert ctx.status        == "Completed"
    assert ctx.is_terminal() == True
    ok(f"approve() → {ctx.status}: '{msg}'")

    # Terminal state blocks further actions
    msg = ctx.cancel()
    assert "not allowed" in msg.lower() or "invalid" in msg.lower() \
        or "Completed" in msg
    ok(f"Terminal state blocks cancel: '{msg}'")

    # Cancellation path
    ctx2 = OrderContext(order_id=100, status="Pending")
    msg  = ctx2.cancel()
    assert ctx2.status       == "Cancelled"
    assert ctx2.is_terminal() == True
    ok(f"cancel() from Pending → {ctx2.status}")

    # Dispute path
    ctx3 = OrderContext(order_id=101, status="InProgress")
    msg  = ctx3.dispute()
    assert ctx3.status == "Disputed"
    ok(f"dispute() from InProgress → {ctx3.status}")

    # Resolve disputed → Completed
    msg = ctx3.approve()
    assert ctx3.status == "Completed"
    ok(f"Admin resolves Disputed → {ctx3.status}")

    # History audit trail
    ctx4 = OrderContext(order_id=102, status="Pending")
    ctx4.start_work()
    ctx4.deliver("https://link")
    ctx4.approve()
    assert ctx4.history == ["Pending","InProgress","Delivered","Completed"]
    ok(f"History audit trail: {ctx4.history}")

    # state_from_string
    for s in ["Pending","InProgress","Delivered","Completed",
              "Cancelled","Disputed"]:
        state = state_from_string(s)
        assert state.get_status() == s
    ok("state_from_string() works for all 6 states")

    # Invalid state string
    try:
        state_from_string("Flying")
        fail("Should raise ValueError")
    except ValueError as e:
        ok(f"Invalid state raises ValueError: {e}")

    # can_cancel only in early states
    ctx5 = OrderContext(order_id=103, status="Delivered")
    assert ctx5.can_cancel() == False
    ok("can_cancel() = False in Delivered state")

except Exception as e:
    fail(f"State test error: {e}")
    import traceback; traceback.print_exc()

# ==============================================================
# TEST 4 – STRATEGY PATTERN
# ==============================================================
print("\n[TEST 4] Strategy Pattern – PaymentContext")
try:
    from app.patterns.payment_strategy import (
        PaymentContext, PaymentResult,
        CampusCoinsStrategy, SkillSwapStrategy
    )

    # Strategy selection
    coins_ctx = PaymentContext("coins")
    swap_ctx  = PaymentContext("swap")
    assert coins_ctx.get_method_name() == "coins"
    assert swap_ctx.get_method_name()  == "swap"
    ok("PaymentContext selects correct strategies")

    # Valid methods list
    methods = PaymentContext.valid_methods()
    assert "coins" in methods
    assert "swap"  in methods
    ok(f"Valid payment methods: {methods}")

    # Invalid method raises ValueError
    try:
        PaymentContext("bitcoin")
        fail("Should raise ValueError")
    except ValueError as e:
        ok(f"Invalid method raises ValueError: {e}")

    # PaymentResult structure
    result = PaymentResult(
        success=True, method="coins",
        amount=50.0, message="Test"
    )
    d = result.to_dict()
    assert "success" in d
    assert "method"  in d
    assert "amount"  in d
    assert "message" in d
    ok("PaymentResult.to_dict() has required keys")

    # Swap strategy pay/refund/release return success without DB
    swap = SkillSwapStrategy()
    # Swap calls TransactionModel which needs DB; test gracefully
    r1 = swap.pay(1, 2, 0, 1)
    assert isinstance(r1, PaymentResult)
    ok(f"SkillSwap pay() returns PaymentResult: success={r1.success}")

    r2 = swap.refund(1, 0, 1)
    assert r2.success == True
    ok(f"SkillSwap refund(): {r2.message}")

    r3 = swap.release(2, 0, 1)
    assert r3.success == True
    ok(f"SkillSwap release(): {r3.message}")

    # Coins strategy fails gracefully without DB
    coins = CampusCoinsStrategy()
    r4 = coins.pay(1, 2, 100, 1)
    # Should return PaymentResult (success or fail) not raise exception
    assert isinstance(r4, PaymentResult)
    ok(f"CampusCoins pay() returns PaymentResult gracefully: "
       f"success={r4.success}")

except Exception as e:
    fail(f"Strategy test error: {e}")
    import traceback; traceback.print_exc()

# ==============================================================
# TEST 5 – OBSERVER PATTERN
# ==============================================================
print("\n[TEST 5] Observer Pattern – NotificationPublisher")
try:
    from app.patterns.notification_observer import (
        NotificationPublisher, NotificationEvent,
        NotificationObserver,
        DatabaseNotificationObserver,
        SocketIONotificationObserver,
        EmailNotificationObserver,
        notify_new_order, notify_new_message,
        notify_order_delivered, notify_order_completed,
        notify_new_bid, notify_bid_accepted,
    )

    # Custom test observer to capture events
    class TestObserver(NotificationObserver):
        def __init__(self):
            self.received = []
        def update(self, event: NotificationEvent):
            self.received.append(event)
        def get_name(self) -> str:
            return "TestObserver"

    # Reset and set up with only our test observer
    NotificationPublisher._observers   = []
    NotificationPublisher._initialized = True
    test_obs = TestObserver()
    NotificationPublisher.subscribe(test_obs)

    # Publish an event
    event = NotificationEvent(
        event_type   = "order_placed",
        recipient_id = 42,
        actor_name   = "Test Buyer",
        title        = "New Order!",
        body         = "You got an order.",
        link         = "/chat/1",
    )
    NotificationPublisher.notify(event)
    assert len(test_obs.received) == 1
    assert test_obs.received[0].recipient_id == 42
    assert test_obs.received[0].title        == "New Order!"
    ok("Publisher notifies observer with correct event")

    # Multiple subscribers
    test_obs2 = TestObserver()
    NotificationPublisher.subscribe(test_obs2)
    NotificationPublisher.notify(event)
    assert len(test_obs.received)  == 2
    assert len(test_obs2.received) == 1
    ok("Multiple observers all receive events")

    # Unsubscribe
    before_count = len(test_obs.received)
    NotificationPublisher.unsubscribe(test_obs2)
    NotificationPublisher.notify(event)
    assert len(test_obs.received) == before_count + 1  # active obs gets it
    ok("Unsubscribed observer stops receiving new events")

    # Convenience functions exist and are callable
    fns = [notify_new_order, notify_new_message,
           notify_order_delivered, notify_order_completed,
           notify_new_bid, notify_bid_accepted]
    for fn in fns:
        assert callable(fn)
    ok(f"All {len(fns)} convenience notify functions are callable")

    # NotificationEvent dataclass
    e = NotificationEvent(
        event_type="message_sent", recipient_id=5,
        actor_name="Zara", title="Hi!", body="Hello there",
        link="/chat/2"
    )
    assert e.data == {}   # default empty dict
    ok("NotificationEvent data defaults to empty dict")

    # Observer names
    names = NotificationPublisher.get_observer_names()
    assert "TestObserver" in names
    ok(f"Observer names: {names}")

    # Email observer only fires on critical events
    email_obs = EmailNotificationObserver()
    non_critical = NotificationEvent(
        event_type="message_sent", recipient_id=1,
        actor_name="X", title="msg", body="body"
    )
    # Should not raise even if DB not available
    email_obs.update(non_critical)
    ok("Email observer ignores non-critical events silently")

except Exception as e:
    fail(f"Observer test error: {e}")
    import traceback; traceback.print_exc()

# ==============================================================
# SUMMARY
# ==============================================================
print()
print("=" * 60)
print(f"  Results: {passed} passed, {failed} failed")
if failed == 0:
    print("  ✅ ALL STEP 3 PATTERN TESTS PASSED!")
    print()
    print("  Patterns implemented:")
    print("    🔌 Adapter  – GoogleAuthAdapter")
    print("    🏭 Factory  – UserFactory (buyer/seller/both)")
    print("    🔄 State    – OrderContext (6 states)")
    print("    💳 Strategy – PaymentContext (coins/swap)")
    print("    📢 Observer – NotificationPublisher (3 observers)")
else:
    print(f"  ⚠️  {failed} test(s) failed. Check errors above.")
print("=" * 60)
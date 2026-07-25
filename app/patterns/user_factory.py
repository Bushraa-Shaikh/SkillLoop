"""
FACTORY DESIGN PATTERN
======================
Problem : Creating a user with role 'buyer', 'seller', or 'both'
          involves different setup logic (wallet credits, badges,
          default permissions, welcome notifications, etc.)
Solution: UserFactory decides which concrete creator to use
          based on the requested role.

Product          : UserProfile (the thing being created)
Creator          : UserCreator (abstract)
Concrete Creators: BuyerCreator, SellerCreator, BothCreator
Factory          : UserFactory.create()
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------
# PRODUCT  – the result returned by every factory
# ---------------------------------------------------------------
@dataclass
class UserProfile:
    """
    Represents the fully configured profile created by the factory.
    Contains everything needed to finish onboarding a new user.
    """
    user_id:       int
    role:          str
    permissions:   List[str]     = field(default_factory=list)
    default_coins: int           = 0
    welcome_msg:   str           = ""
    badges:        List[str]     = field(default_factory=list)
    dashboard_tabs: List[str]    = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "user_id":       self.user_id,
            "role":          self.role,
            "permissions":   self.permissions,
            "default_coins": self.default_coins,
            "welcome_msg":   self.welcome_msg,
            "badges":        self.badges,
            "dashboard_tabs":self.dashboard_tabs,
        }


# ---------------------------------------------------------------
# ABSTRACT CREATOR
# ---------------------------------------------------------------
class UserCreator(ABC):
    """
    Declares the factory method that subclasses must implement.
    Also contains shared setup logic.
    """

    @abstractmethod
    def create_profile(self, user_id: int) -> UserProfile:
        pass

    def _base_permissions(self) -> List[str]:
        """Permissions every user gets regardless of role."""
        return [
            "view_profile",
            "send_messages",
            "manage_wallet",
            "view_notifications",
        ]


# ---------------------------------------------------------------
# CONCRETE CREATORS
# ---------------------------------------------------------------
class BuyerCreator(UserCreator):
    """Creates a Buyer profile with browse & order permissions."""

    def create_profile(self, user_id: int) -> UserProfile:
        perms = self._base_permissions() + [
            "browse_gigs",
            "place_orders",
            "post_projects",
            "leave_reviews",
            "accept_bids",
        ]
        return UserProfile(
            user_id        = user_id,
            role           = "buyer",
            permissions    = perms,
            default_coins  = 100,
            welcome_msg    = (
                "Welcome! You have 100 Campus Coins to get started. "
                "Browse gigs and find the perfect match for your project."
            ),
            badges         = ["New Buyer"],
            dashboard_tabs = ["Browse Gigs", "My Orders",
                              "Post Project", "Wallet", "Messages"],
        )


class SellerCreator(UserCreator):
    """Creates a Seller profile with gig management permissions."""

    def create_profile(self, user_id: int) -> UserProfile:
        perms = self._base_permissions() + [
            "create_gigs",
            "manage_gigs",
            "receive_orders",
            "place_bids",
            "deliver_work",
            "view_analytics",
        ]
        return UserProfile(
            user_id        = user_id,
            role           = "seller",
            permissions    = perms,
            default_coins  = 50,
            welcome_msg    = (
                "Welcome! Create your first gig and start earning "
                "Campus Coins. Showcase your skills to buyers worldwide."
            ),
            badges         = ["New Talent"],
            dashboard_tabs = ["My Gigs", "Create Gig", "Orders",
                              "Analytics", "Wallet", "Messages"],
        )


class BothCreator(UserCreator):
    """Creates a dual Buyer+Seller profile with all permissions."""

    def create_profile(self, user_id: int) -> UserProfile:
        # Merge all permissions from buyer and seller
        buyer_perms  = BuyerCreator()._base_permissions() + [
            "browse_gigs", "place_orders", "post_projects",
            "leave_reviews", "accept_bids",
        ]
        seller_perms = [
            "create_gigs", "manage_gigs", "receive_orders",
            "place_bids", "deliver_work", "view_analytics",
        ]
        all_perms = list(set(buyer_perms + seller_perms))

        return UserProfile(
            user_id        = user_id,
            role           = "both",
            permissions    = all_perms,
            default_coins  = 100,
            welcome_msg    = (
                "Welcome! You can both buy and sell on SkillLoop. "
                "You have 100 Campus Coins ready to use."
            ),
            badges         = ["New Talent", "New Buyer"],
            dashboard_tabs = ["Browse Gigs", "My Gigs", "Create Gig",
                              "Orders", "Post Project", "Analytics",
                              "Wallet", "Messages"],
        )


# ---------------------------------------------------------------
# FACTORY  – the single public entry point
# ---------------------------------------------------------------
class UserFactory:
    """
    Static factory that picks the correct creator based on role
    and returns a fully configured UserProfile.

    Usage:
        profile = UserFactory.create(user_id=5, role='seller')
    """

    _creators = {
        "buyer":  BuyerCreator,
        "seller": SellerCreator,
        "both":   BothCreator,
    }

    @staticmethod
    def create(user_id: int, role: str) -> UserProfile:
        role = role.lower().strip()
        creator_cls = UserFactory._creators.get(role)
        if not creator_cls:
            raise ValueError(
                f"Unknown role '{role}'. "
                f"Valid roles: {list(UserFactory._creators.keys())}"
            )
        creator = creator_cls()
        return creator.create_profile(user_id)

    @staticmethod
    def get_valid_roles() -> List[str]:
        return list(UserFactory._creators.keys())

    @staticmethod
    def apply_to_db(user_id: int, profile: UserProfile):
        """
        Persist the factory-generated profile to the database.
        Called after UserFactory.create().
        """
        from app.models.user   import UserModel
        from app.models.wallet import WalletModel
        from app.models.notification import NotificationModel

        # 1. Update user role
        UserModel.update_role(user_id, profile.role)

        # 2. Credit initial coins
        if profile.default_coins > 0:
            WalletModel.credit(
                user_id, profile.default_coins,
                "Welcome bonus coins"
            )

        # 3. Send welcome notification
        NotificationModel.create(
            user_id   = user_id,
            notif_type = "system",
            title     = "Welcome to SkillLoop! 🎉",
            body      = profile.welcome_msg,
            link      = "/dashboard"
        )
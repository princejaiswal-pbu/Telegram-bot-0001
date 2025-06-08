"""
Inline keyboard utilities
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import EMOJIS

def get_main_menu() -> InlineKeyboardMarkup:
    """Get the main menu keyboard with cyberpunk styling"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['deal']} Create Deal",
                callback_data="create_deal"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['status']} My Deals",
                callback_data="my_deals"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['money']} Payment Status",
                callback_data="payment_status"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['dispute']} Support",
                callback_data="support"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lightning']} How It Works",
                callback_data="how_it_works"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['shield']} Security",
                callback_data="security_info"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_onboarding_keyboard() -> InlineKeyboardMarkup:
    """Get onboarding keyboard"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['rocket']} Get Started",
                callback_data="start_onboarding"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Get confirmation keyboard for deal creation"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['success']} Create Deal",
                callback_data="confirm_deal"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['error']} Cancel",
                callback_data="cancel_deal_creation"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_deal_keyboard(deal_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for a specific deal"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['money']} Pay Now",
                callback_data=f"pay_deal_{deal_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['status']} View Details",
                callback_data=f"deal_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lock']} Share Deal",
                callback_data=f"share_deal_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lightning']} Back to Menu",
                callback_data="main_menu"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_deal_management_keyboard(deal_id: str, status: str) -> InlineKeyboardMarkup:
    """Get management keyboard based on deal status"""
    
    keyboard = []
    
    if status == 'created':
        keyboard.append([
            InlineKeyboardButton(
                text=f"{EMOJIS['money']} Pay Now",
                callback_data=f"pay_deal_{deal_id}"
            )
        ])
    
    elif status == 'funded':
        keyboard.extend([
            [
                InlineKeyboardButton(
                    text=f"{EMOJIS['send']} Release Payment",
                    callback_data=f"release_payment_{deal_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJIS['dispute']} Create Dispute",
                    callback_data=f"dispute_deal_{deal_id}"
                )
            ]
        ])
    
    elif status == 'disputed':
        keyboard.append([
            InlineKeyboardButton(
                text=f"{EMOJIS['admin']} Contact Admin",
                url="https://t.me/darx_zerox"
            )
        ])
    
    # Common buttons
    keyboard.extend([
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lock']} Share Deal",
                callback_data=f"share_deal_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lightning']} Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_payment_keyboard(deal_id: str) -> InlineKeyboardMarkup:
    """Get payment confirmation keyboard"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['success']} Payment Done",
                callback_data=f"payment_done_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['qr']} Generate New QR",
                callback_data=f"regenerate_qr_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lightning']} Back to Deal",
                callback_data=f"deal_{deal_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['deal']} All Deals",
                callback_data="admin_all_deals"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['warning']} Disputes",
                callback_data="admin_disputes"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['rocket']} Broadcast",
                callback_data="admin_broadcast"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['diamond']} Statistics",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['shield']} Security Log",
                callback_data="admin_security"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['key']} System Status",
                callback_data="admin_system"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_deal_keyboard(deal_id: str, status: str) -> InlineKeyboardMarkup:
    """Get admin actions keyboard for a specific deal"""
    
    keyboard = []
    
    if status == 'disputed':
        keyboard.append([
            InlineKeyboardButton(
                text=f"{EMOJIS['success']} Resolve (Release)",
                callback_data=f"admin_resolve_{deal_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJIS['error']} Cancel Deal",
                callback_data=f"admin_cancel_{deal_id}"
            )
        ])
    
    elif status in ['created', 'funded']:
        keyboard.extend([
            [
                InlineKeyboardButton(
                    text=f"{EMOJIS['send']} Force Release",
                    callback_data=f"admin_resolve_{deal_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJIS['error']} Cancel Deal",
                    callback_data=f"admin_cancel_{deal_id}"
                )
            ]
        ])
    
    # Common admin buttons
    keyboard.extend([
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['lock']} View Details",
                callback_data=f"admin_deal_details_{deal_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJIS['shield']} Back to Admin",
                callback_data="back_to_admin"
            )
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

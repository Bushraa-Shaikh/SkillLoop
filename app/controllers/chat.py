"""
Chat Controller – real-time messaging per order
Routes: /chat/<order_id>   GET = load chat
        /messages           GET = all conversations
SocketIO events: join_room, send_message
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort, jsonify)
from flask_login import login_required, current_user
try:
    from app import socketio
    from flask_socketio import join_room, leave_room, emit
except Exception:
    socketio = None
    join_room = leave_room = emit = None

from app.models.order   import OrderModel
from app.models.message import MessageModel
from app.patterns.notification_observer import notify_new_message

chat_bp = Blueprint("chat", __name__)


# ---------------------------------------------------------------
# CHAT ROOM  /chat/<order_id>
# ---------------------------------------------------------------
@chat_bp.route("/chat/<int:order_id>")
@login_required
def chat_room(order_id):
    order = OrderModel.get_by_id(order_id)
    if not order:
        abort(404)

    uid = current_user.user_id
    if order["buyer_id"] != uid and order["seller_id"] != uid:
        abort(403)

    messages = MessageModel.get_by_order(order_id)
    MessageModel.mark_read(order_id, uid)

    is_seller = order["seller_id"] == uid

    return render_template(
        "chat/chat.html",
        order     = order,
        messages  = messages,
        is_seller = is_seller,
    )


# ---------------------------------------------------------------
# MESSAGES INBOX  /messages
# ---------------------------------------------------------------
@chat_bp.route("/messages")
@login_required
def messages():
    convos = MessageModel.get_conversations(current_user.user_id)
    return render_template("chat/messages.html", conversations=convos)


# ---------------------------------------------------------------
# SEND MESSAGE (AJAX)  /chat/<order_id>/send
# ---------------------------------------------------------------
@chat_bp.route("/chat/<int:order_id>/send", methods=["POST"])
@login_required
def send_message(order_id):
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    uid = current_user.user_id
    if order["buyer_id"] != uid and order["seller_id"] != uid:
        return jsonify({"error": "Forbidden"}), 403

    body       = request.form.get("body","").strip()
    drive_link = request.form.get("drive_link","").strip() or None

    if not body and not drive_link:
        return jsonify({"error": "Message cannot be empty"}), 400

    msg_id = MessageModel.send(order_id, uid, body, drive_link)

    # Notify the other party
    other_id = (order["seller_id"]
                if uid == order["buyer_id"]
                else order["buyer_id"])
    notify_new_message(current_user.name, other_id, order_id)

    return jsonify({
        "success": True,
        "message_id": msg_id,
        "sender_name": current_user.name,
        "body": body,
        "drive_link": drive_link,
    })


# ---------------------------------------------------------------
# SocketIO – join room
# ---------------------------------------------------------------
def register_socketio_events():
    """Called from app factory after socketio is confirmed available."""
    from app import socketio as sio
    if not sio:
        return

    @sio.on("join_room")
    def handle_join(data):
        order_id = data.get("order_id")
        if order_id:
            room = f"order_{order_id}"
            join_room(room)
            emit("status",
                 {"msg": f"Joined chat room {order_id}"},
                 room=room)

    @sio.on("send_message")
    def handle_message(data):
        from flask_login import current_user
        order_id   = data.get("order_id")
        body       = data.get("body", "").strip()
        drive_link = data.get("drive_link", "").strip() or None

        if not order_id or (not body and not drive_link):
            return

        order = OrderModel.get_by_id(order_id)
        if not order:
            return

        uid = current_user.user_id
        if order["buyer_id"] != uid and order["seller_id"] != uid:
            return

        msg_id = MessageModel.send(order_id, uid, body, drive_link)

        room = f"order_{order_id}"
        emit("new_message", {
            "message_id":  msg_id,
            "sender_id":   uid,
            "sender_name": current_user.name,
            "body":        body,
            "drive_link":  drive_link,
        }, room=room)

        other_id = (order["seller_id"]
                    if uid == order["buyer_id"]
                    else order["buyer_id"])
        notify_new_message(current_user.name, other_id, order_id)

    @sio.on("join_user_room")
    def handle_join_user(data):
        user_id = data.get("user_id")
        if user_id:
            join_room(f"user_{user_id}")
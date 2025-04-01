import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from base.strConst import HTML_TEMPLATE_NEW_USER_ALERT, HTML_TEMPLATE_NEW_ORDER_ALERT


# pre_save is triggered before a model's save() method is called
# Listen for the pre_save signal for the User model
@receiver(pre_save, sender=User)
def updateUsername(sender, instance, **kwargs):
    # The instance represents the User object being saved
    user = instance

    # If the user's email field is not empty, update the username to match the email
    if user.email != '':
        user.username = user.email
        # Print a message for debugging or logging purposes
        # print(user, 'updated!')


@receiver(post_save, sender=User)
def newUserAlert(sender, instance, created, **kwargs):
    user = instance
    if created:
        html_content = HTML_TEMPLATE_NEW_USER_ALERT(user)
        try:
            send_mail(
                "E-SHOP | NEW USER",
                "",
                settings.EMAIL_HOST_USER,
                ["abolfazl.hassanzade.81@gmail.com"],
                html_message=html_content,
            )
        except Exception as e:
            logging.error(f"Error sending email: {e}")


order_created = Signal()


@receiver(order_created)
def newOrderAlert(sender, **kwargs):
    order = kwargs.get("order")
    user = kwargs.get("user")
    orderItems = order.orderitem_set.all()
    itemsPrice = sum(item.qty * item.price for item in orderItems)

    html_content = HTML_TEMPLATE_NEW_ORDER_ALERT(
        user, order, orderItems, itemsPrice)

    try:
        send_mail(
            "E-SHOP | NEW ORDER",
            "",
            settings.EMAIL_HOST_USER,
            ["abolfazl.hassanzade.81@gmail.com"],
            html_message=html_content,
        )
    except Exception as e:
        logging.error(f"Error sending email: {e}")



from menu import Menu, MenuItem
from django.urls import reverse
from . import views as baseball_vw

# add items to the menu
Menu.add_item("main", MenuItem("Run Jobs",
                               reverse(baseball_vw.run_jobs_view),
                               weight=10))
Menu.add_item("main", MenuItem("View Stats",
                               url="/",
                               # reverse(""),
                               weight=10))
Menu.add_item("main", MenuItem("Home",
                               url="/",
                               # reverse(""),
                               weight=10))

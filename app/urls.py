from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addUserEntry", views.addUserEntry, name='addUserEntry'),
    path("getUserEntry", views.getUserEntry, name='getUserEntry'),
    path("removeUserEntry", views.removeUserEntry, name='removeUserEntry'),
    path("removeAllEntry", views.removeAllEntry, name='removeAllEntry'),
    path("validateUserEntry", views.validateUserEntry, name='validateUserEntry'),
    path("addRecord", views.addRecord, name='addRecord'),
    path("removeOutDateRecord", views.removeOutDateRecord, name='removeOutDateRecord'),
    path("showAll", views.showAll, name='showAll'),
    path("addAdmin", views.addAdmin, name='addAdmin'),
    path("removeAdmin", views.removeAdmin, name='removeAdmin'),
    path("isReady", views.isReady, name='isReady'),
]
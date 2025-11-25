from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    VATMasterViewSet,
    SupplierMasterViewSet,
    GroupMasterViewSet,
    BrandMasterViewSet,
    ITGRP_MAPViewSet,
    UnitMasterViewSet,
    ItemMasterViewSet,
    UnitMapViewSet
)


router = DefaultRouter()
router.register("vat", VATMasterViewSet, basename="vat")
router.register("supplier", SupplierMasterViewSet, basename="supplier")
router.register("group-master", GroupMasterViewSet, basename="group-master")
router.register("brand-master", BrandMasterViewSet, basename="brand-master")
router.register("itgrp-map", ITGRP_MAPViewSet, basename="itgrp-map")
router.register("unit-master", UnitMasterViewSet, basename="unit-master")
router.register("itemmaster", ItemMasterViewSet, basename="itemmaster")
router.register("unit-map", UnitMapViewSet, basename="unit-map")


urlpatterns = [
    path("", include(router.urls)),
]
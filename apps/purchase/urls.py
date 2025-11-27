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
    UnitMapViewSet,
    VRTypeMasterViewSet,
    INVTRANViewSet,
    ACC_TRANViewSet,
    ACCTMASTViewSet,
    ACCT_MAST_MAPViewSet,
    ACC_TRAN_DETAViewSet,
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
router.register("vr-type", VRTypeMasterViewSet, basename="vr-type")
router.register("inv-tran", INVTRANViewSet, basename="inv-tran")
router.register("acc-tran", ACC_TRANViewSet, basename="acc-tran")
router.register("acct-mast", ACCTMASTViewSet, basename="acct-mast")
router.register("acct-mast-map", ACCT_MAST_MAPViewSet, basename="acct-mast-map")
router.register("acc-tran-deta", ACC_TRAN_DETAViewSet, basename="acc-tran-deta")


urlpatterns = [
    path("", include(router.urls)),
]
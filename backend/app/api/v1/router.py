from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.drivers_auth import router as drivers_auth_router
from app.api.v1.routes.booking import router as booking_router
from app.api.v1.routes.emergency_contacts import router as emergency_contacts_router
from app.api.v1.routes.home import router as home_router
from app.api.v1.routes.driver_dashboard import router as driver_dashboard_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.driver_menu import router as driver_menu_router
from app.api.v1.routes.driver_matching import router as driver_matching_router
from app.api.v1.routes.passenger_profile import router as passenger_profile_router
from app.api.v1.routes.realtime import router as realtime_router
from app.api.v1.routes.maps import router as maps_router
from app.api.v1.routes.outstation import router as outstation_router
from app.api.v1.routes.notifications import router as notifications_router
from app.api.v1.routes.documents import router as documents_router
from app.api.v1.routes.drivers_documents import router as drivers_documents_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(drivers_auth_router)
api_router.include_router(drivers_documents_router)
api_router.include_router(documents_router)
api_router.include_router(driver_dashboard_router)
api_router.include_router(admin_router)
api_router.include_router(driver_menu_router)
api_router.include_router(driver_matching_router)
api_router.include_router(passenger_profile_router)
api_router.include_router(home_router)
api_router.include_router(booking_router)
api_router.include_router(emergency_contacts_router)
api_router.include_router(realtime_router)
api_router.include_router(maps_router)
api_router.include_router(outstation_router)
api_router.include_router(notifications_router)

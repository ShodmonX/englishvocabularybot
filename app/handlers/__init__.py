from .start import router as start_router
from .word import router as word_router
from .admin import router as admin_router

routers = [admin_router, start_router, word_router]
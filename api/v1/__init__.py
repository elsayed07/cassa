from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth

api = NinjaAPI(
    title="Cassa API",
    version="1.0.0",
    description="Cassa ecommerce REST API",
    auth=JWTAuth(),
    urls_namespace="api-v1",
)

# Token endpoints (public, no auth required)
from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router

api.add_router("/token", obtain_pair_router, tags=["Auth"])
api.add_router("/token", verify_router, tags=["Auth"])

# Domain routers
from api.v1.catalog import router as catalog_router
from api.v1.carts import router as carts_router
from api.v1.orders import router as orders_router
from api.v1.accounts import router as accounts_router

api.add_router("/catalog/", catalog_router, tags=["Catalog"])
api.add_router("/cart/", carts_router, tags=["Cart"])
api.add_router("/orders/", orders_router, tags=["Orders"])
api.add_router("/accounts/", accounts_router, tags=["Accounts"])
